#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/integrations.py

import datetime
from typing import List, Optional
from rich.table import Table
from rich.console import Console
from rich import print as rprint
from rich.prompt import Prompt, Confirm

# Simple base command class
class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
    
    def execute(self, **kwargs):
        return True
# Import integrations with error handling
try:
    from logbuch.integrations.github_gists import GitHubGistManager, GistError
    GITHUB_AVAILABLE = True
except ImportError as e:
    GITHUB_AVAILABLE = False
    GITHUB_ERROR = str(e)

try:
    from logbuch.integrations.smart_suggestions import SmartSuggestionEngine
    SUGGESTIONS_AVAILABLE = True
except ImportError as e:
    SUGGESTIONS_AVAILABLE = False
    SUGGESTIONS_ERROR = str(e)

try:
    from logbuch.integrations.cloud_sync import CloudSyncManager, CloudProvider
    CLOUD_AVAILABLE = True
except ImportError as e:
    CLOUD_AVAILABLE = False
    CLOUD_ERROR = str(e)

try:
    from logbuch.integrations.webhook_server import WebhookServer, LogbuchWebhookHandlers
    WEBHOOK_AVAILABLE = True
except ImportError as e:
    WEBHOOK_AVAILABLE = False
    WEBHOOK_ERROR = str(e)


class GitHubGistCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        if not GITHUB_AVAILABLE:
            self.gist_manager = None
        else:
            self.gist_manager = GitHubGistManager()
    
    def execute(self, action: str, **kwargs) -> None:
        if not GITHUB_AVAILABLE:
            print(f"❌ GitHub Gists integration not available: {GITHUB_ERROR}")
            print("💡 Install with: pip install requests")
            return
        
        if action == "setup":
            self._setup_github_token()
        
        elif action == "test":
            self._test_authentication()
        
        elif action == "share":
            self._share_content(**kwargs)
        
        elif action == "list":
            self._list_gists()
        
        elif action == "backup":
            self._create_backup(**kwargs)
        
        elif action == "restore":
            self._restore_from_gist(**kwargs)
        
        else:
            self.error(f"Unknown action: {action}")
    
    def _setup_github_token(self):
        self.console.print("[bold cyan]🔧 GitHub Gist Setup[/bold cyan]")
        self.console.print("To use GitHub Gists, you need a personal access token.")
        self.console.print("Create one at: https://github.com/settings/tokens")
        self.console.print("Required scopes: 'gist'")
        
        token = Prompt.ask("Enter your GitHub token", password=True)
        
        if token:
            self.gist_manager.set_token(token)
            if self.gist_manager.test_authentication():
                self.success("GitHub token configured successfully!")
            else:
                self.error("Failed to authenticate with GitHub")
        else:
            self.warning("Setup cancelled")
    
    def _test_authentication(self):
        if self.gist_manager.test_authentication():
            self.success("GitHub authentication successful!")
        else:
            self.error("GitHub authentication failed. Run 'logbuch gist setup' to configure.")
    
    def _share_content(self, content_type: str, **kwargs):
        try:
            public = kwargs.get('public', False)
            
            if content_type == "tasks":
                task_ids = kwargs.get('task_ids', [])
                if not task_ids:
                    # Get recent tasks
                    tasks = self.storage.get_tasks()
                    incomplete_tasks = [t for t in tasks if not t.get('done')][:10]
                    task_ids = [t['id'] for t in incomplete_tasks]
                
                gist = self.gist_manager.share_tasks_as_gist(self.storage, task_ids, public)
                self.success(f"Tasks shared as gist: {gist.html_url}")
            
            elif content_type == "journal":
                date_range = kwargs.get('date_range')
                gist = self.gist_manager.share_journal_as_gist(self.storage, date_range, public)
                self.success(f"Journal shared as gist: {gist.html_url}")
            
            elif content_type == "dashboard":
                gist = self.gist_manager.share_dashboard_as_gist(self.storage, public)
                self.success(f"Dashboard shared as gist: {gist.html_url}")
            
            else:
                self.error(f"Unknown content type: {content_type}")
                
        except GistError as e:
            self.error(f"Failed to share content: {e}")
    
    def _list_gists(self):
        try:
            gists = self.gist_manager.list_gists()
            
            if not gists:
                self.info("No gists found")
                return
            
            table = Table(title="📋 Your GitHub Gists")
            table.add_column("ID", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Files", style="yellow")
            table.add_column("Public", style="green")
            table.add_column("Updated", style="blue")
            
            for gist in gists:
                table.add_row(
                    gist.id[:8] + "...",
                    gist.description[:50] + ("..." if len(gist.description) > 50 else ""),
                    str(len(gist.files)),
                    "Yes" if gist.public else "No",
                    gist.updated_at.strftime("%m-%d %H:%M")
                )
            
            self.console.print(table)
            
        except GistError as e:
            self.error(f"Failed to list gists: {e}")
    
    def _create_backup(self, public: bool = False):
        try:
            gist = self.gist_manager.backup_to_gist(self.storage, public)
            self.success(f"Backup created: {gist.html_url}")
            self.info(f"Gist ID: {gist.id}")
            
        except GistError as e:
            self.error(f"Failed to create backup: {e}")
    
    def _restore_from_gist(self, gist_id: str):
        if not gist_id:
            self.error("Gist ID required for restore")
            return
        
        if not self.confirm("This will overwrite your current data. Continue?"):
            self.warning("Restore cancelled")
            return
        
        try:
            # Implementation would depend on storage capabilities
            self.info(f"Restore from gist {gist_id} - feature coming soon!")
            
        except GistError as e:
            self.error(f"Failed to restore from gist: {e}")


class SmartSuggestionsCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        if not SUGGESTIONS_AVAILABLE:
            self.suggestion_engine = None
        else:
            self.suggestion_engine = SmartSuggestionEngine()
    
    def execute(self, **kwargs) -> None:
        if not SUGGESTIONS_AVAILABLE:
            print(f"❌ Smart Suggestions not available: {SUGGESTIONS_ERROR}")
            return
        
        self.console.print("[bold cyan]🧠 Analyzing your productivity patterns...[/bold cyan]")
        
        suggestions = self.suggestion_engine.analyze_and_suggest(self.storage)
        
        if not suggestions:
            self.info("No suggestions available at this time.")
            return
        
        self.console.print(f"\n[bold green]✨ Found {len(suggestions)} smart suggestions:[/bold green]\n")
        
        for i, suggestion in enumerate(suggestions, 1):
            # Priority indicator
            priority_color = {
                'high': 'red',
                'medium': 'yellow', 
                'low': 'blue'
            }.get(suggestion.priority, 'white')
            
            priority_icon = {
                'high': '🔥',
                'medium': '⚡',
                'low': '💡'
            }.get(suggestion.priority, '📝')
            
            self.console.print(f"[bold]{i}. {priority_icon} {suggestion.title}[/bold]")
            self.console.print(f"   [{priority_color}]{suggestion.priority.upper()} PRIORITY[/{priority_color}] • Confidence: {suggestion.confidence:.0%}")
            self.console.print(f"   {suggestion.description}")
            
            if suggestion.action:
                self.console.print(f"   [dim]💡 Suggested action: {suggestion.action}[/dim]")
            
            self.console.print()
        
        # Ask if user wants to act on suggestions
        if self.confirm("Would you like to act on any of these suggestions?"):
            self._handle_suggestion_actions(suggestions)
    
    def _handle_suggestion_actions(self, suggestions):
        self.console.print("\n[cyan]Available actions:[/cyan]")
        
        for i, suggestion in enumerate(suggestions, 1):
            if suggestion.action:
                self.console.print(f"{i}. {suggestion.title} → {suggestion.action}")
        
        choice = Prompt.ask("Enter suggestion number to act on (or 'skip')", default="skip")
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(suggestions):
                suggestion = suggestions[idx]
                self._execute_suggestion_action(suggestion)
        else:
            self.info("No action taken")
    
    def _execute_suggestion_action(self, suggestion):
        action = suggestion.action
        
        if action == "bulk_cleanup":
            self.info("💡 Consider using: logbuch bulk --cleanup 30")
        
        elif action == "set_priorities":
            self.info("💡 Consider using: logbuch task --list and set priorities manually")
        
        elif action == "create_goals":
            self.info("💡 Consider using: logbuch goal 'Your meaningful goal'")
        
        elif action == "start_mood_tracking":
            self.info("💡 Consider using: logbuch mood --random to start tracking")
        
        elif action == "add_due_dates":
            self.info("💡 Consider using: logbuch qtask with -d flag for natural dates")
        
        else:
            self.info(f"💡 Suggestion: {suggestion.description}")


class CloudSyncCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.sync_manager = CloudSyncManager()
    
    def execute(self, action: str, **kwargs) -> None:
        if action == "providers":
            self._list_providers()
        
        elif action == "setup":
            self._setup_provider(**kwargs)
        
        elif action == "sync":
            self._sync_data(**kwargs)
        
        elif action == "status":
            self._show_sync_status()
        
        elif action == "backup":
            self._create_cloud_backup(**kwargs)
        
        elif action == "restore":
            self._restore_from_cloud(**kwargs)
        
        else:
            self.error(f"Unknown action: {action}")
    
    def _list_providers(self):
        providers = self.sync_manager.get_available_providers()
        
        table = Table(title="☁️ Available Cloud Providers")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Description", style="white")
        
        provider_info = {
            CloudProvider.GOOGLE_DRIVE: "Google Drive integration",
            CloudProvider.DROPBOX: "Dropbox integration", 
            CloudProvider.GITHUB_GIST: "GitHub Gists integration",
            CloudProvider.ONEDRIVE: "Microsoft OneDrive integration",
            CloudProvider.CUSTOM_S3: "Custom S3-compatible storage"
        }
        
        for provider in CloudProvider:
            status = "✅ Available" if provider in providers else "❌ Not Available"
            description = provider_info.get(provider, "Cloud storage provider")
            
            table.add_row(
                provider.value,
                status,
                description
            )
        
        self.console.print(table)
    
    def _setup_provider(self, provider_name: str):
        try:
            provider = CloudProvider(provider_name)
        except ValueError:
            self.error(f"Unknown provider: {provider_name}")
            return
        
        self.console.print(f"[bold cyan]🔧 Setting up {provider.value}[/bold cyan]")
        
        if provider == CloudProvider.GITHUB_GIST:
            self.info("Use 'logbuch gist setup' for GitHub Gist configuration")
            return
        
        # Generic provider setup
        credentials = {}
        
        if provider == CloudProvider.GOOGLE_DRIVE:
            credentials['client_id'] = Prompt.ask("Google Client ID")
            credentials['client_secret'] = Prompt.ask("Google Client Secret", password=True)
        
        elif provider == CloudProvider.DROPBOX:
            credentials['access_token'] = Prompt.ask("Dropbox Access Token", password=True)
        
        # Configure provider
        try:
            success = self.sync_manager.configure_provider(provider, credentials)
            if success:
                self.success(f"{provider.value} configured successfully!")
            else:
                self.error(f"Failed to configure {provider.value}")
        except Exception as e:
            self.error(f"Configuration failed: {e}")
    
    def _sync_data(self, provider_name: str, direction: str = "both"):
        try:
            provider = CloudProvider(provider_name)
            
            self.console.print(f"[cyan]🔄 Syncing with {provider.value}...[/cyan]")
            
            status = self.sync_manager.sync_data(self.storage, provider, direction)
            
            if status.status == "synced":
                self.success(f"Sync completed successfully with {provider.value}")
            elif status.status == "conflict":
                self.warning(f"Sync conflict detected with {provider.value}")
                self._handle_sync_conflict(provider, status)
            elif status.status == "error":
                self.error(f"Sync failed: {status.error_message}")
            else:
                self.info(f"Sync status: {status.status}")
                
        except ValueError:
            self.error(f"Unknown provider: {provider_name}")
        except Exception as e:
            self.error(f"Sync failed: {e}")
    
    def _show_sync_status(self):
        status_dict = self.sync_manager.get_sync_status()
        
        if not status_dict:
            self.info("No sync status available")
            return
        
        table = Table(title="☁️ Cloud Sync Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Last Sync", style="blue")
        table.add_column("Details", style="white")
        
        for provider, status in status_dict.items():
            status_color = {
                'synced': 'green',
                'pending': 'yellow',
                'error': 'red',
                'conflict': 'orange'
            }.get(status.status, 'white')
            
            last_sync = status.last_sync.strftime("%m-%d %H:%M") if status.last_sync else "Never"
            details = status.error_message if status.error_message else "OK"
            
            table.add_row(
                provider.value,
                f"[{status_color}]{status.status.upper()}[/{status_color}]",
                last_sync,
                details[:50] + ("..." if len(details) > 50 else "")
            )
        
        self.console.print(table)
    
    def _handle_sync_conflict(self, provider: CloudProvider, status):
        self.console.print(f"\n[yellow]⚠️ Sync conflict with {provider.value}[/yellow]")
        self.console.print("Local and remote data differ. Choose resolution:")
        self.console.print("1. Keep local data (upload)")
        self.console.print("2. Keep remote data (download)")
        self.console.print("3. Attempt merge")
        
        choice = Prompt.ask("Choose resolution", choices=["1", "2", "3"], default="3")
        
        resolution_map = {
            "1": "local_wins",
            "2": "remote_wins", 
            "3": "merge"
        }
        
        try:
            resolved_status = self.sync_manager.resolve_conflict(
                self.storage, 
                provider, 
                resolution_map[choice]
            )
            
            if resolved_status.status == "synced":
                self.success("Conflict resolved successfully!")
            else:
                self.error("Failed to resolve conflict")
                
        except Exception as e:
            self.error(f"Conflict resolution failed: {e}")
    
    def _create_cloud_backup(self, provider_name: str):
        try:
            provider = CloudProvider(provider_name)
            backup_id = self.sync_manager.backup_to_cloud(self.storage, provider)
            self.success(f"Backup created in {provider.value}: {backup_id}")
            
        except Exception as e:
            self.error(f"Backup failed: {e}")
    
    def _restore_from_cloud(self, provider_name: str, backup_id: str):
        if not self.confirm("This will overwrite your current data. Continue?"):
            self.warning("Restore cancelled")
            return
        
        try:
            provider = CloudProvider(provider_name)
            success = self.sync_manager.restore_from_cloud(self.storage, provider, backup_id)
            
            if success:
                self.success("Data restored successfully!")
            else:
                self.error("Restore failed")
                
        except Exception as e:
            self.error(f"Restore failed: {e}")


class WebhookCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.webhook_server = None
    
    def execute(self, action: str, **kwargs) -> None:
        if action == "start":
            self._start_server(**kwargs)
        
        elif action == "stop":
            self._stop_server()
        
        elif action == "status":
            self._show_status()
        
        elif action == "events":
            self._list_events()
        
        elif action == "setup":
            self._setup_webhooks()
        
        else:
            self.error(f"Unknown action: {action}")
    
    def _start_server(self, port: int = 8080, host: str = "localhost"):
        try:
            self.webhook_server = WebhookServer(port=port, host=host)
            
            # Register handlers
            handlers = LogbuchWebhookHandlers(self.storage)
            handlers.register_all_handlers(self.webhook_server)
            
            # Add some API keys for testing
            self.webhook_server.add_api_key("logbuch-test-key")
            
            self.webhook_server.start_server(background=True)
            self.success(f"Webhook server started on {host}:{port}")
            self.info("Available endpoints:")
            self.info(f"  • http://{host}:{port}/webhook/{{source}}")
            self.info(f"  • http://{host}:{port}/api/events")
            self.info(f"  • http://{host}:{port}/api/health")
            
        except Exception as e:
            self.error(f"Failed to start webhook server: {e}")
    
    def _stop_server(self):
        if self.webhook_server:
            self.webhook_server.stop_server()
            self.success("Webhook server stopped")
        else:
            self.warning("No webhook server running")
    
    def _show_status(self):
        if self.webhook_server and self.webhook_server.is_running:
            self.success(f"Webhook server running on {self.webhook_server.host}:{self.webhook_server.port}")
            self.info(f"Events processed: {len([e for e in self.webhook_server.events if e.processed])}")
            self.info(f"Events pending: {len([e for e in self.webhook_server.events if not e.processed])}")
        else:
            self.info("Webhook server not running")
    
    def _list_events(self):
        if not self.webhook_server:
            self.error("No webhook server instance")
            return
        
        events = self.webhook_server.events[-20:]  # Last 20 events
        
        if not events:
            self.info("No webhook events")
            return
        
        table = Table(title="🔗 Recent Webhook Events")
        table.add_column("Source", style="cyan")
        table.add_column("Event Type", style="yellow")
        table.add_column("Timestamp", style="blue")
        table.add_column("Status", style="green")
        
        for event in events:
            status = "✅ Processed" if event.processed else "⏳ Pending"
            table.add_row(
                event.source,
                event.event_type,
                event.timestamp.strftime("%m-%d %H:%M:%S"),
                status
            )
        
        self.console.print(table)
    
    def _setup_webhooks(self):
        self.console.print("[bold cyan]🔗 Webhook Integration Setup[/bold cyan]")
        self.console.print("\nAvailable integrations:")
        self.console.print("1. GitHub - Receive push notifications")
        self.console.print("2. IFTTT - Trigger actions from web services")
        self.console.print("3. Zapier - Connect with 3000+ apps")
        self.console.print("4. Calendar - Get meeting reminders")
        self.console.print("5. Email - Convert emails to tasks")
        
        self.console.print("\nTo set up webhooks:")
        self.console.print("1. Start the webhook server: logbuch webhook start")
        self.console.print("2. Use ngrok or similar to expose your local server")
        self.console.print("3. Configure your services to send webhooks to:")
        self.console.print("   http://your-domain.com/webhook/{source}")
        
        self.info("Example webhook URLs:")
        self.info("  • GitHub: http://localhost:8080/webhook/github")
        self.info("  • IFTTT: http://localhost:8080/webhook/ifttt")
        self.info("  • Zapier: http://localhost:8080/webhook/zapier")
