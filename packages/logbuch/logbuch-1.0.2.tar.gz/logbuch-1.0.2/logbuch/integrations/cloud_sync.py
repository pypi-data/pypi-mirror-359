#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/integrations/cloud_sync.py

import json
import hashlib
import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
import asyncio

from logbuch.core.logger import get_logger
from logbuch.core.config import get_config
from logbuch.core.exceptions import LogbuchError
from logbuch.core.security import get_security_manager


class CloudProvider(Enum):
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"
    ONEDRIVE = "onedrive"
    CUSTOM_S3 = "custom_s3"
    GITHUB_GIST = "github_gist"


@dataclass
class SyncStatus:
    provider: CloudProvider
    last_sync: Optional[datetime.datetime]
    status: str  # 'synced', 'pending', 'error', 'conflict'
    local_hash: Optional[str]
    remote_hash: Optional[str]
    error_message: Optional[str] = None


@dataclass
class CloudFile:
    name: str
    path: str
    size: int
    modified: datetime.datetime
    hash: str
    provider: CloudProvider


class CloudSyncError(LogbuchError):
    pass


class CloudSyncManager:
    def __init__(self):
        self.logger = get_logger("cloud_sync")
        self.security = get_security_manager()
        self.config = get_config()
        
        self.providers = {}
        self.sync_status = {}
        
        # Initialize available providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        # Google Drive
        try:
            from .providers.google_drive import GoogleDriveProvider
            self.providers[CloudProvider.GOOGLE_DRIVE] = GoogleDriveProvider()
        except ImportError:
            self.logger.debug("Google Drive provider not available")
        
        # Dropbox
        try:
            from .providers.dropbox import DropboxProvider
            self.providers[CloudProvider.DROPBOX] = DropboxProvider()
        except ImportError:
            self.logger.debug("Dropbox provider not available")
        
        # GitHub Gist (already implemented)
        try:
            from .github_gists import GitHubGistManager
            self.providers[CloudProvider.GITHUB_GIST] = GitHubGistManager()
        except ImportError:
            self.logger.debug("GitHub Gist provider not available")
    
    def get_available_providers(self) -> List[CloudProvider]:
        return list(self.providers.keys())
    
    def configure_provider(self, provider: CloudProvider, credentials: Dict[str, str]) -> bool:
        if provider not in self.providers:
            raise CloudSyncError(f"Provider {provider.value} not available")
        
        try:
            provider_instance = self.providers[provider]
            success = provider_instance.configure(credentials)
            
            if success:
                self.logger.info(f"Successfully configured {provider.value}")
                self._save_provider_config(provider, credentials)
            
            return success
            
        except Exception as e:
            raise CloudSyncError(f"Failed to configure {provider.value}: {e}")
    
    def sync_data(self, storage, provider: CloudProvider, direction: str = "both") -> SyncStatus:
        if provider not in self.providers:
            raise CloudSyncError(f"Provider {provider.value} not configured")
        
        try:
            provider_instance = self.providers[provider]
            
            # Get local data
            local_data = self._export_local_data(storage)
            local_hash = self._calculate_hash(local_data)
            
            # Get remote data
            remote_data = provider_instance.download_data()
            remote_hash = self._calculate_hash(remote_data) if remote_data else None
            
            # Determine sync action
            if direction == "upload" or (direction == "both" and not remote_data):
                # Upload local data
                provider_instance.upload_data(local_data)
                status = "synced"
                
            elif direction == "download" or (direction == "both" and local_hash == remote_hash):
                # Download remote data
                if remote_data:
                    self._import_remote_data(storage, remote_data)
                status = "synced"
                
            elif direction == "both" and local_hash != remote_hash:
                # Conflict resolution needed
                status = "conflict"
                
            else:
                status = "pending"
            
            sync_status = SyncStatus(
                provider=provider,
                last_sync=datetime.datetime.now(),
                status=status,
                local_hash=local_hash,
                remote_hash=remote_hash
            )
            
            self.sync_status[provider] = sync_status
            self.logger.info(f"Sync completed with {provider.value}: {status}")
            
            return sync_status
            
        except Exception as e:
            error_status = SyncStatus(
                provider=provider,
                last_sync=datetime.datetime.now(),
                status="error",
                local_hash=None,
                remote_hash=None,
                error_message=str(e)
            )
            
            self.sync_status[provider] = error_status
            self.logger.error(f"Sync failed with {provider.value}: {e}")
            
            return error_status
    
    async def auto_sync(self, storage, providers: List[CloudProvider], interval_minutes: int = 30):
        self.logger.info(f"Starting auto-sync with {len(providers)} providers")
        
        while True:
            try:
                for provider in providers:
                    if provider in self.providers:
                        await asyncio.to_thread(self.sync_data, storage, provider)
                        await asyncio.sleep(1)  # Small delay between providers
                
                # Wait for next sync cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except asyncio.CancelledError:
                self.logger.info("Auto-sync cancelled")
                break
            except Exception as e:
                self.logger.error(f"Auto-sync error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def resolve_conflict(self, storage, provider: CloudProvider, resolution: str) -> SyncStatus:
        if provider not in self.sync_status:
            raise CloudSyncError(f"No sync status for {provider.value}")
        
        status = self.sync_status[provider]
        if status.status != "conflict":
            raise CloudSyncError(f"No conflict to resolve for {provider.value}")
        
        try:
            provider_instance = self.providers[provider]
            
            if resolution == "local_wins":
                # Upload local data, overwriting remote
                local_data = self._export_local_data(storage)
                provider_instance.upload_data(local_data, force=True)
                
            elif resolution == "remote_wins":
                # Download remote data, overwriting local
                remote_data = provider_instance.download_data()
                if remote_data:
                    self._import_remote_data(storage, remote_data, overwrite=True)
                
            elif resolution == "merge":
                # Attempt to merge data (basic implementation)
                local_data = self._export_local_data(storage)
                remote_data = provider_instance.download_data()
                
                if remote_data:
                    merged_data = self._merge_data(local_data, remote_data)
                    self._import_remote_data(storage, merged_data, overwrite=True)
                    provider_instance.upload_data(merged_data, force=True)
            
            else:
                raise CloudSyncError(f"Unknown resolution strategy: {resolution}")
            
            # Update sync status
            new_status = SyncStatus(
                provider=provider,
                last_sync=datetime.datetime.now(),
                status="synced",
                local_hash=self._calculate_hash(self._export_local_data(storage)),
                remote_hash=None  # Will be updated on next sync
            )
            
            self.sync_status[provider] = new_status
            self.logger.info(f"Conflict resolved for {provider.value} using {resolution}")
            
            return new_status
            
        except Exception as e:
            raise CloudSyncError(f"Failed to resolve conflict: {e}")
    
    def get_sync_status(self, provider: Optional[CloudProvider] = None) -> Union[SyncStatus, Dict[CloudProvider, SyncStatus]]:
        if provider:
            return self.sync_status.get(provider)
        else:
            return self.sync_status.copy()
    
    def list_remote_files(self, provider: CloudProvider) -> List[CloudFile]:
        if provider not in self.providers:
            raise CloudSyncError(f"Provider {provider.value} not configured")
        
        try:
            provider_instance = self.providers[provider]
            return provider_instance.list_files()
            
        except Exception as e:
            raise CloudSyncError(f"Failed to list remote files: {e}")
    
    def backup_to_cloud(self, storage, provider: CloudProvider, backup_name: Optional[str] = None) -> str:
        if provider not in self.providers:
            raise CloudSyncError(f"Provider {provider.value} not configured")
        
        try:
            # Create backup data
            backup_data = {
                "created_at": datetime.datetime.now().isoformat(),
                "backup_name": backup_name or f"logbuch_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "version": "1.0",
                "data": {
                    "tasks": storage.get_tasks(),
                    "journal_entries": storage.get_journal_entries(limit=10000),
                    "mood_entries": storage.get_mood_entries(limit=10000),
                    "sleep_entries": storage.get_sleep_entries(limit=10000),
                    "goals": storage.get_goals()
                }
            }
            
            provider_instance = self.providers[provider]
            backup_id = provider_instance.create_backup(backup_data)
            
            self.logger.info(f"Backup created in {provider.value}: {backup_id}")
            return backup_id
            
        except Exception as e:
            raise CloudSyncError(f"Failed to create cloud backup: {e}")
    
    def restore_from_cloud(self, storage, provider: CloudProvider, backup_id: str) -> bool:
        if provider not in self.providers:
            raise CloudSyncError(f"Provider {provider.value} not configured")
        
        try:
            provider_instance = self.providers[provider]
            backup_data = provider_instance.restore_backup(backup_id)
            
            if backup_data and 'data' in backup_data:
                self._import_remote_data(storage, backup_data['data'], overwrite=True)
                self.logger.info(f"Data restored from {provider.value} backup: {backup_id}")
                return True
            else:
                raise CloudSyncError("Invalid backup data format")
                
        except Exception as e:
            raise CloudSyncError(f"Failed to restore from cloud backup: {e}")
    
    def _export_local_data(self, storage) -> Dict[str, Any]:
        return {
            "tasks": storage.get_tasks(),
            "journal_entries": storage.get_journal_entries(limit=10000),
            "mood_entries": storage.get_mood_entries(limit=10000),
            "sleep_entries": storage.get_sleep_entries(limit=10000),
            "goals": storage.get_goals(),
            "exported_at": datetime.datetime.now().isoformat()
        }
    
    def _import_remote_data(self, storage, data: Dict[str, Any], overwrite: bool = False):
        if overwrite:
            # Clear existing data (implement based on storage capabilities)
            self.logger.warning("Overwrite mode - this would clear existing data")
        
        # Import data (basic implementation)
        if 'tasks' in data:
            for task_data in data['tasks']:
                # Import task (implement based on storage API)
                pass
        
        if 'journal_entries' in data:
            for entry_data in data['journal_entries']:
                # Import journal entry
                pass
        
        # Continue for other data types...
    
    def _merge_data(self, local_data: Dict[str, Any], remote_data: Dict[str, Any]) -> Dict[str, Any]:
        merged = local_data.copy()
        
        # Simple merge strategy - combine lists and deduplicate by ID
        for data_type in ['tasks', 'journal_entries', 'mood_entries', 'sleep_entries', 'goals']:
            if data_type in remote_data:
                local_items = {item.get('id'): item for item in merged.get(data_type, [])}
                remote_items = {item.get('id'): item for item in remote_data[data_type]}
                
                # Merge items, preferring newer timestamps
                for item_id, remote_item in remote_items.items():
                    if item_id not in local_items:
                        local_items[item_id] = remote_item
                    else:
                        # Compare timestamps and keep newer
                        local_time = local_items[item_id].get('updated_at', local_items[item_id].get('created_at', ''))
                        remote_time = remote_item.get('updated_at', remote_item.get('created_at', ''))
                        
                        if remote_time > local_time:
                            local_items[item_id] = remote_item
                
                merged[data_type] = list(local_items.values())
        
        return merged
    
    def _calculate_hash(self, data: Any) -> str:
        if data is None:
            return ""
        
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _save_provider_config(self, provider: CloudProvider, credentials: Dict[str, str]):
        config_path = Path.home() / ".logbuch" / "cloud_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Load existing config
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
            else:
                config_data = {}
            
            # Update with new provider config (encrypt sensitive data in production)
            config_data[provider.value] = {
                "configured_at": datetime.datetime.now().isoformat(),
                "credentials": credentials  # Should be encrypted
            }
            
            # Save config
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save provider config: {e}")


# Base class for cloud providers
class CloudProvider:
    def configure(self, credentials: Dict[str, str]) -> bool:
        raise NotImplementedError
    
    def upload_data(self, data: Dict[str, Any], force: bool = False) -> str:
        raise NotImplementedError
    
    def download_data(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
    
    def list_files(self) -> List[CloudFile]:
        raise NotImplementedError
    
    def create_backup(self, data: Dict[str, Any]) -> str:
        raise NotImplementedError
    
    def restore_backup(self, backup_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
