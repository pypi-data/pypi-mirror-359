#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/integrations/github_gists.py

import json
try:
    import requests
except ImportError:
    requests = None
import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass

from logbuch.core.logger import get_logger
from logbuch.core.config import get_config
from logbuch.core.exceptions import LogbuchError
from logbuch.core.security import get_security_manager


class GistError(LogbuchError):
    pass


@dataclass
class GistFile:
    filename: str
    content: str
    language: Optional[str] = None
    size: Optional[int] = None
    raw_url: Optional[str] = None


@dataclass
class Gist:
    id: str
    description: str
    public: bool
    files: Dict[str, GistFile]
    html_url: str
    git_pull_url: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner: Optional[str] = None


class GitHubGistManager:
    def __init__(self, token: Optional[str] = None):
        if requests is None:
            raise ImportError("GitHub Gists integration requires 'requests' library. Install with: pip install requests")
            
        self.logger = get_logger("github_gists")
        self.security = get_security_manager()
        self.config = get_config()
        
        # GitHub API configuration
        self.base_url = "https://api.github.com"
        self.token = token or self._get_token_from_config()
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Logbuch-CLI/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _get_token_from_config(self) -> Optional[str]:
        import os
        
        # Try environment variable first
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_GIST_TOKEN')
        if token:
            return token
        
        # Try config file
        try:
            config_path = Path.home() / ".logbuch" / "github_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    return config_data.get('token')
        except Exception as e:
            self.logger.warning(f"Failed to load GitHub config: {e}")
        
        return None
    
    def set_token(self, token: str) -> None:
        self.token = token
        self.headers["Authorization"] = f"token {token}"
        self.session.headers.update(self.headers)
        
        # Save to config
        try:
            config_path = Path.home() / ".logbuch" / "github_config.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {"token": token, "updated_at": datetime.datetime.now().isoformat()}
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info("GitHub token saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save GitHub token: {e}")
    
    def test_authentication(self) -> bool:
        if not self.token:
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/user")
            if response.status_code == 200:
                user_data = response.json()
                self.logger.info(f"Authenticated as GitHub user: {user_data.get('login')}")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Authentication test failed: {e}")
            return False
    
    def create_gist(
        self, 
        files: Dict[str, str], 
        description: str = "", 
        public: bool = False
    ) -> Gist:
        if not self.token:
            raise GistError("GitHub token required to create gists")
        
        # Prepare files data
        gist_files = {}
        for filename, content in files.items():
            # Security check
            safe_filename = self.security.sanitize_user_input(filename, "filename")
            safe_content = self.security.sanitize_user_input(content, "text")
            
            gist_files[safe_filename] = {"content": safe_content}
        
        # Prepare gist data
        gist_data = {
            "description": description,
            "public": public,
            "files": gist_files
        }
        
        try:
            response = self.session.post(f"{self.base_url}/gists", json=gist_data)
            response.raise_for_status()
            
            gist_json = response.json()
            gist = self._parse_gist_response(gist_json)
            
            self.logger.info(f"Created gist: {gist.id}")
            return gist
            
        except requests.RequestException as e:
            raise GistError(f"Failed to create gist: {e}")
    
    def get_gist(self, gist_id: str) -> Gist:
        try:
            response = self.session.get(f"{self.base_url}/gists/{gist_id}")
            response.raise_for_status()
            
            gist_json = response.json()
            return self._parse_gist_response(gist_json)
            
        except requests.RequestException as e:
            raise GistError(f"Failed to get gist {gist_id}: {e}")
    
    def list_gists(self, per_page: int = 30) -> List[Gist]:
        if not self.token:
            raise GistError("GitHub token required to list gists")
        
        try:
            response = self.session.get(f"{self.base_url}/gists", params={"per_page": per_page})
            response.raise_for_status()
            
            gists_json = response.json()
            return [self._parse_gist_response(gist_data) for gist_data in gists_json]
            
        except requests.RequestException as e:
            raise GistError(f"Failed to list gists: {e}")
    
    def update_gist(self, gist_id: str, files: Dict[str, str], description: Optional[str] = None) -> Gist:
        if not self.token:
            raise GistError("GitHub token required to update gists")
        
        # Prepare update data
        update_data = {}
        
        if description is not None:
            update_data["description"] = description
        
        if files:
            gist_files = {}
            for filename, content in files.items():
                safe_filename = self.security.sanitize_user_input(filename, "filename")
                safe_content = self.security.sanitize_user_input(content, "text")
                gist_files[safe_filename] = {"content": safe_content}
            update_data["files"] = gist_files
        
        try:
            response = self.session.patch(f"{self.base_url}/gists/{gist_id}", json=update_data)
            response.raise_for_status()
            
            gist_json = response.json()
            gist = self._parse_gist_response(gist_json)
            
            self.logger.info(f"Updated gist: {gist.id}")
            return gist
            
        except requests.RequestException as e:
            raise GistError(f"Failed to update gist {gist_id}: {e}")
    
    def delete_gist(self, gist_id: str) -> bool:
        if not self.token:
            raise GistError("GitHub token required to delete gists")
        
        try:
            response = self.session.delete(f"{self.base_url}/gists/{gist_id}")
            response.raise_for_status()
            
            self.logger.info(f"Deleted gist: {gist_id}")
            return True
            
        except requests.RequestException as e:
            raise GistError(f"Failed to delete gist {gist_id}: {e}")
    
    def _parse_gist_response(self, gist_data: Dict[str, Any]) -> Gist:
        files = {}
        for filename, file_data in gist_data.get("files", {}).items():
            files[filename] = GistFile(
                filename=filename,
                content=file_data.get("content", ""),
                language=file_data.get("language"),
                size=file_data.get("size"),
                raw_url=file_data.get("raw_url")
            )
        
        return Gist(
            id=gist_data["id"],
            description=gist_data.get("description", ""),
            public=gist_data.get("public", False),
            files=files,
            html_url=gist_data["html_url"],
            git_pull_url=gist_data["git_pull_url"],
            created_at=datetime.datetime.fromisoformat(gist_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.datetime.fromisoformat(gist_data["updated_at"].replace("Z", "+00:00")),
            owner=gist_data.get("owner", {}).get("login") if gist_data.get("owner") else None
        )
    
    # Logbuch-specific methods
    
    def share_tasks_as_gist(self, storage, task_ids: List[str], public: bool = False) -> Gist:
        tasks = storage.get_tasks()
        selected_tasks = [task for task in tasks if task['id'] in task_ids]
        
        if not selected_tasks:
            raise GistError("No tasks found with the specified IDs")
        
        # Format tasks as markdown
        content = self._format_tasks_as_markdown(selected_tasks)
        
        files = {
            "logbuch_tasks.md": content
        }
        
        description = f"Logbuch Tasks - {len(selected_tasks)} task(s) shared on {datetime.date.today()}"
        
        return self.create_gist(files, description, public)
    
    def share_journal_as_gist(self, storage, date_range: Optional[tuple] = None, public: bool = False) -> Gist:
        entries = storage.get_journal_entries(limit=1000)
        
        if date_range:
            start_date, end_date = date_range
            entries = [
                entry for entry in entries
                if start_date <= datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00')).date() <= end_date
            ]
        
        if not entries:
            raise GistError("No journal entries found for the specified criteria")
        
        # Format entries as markdown
        content = self._format_journal_as_markdown(entries)
        
        files = {
            "logbuch_journal.md": content
        }
        
        description = f"Logbuch Journal - {len(entries)} entries shared on {datetime.date.today()}"
        
        return self.create_gist(files, description, public)
    
    def share_dashboard_as_gist(self, storage, public: bool = False) -> Gist:
        # Collect dashboard data
        tasks = storage.get_tasks()
        journal_entries = storage.get_journal_entries(limit=10)
        mood_entries = storage.get_mood_entries(limit=10)
        goals = storage.get_goals()
        
        # Create comprehensive dashboard
        dashboard_content = self._format_dashboard_as_markdown(tasks, journal_entries, mood_entries, goals)
        
        files = {
            "logbuch_dashboard.md": dashboard_content
        }
        
        description = f"Logbuch Dashboard Snapshot - {datetime.date.today()}"
        
        return self.create_gist(files, description, public)
    
    def backup_to_gist(self, storage, public: bool = False) -> Gist:
        # Export all data
        backup_data = {
            "exported_at": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "data": {
                "tasks": storage.get_tasks(),
                "journal_entries": storage.get_journal_entries(limit=10000),
                "mood_entries": storage.get_mood_entries(limit=10000),
                "sleep_entries": storage.get_sleep_entries(limit=10000),
                "goals": storage.get_goals()
            }
        }
        
        files = {
            "logbuch_backup.json": json.dumps(backup_data, indent=2, ensure_ascii=False),
            "README.md": self._create_backup_readme()
        }
        
        description = f"Logbuch Complete Backup - {datetime.date.today()}"
        
        return self.create_gist(files, description, public)
    
    def _format_tasks_as_markdown(self, tasks: List[Dict]) -> str:
        content = ["# 📋 Logbuch Tasks\n"]
        content.append(f"*Shared on {datetime.date.today()}*\n")
        
        # Group by priority
        high_priority = [t for t in tasks if t.get('priority') == 'high']
        medium_priority = [t for t in tasks if t.get('priority') == 'medium']
        low_priority = [t for t in tasks if t.get('priority') == 'low']
        
        for priority_name, priority_tasks in [
            ("🔥 High Priority", high_priority),
            ("📋 Medium Priority", medium_priority), 
            ("📝 Low Priority", low_priority)
        ]:
            if priority_tasks:
                content.append(f"## {priority_name}\n")
                for task in priority_tasks:
                    status = "✅" if task.get('done') else "⏳"
                    content.append(f"- {status} **{task['content']}**")
                    
                    if task.get('due_date'):
                        content.append(f" - Due: {task['due_date'][:10]}")
                    
                    if task.get('tags'):
                        tags = ', '.join(f"`{tag}`" for tag in task['tags'])
                        content.append(f" - Tags: {tags}")
                    
                    content.append("")
                content.append("")
        
        return "\n".join(content)
    
    def _format_journal_as_markdown(self, entries: List[Dict]) -> str:
        content = ["# 📝 Logbuch Journal\n"]
        content.append(f"*Shared on {datetime.date.today()}*\n")
        
        for entry in sorted(entries, key=lambda x: x['date'], reverse=True):
            date_obj = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
            date_str = date_obj.strftime('%B %d, %Y')
            
            content.append(f"## {date_str}\n")
            content.append(f"{entry['text']}\n")
            
            if entry.get('tags'):
                tags = ', '.join(f"`{tag}`" for tag in entry['tags'])
                content.append(f"*Tags: {tags}*\n")
            
            content.append("---\n")
        
        return "\n".join(content)
    
    def _format_dashboard_as_markdown(self, tasks, journal_entries, mood_entries, goals) -> str:
        content = ["# 📊 Logbuch Dashboard\n"]
        content.append(f"*Generated on {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}*\n")
        
        # Task summary
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('done')])
        pending_tasks = total_tasks - completed_tasks
        
        content.append("## 📋 Task Summary\n")
        content.append(f"- **Total Tasks:** {total_tasks}")
        content.append(f"- **Completed:** {completed_tasks}")
        content.append(f"- **Pending:** {pending_tasks}")
        content.append("")
        
        # Recent tasks
        if tasks:
            content.append("### Recent Tasks\n")
            recent_tasks = sorted(tasks, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            for task in recent_tasks:
                status = "✅" if task.get('done') else "⏳"
                content.append(f"- {status} {task['content']}")
            content.append("")
        
        # Goals progress
        if goals:
            content.append("## 🎯 Goals Progress\n")
            for goal in goals:
                progress = goal.get('progress', 0)
                status = "✅" if goal.get('completed') else "⏳"
                content.append(f"- {status} **{goal['description']}** - {progress}%")
            content.append("")
        
        # Recent journal entries
        if journal_entries:
            content.append("## 📝 Recent Journal Entries\n")
            for entry in journal_entries[:3]:
                date_obj = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
                date_str = date_obj.strftime('%m-%d')
                preview = entry['text'][:100] + ('...' if len(entry['text']) > 100 else '')
                content.append(f"**{date_str}:** {preview}\n")
        
        # Recent moods
        if mood_entries:
            content.append("## 😊 Recent Moods\n")
            for mood in mood_entries[:5]:
                date_obj = datetime.datetime.fromisoformat(mood['date'].replace('Z', '+00:00'))
                date_str = date_obj.strftime('%m-%d')
                content.append(f"- **{date_str}:** {mood['mood']}")
            content.append("")
        
        content.append("---")
        content.append("*Generated by [Logbuch](https://github.com/your-username/logbuch) - Personal Productivity CLI*")
        
        return "\n".join(content)
    
    def _create_backup_readme(self) -> str:
        return """# 💾 Logbuch Backup

This is a complete backup of your Logbuch data, exported as JSON.

## Contents

- **logbuch_backup.json**: Complete data export including tasks, journal entries, moods, sleep data, and goals

## Restore Instructions

To restore this backup:

1. Install Logbuch CLI
2. Use the import command: `logbuch import logbuch_backup.json`

## Data Format

The backup uses Logbuch's standard JSON export format, compatible with all import/export features.

---

*Generated by [Logbuch](https://github.com/your-username/logbuch) - Personal Productivity CLI*
"""
