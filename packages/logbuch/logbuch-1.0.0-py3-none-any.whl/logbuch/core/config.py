#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/core/config.py

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from .exceptions import ConfigurationError


@dataclass
class DatabaseConfig:
    path: str
    backup_interval_hours: int = 24
    max_backups: int = 10
    auto_vacuum: bool = True
    connection_timeout: int = 30


@dataclass
class NotificationConfig:
    enabled: bool = True
    sound_enabled: bool = True
    overdue_check_interval: int = 3600  # seconds
    daily_reminder_time: str = "09:00"
    urgency_levels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.urgency_levels is None:
            self.urgency_levels = {
                'low': 'normal',
                'medium': 'normal', 
                'high': 'critical'
            }


@dataclass
class UIConfig:
    theme: str = "default"
    color_enabled: bool = True
    progress_bar_style: str = "bar"
    table_style: str = "rounded"
    max_content_length: int = 50
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M"


@dataclass
class SecurityConfig:
    input_validation: bool = True
    max_input_length: int = 10000
    allowed_file_extensions: list = None
    sanitize_paths: bool = True
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 100
    
    def __post_init__(self):
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = ['.json', '.csv', '.md', '.txt']


@dataclass
class Config:
    database: DatabaseConfig
    notifications: NotificationConfig
    ui: UIConfig
    security: SecurityConfig
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = None
    
    def __post_init__(self):
        if self.data_dir is None:
            self.data_dir = str(Path.home() / ".logbuch")


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path.home() / ".logbuch" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[Config] = None
    
    def load(self) -> Config:
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._config = self._deserialize_config(config_data)
            else:
                self._config = self._create_default_config()
                self.save()  # Save defaults for future use
            
            self._validate_config()
            return self._config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save(self) -> None:
        if not self._config:
            raise ConfigurationError("No configuration loaded to save")
        
        try:
            config_data = self._serialize_config(self._config)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def get(self) -> Config:
        if not self._config:
            self.load()
        return self._config
    
    def update(self, **kwargs) -> None:
        if not self._config:
            self.load()
        
        # Update configuration fields
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self._validate_config()
        self.save()
    
    def reset_to_defaults(self) -> None:
        self._config = self._create_default_config()
        self.save()
    
    def _create_default_config(self) -> Config:
        data_dir = str(Path.home() / ".logbuch")
        
        return Config(
            database=DatabaseConfig(
                path=os.path.join(data_dir, "logbuch.db")
            ),
            notifications=NotificationConfig(),
            ui=UIConfig(),
            security=SecurityConfig(),
            data_dir=data_dir
        )
    
    def _serialize_config(self, config: Config) -> Dict[str, Any]:
        return {
            'database': asdict(config.database),
            'notifications': asdict(config.notifications),
            'ui': asdict(config.ui),
            'security': asdict(config.security),
            'debug': config.debug,
            'log_level': config.log_level,
            'data_dir': config.data_dir
        }
    
    def _deserialize_config(self, data: Dict[str, Any]) -> Config:
        return Config(
            database=DatabaseConfig(**data.get('database', {})),
            notifications=NotificationConfig(**data.get('notifications', {})),
            ui=UIConfig(**data.get('ui', {})),
            security=SecurityConfig(**data.get('security', {})),
            debug=data.get('debug', False),
            log_level=data.get('log_level', 'INFO'),
            data_dir=data.get('data_dir')
        )
    
    def _validate_config(self) -> None:
        if not self._config:
            return
        
        # Validate database path
        db_path = Path(self._config.database.path)
        if not db_path.parent.exists():
            try:
                db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ConfigurationError(f"Cannot create database directory: {e}")
        
        # Validate data directory
        data_dir = Path(self._config.data_dir)
        if not data_dir.exists():
            try:
                data_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ConfigurationError(f"Cannot create data directory: {e}")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self._config.log_level not in valid_log_levels:
            raise ConfigurationError(f"Invalid log level: {self._config.log_level}")
        
        # Validate notification time format
        try:
            from datetime import datetime
            datetime.strptime(self._config.notifications.daily_reminder_time, "%H:%M")
        except ValueError:
            raise ConfigurationError("Invalid daily reminder time format (use HH:MM)")


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> Config:
    return get_config_manager().get()
