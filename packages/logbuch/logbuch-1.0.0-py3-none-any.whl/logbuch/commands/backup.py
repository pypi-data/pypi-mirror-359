#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/backup.py

import os
import shutil
import datetime
import json
import sqlite3
from pathlib import Path
from rich import print as rprint
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


def get_backup_dir():
    home = Path.home()
    backup_dir = home / ".logbuch" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def create_backup(storage, backup_name=None, auto=False):
    console = Console()
    
    if not backup_name:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"logbuch_backup_{timestamp}"
    
    backup_dir = get_backup_dir()
    backup_path = backup_dir / f"{backup_name}.json"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Creating backup...", total=None)
        
        # Collect all data
        backup_data = {
            "created_at": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "data": {
                "tasks": storage.get_tasks(),
                "journal_entries": storage.get_journal_entries(limit=10000),
                "mood_entries": storage.get_mood_entries(limit=10000),
                "sleep_entries": storage.get_sleep_entries(limit=10000),
                "goals": storage.get_goals(),
                "time_entries": getattr(storage, 'get_time_entries', lambda limit=10000: [])(limit=10000),
                "boards": getattr(storage, 'get_boards', lambda: [])()
            },
            "stats": {
                "total_tasks": len(storage.get_tasks()),
                "total_journal_entries": len(storage.get_journal_entries(limit=10000)),
                "total_mood_entries": len(storage.get_mood_entries(limit=10000)),
                "total_goals": len(storage.get_goals())
            }
        }
        
        progress.update(task, description="Writing backup file...")
        
        # Write backup file
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        progress.update(task, description="Creating database backup...")
        
        # Also create a direct database backup
        db_backup_path = backup_dir / f"{backup_name}.db"
        if hasattr(storage, 'db_path') and os.path.exists(storage.db_path):
            shutil.copy2(storage.db_path, db_backup_path)
    
    file_size = backup_path.stat().st_size / 1024  # KB
    
    if not auto:
        rprint(f"[green]✅ Backup created successfully![/green]")
        rprint(f"[blue]📁 Location: {backup_path}[/blue]")
        rprint(f"[blue]💾 Size: {file_size:.1f} KB[/blue]")
        rprint(f"[blue]📊 Data: {backup_data['stats']['total_tasks']} tasks, {backup_data['stats']['total_journal_entries']} journal entries[/blue]")
    
    return backup_path


def list_backups():
    console = Console()
    backup_dir = get_backup_dir()
    
    backups = []
    for backup_file in backup_dir.glob("*.json"):
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            created_at = datetime.datetime.fromisoformat(backup_data.get('created_at', ''))
            stats = backup_data.get('stats', {})
            file_size = backup_file.stat().st_size / 1024  # KB
            
            backups.append({
                'name': backup_file.stem,
                'path': backup_file,
                'created_at': created_at,
                'size_kb': file_size,
                'tasks': stats.get('total_tasks', 0),
                'journals': stats.get('total_journal_entries', 0),
                'moods': stats.get('total_mood_entries', 0)
            })
        except Exception as e:
            # Skip corrupted backup files
            continue
    
    if not backups:
        rprint("[yellow]No backups found. Create one with: logbuch backup create[/yellow]")
        return []
    
    # Sort by creation date (newest first)
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    
    table = Table(title="💾 Available Backups")
    table.add_column("Name", style="cyan")
    table.add_column("Created", style="blue")
    table.add_column("Size", style="green")
    table.add_column("Tasks", style="yellow")
    table.add_column("Journals", style="magenta")
    table.add_column("Moods", style="red")
    
    for backup in backups:
        table.add_row(
            backup['name'],
            backup['created_at'].strftime('%m-%d %H:%M'),
            f"{backup['size_kb']:.1f}KB",
            str(backup['tasks']),
            str(backup['journals']),
            str(backup['moods'])
        )
    
    console.print(table)
    return backups


def restore_backup(storage, backup_name):
    console = Console()
    backup_dir = get_backup_dir()
    
    # Find backup file
    backup_path = None
    if backup_name == "latest":
        backups = list_backups()
        if backups:
            backup_path = backups[0]['path']
            backup_name = backups[0]['name']
    else:
        backup_path = backup_dir / f"{backup_name}.json"
    
    if not backup_path or not backup_path.exists():
        rprint(f"[red]❌ Backup '{backup_name}' not found[/red]")
        return False
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            task = progress.add_task("Loading backup...", total=None)
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            progress.update(task, description="Restoring data...")
            
            # Clear existing data (with confirmation in the CLI command)
            # This is a destructive operation, so we'll handle confirmation in the CLI
            
            # Restore data
            data = backup_data.get('data', {})
            restored_counts = {}
            
            # Restore tasks
            if 'tasks' in data:
                for task_data in data['tasks']:
                    # Remove ID to let storage assign new ones
                    task_data_copy = task_data.copy()
                    if 'id' in task_data_copy:
                        del task_data_copy['id']
                    storage.add_task(
                        task_data_copy['content'],
                        priority=task_data_copy.get('priority', 'medium'),
                        tags=task_data_copy.get('tags'),
                        due_date=task_data_copy.get('due_date'),
                        board=task_data_copy.get('board', 'default')
                    )
                restored_counts['tasks'] = len(data['tasks'])
            
            # Restore journal entries
            if 'journal_entries' in data:
                for entry_data in data['journal_entries']:
                    storage.add_journal_entry(
                        entry_data['text'],
                        tags=entry_data.get('tags'),
                        category=entry_data.get('category')
                    )
                restored_counts['journal_entries'] = len(data['journal_entries'])
            
            # Restore mood entries
            if 'mood_entries' in data:
                for mood_data in data['mood_entries']:
                    storage.add_mood_entry(
                        mood_data['mood'],
                        notes=mood_data.get('notes')
                    )
                restored_counts['mood_entries'] = len(data['mood_entries'])
            
            # Restore goals
            if 'goals' in data:
                for goal_data in data['goals']:
                    storage.add_goal(
                        goal_data['description'],
                        target_date=goal_data.get('target_date')
                    )
                restored_counts['goals'] = len(data['goals'])
            
            progress.update(task, description="Restore complete!")
        
        rprint(f"[green]✅ Backup '{backup_name}' restored successfully![/green]")
        rprint(f"[blue]📊 Restored: {restored_counts.get('tasks', 0)} tasks, {restored_counts.get('journal_entries', 0)} journal entries[/blue]")
        return True
        
    except Exception as e:
        rprint(f"[red]❌ Failed to restore backup: {e}[/red]")
        return False


def auto_backup_check(storage):
    backup_dir = get_backup_dir()
    
    # Check for recent backups
    recent_backups = []
    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=1)
    
    for backup_file in backup_dir.glob("*.json"):
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            created_at = datetime.datetime.fromisoformat(backup_data.get('created_at', ''))
            if created_at > cutoff_time:
                recent_backups.append(backup_file)
        except:
            continue
    
    # Create auto-backup if none in last 24 hours
    if not recent_backups:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"auto_backup_{timestamp}"
        create_backup(storage, backup_name, auto=True)
        return True
    
    return False


def backup_health_check():
    console = Console()
    backup_dir = get_backup_dir()
    
    # Count backups
    json_backups = list(backup_dir.glob("*.json"))
    db_backups = list(backup_dir.glob("*.db"))
    
    # Check disk space
    total_size = sum(f.stat().st_size for f in json_backups + db_backups) / (1024 * 1024)  # MB
    
    # Check backup age
    newest_backup = None
    if json_backups:
        newest_file = max(json_backups, key=lambda f: f.stat().st_mtime)
        newest_backup = datetime.datetime.fromtimestamp(newest_file.stat().st_mtime)
    
    table = Table(title="🏥 Backup Health Check")
    table.add_column("Metric", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="blue")
    
    # Backup count
    backup_count_status = "✅ Good" if len(json_backups) >= 3 else "⚠️ Low" if len(json_backups) >= 1 else "❌ None"
    table.add_row("Backup Count", backup_count_status, f"{len(json_backups)} backups")
    
    # Backup age
    if newest_backup:
        age_hours = (datetime.datetime.now() - newest_backup).total_seconds() / 3600
        age_status = "✅ Recent" if age_hours < 24 else "⚠️ Old" if age_hours < 168 else "❌ Very Old"
        age_text = f"{age_hours:.1f} hours ago"
    else:
        age_status = "❌ None"
        age_text = "No backups found"
    table.add_row("Latest Backup", age_status, age_text)
    
    # Storage usage
    storage_status = "✅ Good" if total_size < 100 else "⚠️ High" if total_size < 500 else "❌ Very High"
    table.add_row("Storage Used", storage_status, f"{total_size:.1f} MB")
    
    # Backup directory
    dir_status = "✅ Exists" if backup_dir.exists() else "❌ Missing"
    table.add_row("Backup Directory", dir_status, str(backup_dir))
    
    console.print(table)
    
    # Recommendations
    recommendations = []
    if len(json_backups) < 3:
        recommendations.append("Create more backups for better safety")
    if newest_backup and (datetime.datetime.now() - newest_backup).days > 7:
        recommendations.append("Create a fresh backup - latest is over a week old")
    if total_size > 100:
        recommendations.append("Consider cleaning up old backups to save space")
    
    if recommendations:
        console.print("\n[yellow]💡 Recommendations:[/yellow]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")


def cleanup_old_backups(days_to_keep=30, max_backups=10):
    console = Console()
    backup_dir = get_backup_dir()
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
    
    # Get all backup files with their creation times
    backup_files = []
    for backup_file in backup_dir.glob("*.json"):
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            created_at = datetime.datetime.fromisoformat(backup_data.get('created_at', ''))
            backup_files.append((backup_file, created_at))
        except:
            # If we can't read the backup, consider it for deletion based on file time
            file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
            backup_files.append((backup_file, file_time))
    
    # Sort by creation time (newest first)
    backup_files.sort(key=lambda x: x[1], reverse=True)
    
    # Determine files to delete
    files_to_delete = []
    
    # Keep at most max_backups files
    if len(backup_files) > max_backups:
        files_to_delete.extend([f[0] for f in backup_files[max_backups:]])
    
    # Also delete files older than cutoff_date (but keep at least 3 recent ones)
    for backup_file, created_at in backup_files[3:]:  # Skip 3 most recent
        if created_at < cutoff_date:
            if backup_file not in files_to_delete:
                files_to_delete.append(backup_file)
    
    if not files_to_delete:
        rprint("[green]✅ No old backups to clean up[/green]")
        return
    
    # Delete files
    deleted_count = 0
    for backup_file in files_to_delete:
        try:
            backup_file.unlink()
            # Also delete corresponding .db file if it exists
            db_file = backup_file.with_suffix('.db')
            if db_file.exists():
                db_file.unlink()
            deleted_count += 1
        except Exception as e:
            rprint(f"[red]Failed to delete {backup_file.name}: {e}[/red]")
    
    rprint(f"[green]🧹 Cleaned up {deleted_count} old backup files[/green]")
