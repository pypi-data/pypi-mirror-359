#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List, Dict, Any
import sqlite3
from datetime import datetime, timedelta

from logbuch.storage import Storage
from logbuch.core.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
def maintenance():
    pass


@maintenance.command()
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without making changes')
@click.option('--force', is_flag=True, help='Skip confirmation prompts')
def cleanup(dry_run: bool, force: bool):
    storage = Storage()
    
    console.print("🧹 [bold bright_blue]Logbuch Database Cleanup[/bold bright_blue]")
    console.print("=" * 50)
    
    cleanup_stats = {
        'duplicate_tasks': 0,
        'invalid_priorities': 0,
        'orphaned_entries': 0,
        'old_completed_tasks': 0
    }
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # 1. Find and remove duplicate tasks
        task1 = progress.add_task("🔍 Scanning for duplicate tasks...", total=None)
        duplicates = find_duplicate_tasks(storage)
        cleanup_stats['duplicate_tasks'] = len(duplicates)
        progress.update(task1, description=f"✅ Found {len(duplicates)} duplicate tasks")
        
        # 2. Fix invalid priorities
        task2 = progress.add_task("🔧 Checking task priorities...", total=None)
        invalid_priorities = find_invalid_priorities(storage)
        cleanup_stats['invalid_priorities'] = len(invalid_priorities)
        progress.update(task2, description=f"✅ Found {len(invalid_priorities)} invalid priorities")
        
        # 3. Find orphaned entries
        task3 = progress.add_task("🔍 Scanning for orphaned entries...", total=None)
        orphaned = find_orphaned_entries(storage)
        cleanup_stats['orphaned_entries'] = len(orphaned)
        progress.update(task3, description=f"✅ Found {len(orphaned)} orphaned entries")
        
        # 4. Find old completed tasks
        task4 = progress.add_task("📅 Checking old completed tasks...", total=None)
        old_completed = find_old_completed_tasks(storage)
        cleanup_stats['old_completed_tasks'] = len(old_completed)
        progress.update(task4, description=f"✅ Found {len(old_completed)} old completed tasks")
    
    # Display cleanup summary
    display_cleanup_summary(cleanup_stats, dry_run)
    
    if not dry_run:
        if not force and not click.confirm("🚀 Proceed with cleanup?"):
            console.print("❌ Cleanup cancelled")
            return
        
        perform_cleanup(storage, duplicates, invalid_priorities, orphaned, old_completed)
        console.print("✅ [bold green]Database cleanup completed![/bold green]")
    else:
        console.print("🔍 [dim]Dry run completed - no changes made[/dim]")


def find_duplicate_tasks(storage: Storage) -> List[Dict[str, Any]]:
    query = """
    SELECT t1.id, t1.title, t1.created_at, COUNT(*) as count
    FROM tasks t1
    JOIN tasks t2 ON t1.title = t2.title 
        AND DATE(t1.created_at) = DATE(t2.created_at)
        AND t1.id != t2.id
    WHERE t1.status != 'deleted'
    GROUP BY t1.title, DATE(t1.created_at)
    HAVING COUNT(*) > 1
    ORDER BY t1.created_at DESC
    """
    
    try:
        result = storage.execute_query(query)
        return [dict(row) for row in result] if result else []
    except Exception as e:
        logger.error(f"Error finding duplicate tasks: {e}")
        return []


def find_invalid_priorities(storage: Storage) -> List[Dict[str, Any]]:
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    
    query = """
    SELECT id, title, priority
    FROM tasks 
    WHERE priority NOT IN ('low', 'medium', 'high', 'urgent')
        AND status != 'deleted'
    ORDER BY created_at DESC
    """
    
    try:
        result = storage.execute_query(query)
        return [dict(row) for row in result] if result else []
    except Exception as e:
        logger.error(f"Error finding invalid priorities: {e}")
        return []


def find_orphaned_entries(storage: Storage) -> List[Dict[str, Any]]:
    query = """
    SELECT 'time_entries' as table_name, id, task_id
    FROM time_entries 
    WHERE task_id NOT IN (SELECT id FROM tasks WHERE status != 'deleted')
    
    UNION ALL
    
    SELECT 'task_dependencies' as table_name, id, task_id
    FROM task_dependencies 
    WHERE task_id NOT IN (SELECT id FROM tasks WHERE status != 'deleted')
        OR depends_on_id NOT IN (SELECT id FROM tasks WHERE status != 'deleted')
    """
    
    try:
        result = storage.execute_query(query)
        return [dict(row) for row in result] if result else []
    except Exception as e:
        logger.error(f"Error finding orphaned entries: {e}")
        return []


def find_old_completed_tasks(storage: Storage, days_old: int = 90) -> List[Dict[str, Any]]:
    cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
    
    query = """
    SELECT id, title, completed_at
    FROM tasks 
    WHERE status = 'completed' 
        AND completed_at < ?
    ORDER BY completed_at ASC
    """
    
    try:
        result = storage.execute_query(query, (cutoff_date,))
        return [dict(row) for row in result] if result else []
    except Exception as e:
        logger.error(f"Error finding old completed tasks: {e}")
        return []


def display_cleanup_summary(stats: Dict[str, int], dry_run: bool):
    table = Table(title="🧹 Cleanup Summary", show_header=True, header_style="bold magenta")
    table.add_column("Issue Type", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Action", style="green")
    
    table.add_row(
        "🔄 Duplicate Tasks", 
        str(stats['duplicate_tasks']),
        "Remove older duplicates" if stats['duplicate_tasks'] > 0 else "None found"
    )
    
    table.add_row(
        "⚠️ Invalid Priorities", 
        str(stats['invalid_priorities']),
        "Reset to 'medium'" if stats['invalid_priorities'] > 0 else "None found"
    )
    
    table.add_row(
        "🔗 Orphaned Entries", 
        str(stats['orphaned_entries']),
        "Remove references" if stats['orphaned_entries'] > 0 else "None found"
    )
    
    table.add_row(
        "📅 Old Completed (90+ days)", 
        str(stats['old_completed_tasks']),
        "Archive or remove" if stats['old_completed_tasks'] > 0 else "None found"
    )
    
    console.print(table)
    
    total_issues = sum(stats.values())
    if total_issues == 0:
        console.print("✨ [bold green]Your database is already clean![/bold green]")
    else:
        action_text = "would be cleaned" if dry_run else "will be cleaned"
        console.print(f"📊 [bold yellow]{total_issues} issues {action_text}[/bold yellow]")


def perform_cleanup(storage: Storage, duplicates: List, invalid_priorities: List, 
                   orphaned: List, old_completed: List):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Clean duplicates
        if duplicates:
            task = progress.add_task("🔄 Removing duplicate tasks...", total=len(duplicates))
            for dup in duplicates:
                try:
                    # Keep the newest, remove older ones
                    storage.execute_query(
                        "UPDATE tasks SET status = 'deleted' WHERE id = ? AND id NOT IN (SELECT MIN(id) FROM tasks WHERE title = ? GROUP BY title)",
                        (dup['id'], dup['title'])
                    )
                    progress.advance(task)
                except Exception as e:
                    logger.error(f"Error removing duplicate task {dup['id']}: {e}")
        
        # Fix invalid priorities
        if invalid_priorities:
            task = progress.add_task("⚠️ Fixing invalid priorities...", total=len(invalid_priorities))
            for invalid in invalid_priorities:
                try:
                    storage.execute_query(
                        "UPDATE tasks SET priority = 'medium' WHERE id = ?",
                        (invalid['id'],)
                    )
                    progress.advance(task)
                except Exception as e:
                    logger.error(f"Error fixing priority for task {invalid['id']}: {e}")
        
        # Remove orphaned entries
        if orphaned:
            task = progress.add_task("🔗 Removing orphaned entries...", total=len(orphaned))
            for orphan in orphaned:
                try:
                    storage.execute_query(
                        f"DELETE FROM {orphan['table_name']} WHERE id = ?",
                        (orphan['id'],)
                    )
                    progress.advance(task)
                except Exception as e:
                    logger.error(f"Error removing orphaned entry {orphan['id']}: {e}")


@maintenance.command()
def stats():
    storage = Storage()
    
    console.print("📊 [bold bright_blue]Logbuch Database Statistics[/bold bright_blue]")
    console.print("=" * 50)
    
    # Get comprehensive stats
    stats = get_database_stats(storage)
    
    # Create stats table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Details", style="dim")
    
    for category, metrics in stats.items():
        table.add_section()
        table.add_row(f"[bold]{category.upper()}[/bold]", "", "")
        for metric, value in metrics.items():
            table.add_row(f"  {metric}", str(value['count']), value.get('details', ''))
    
    console.print(table)


def get_database_stats(storage: Storage) -> Dict[str, Dict[str, Dict[str, Any]]]:
    stats = {
        'tasks': {},
        'productivity': {},
        'data_quality': {},
        'performance': {}
    }
    
    try:
        # Task statistics
        stats['tasks']['Total Tasks'] = {
            'count': storage.execute_query("SELECT COUNT(*) FROM tasks WHERE status != 'deleted'")[0][0],
            'details': 'Active tasks only'
        }
        
        stats['tasks']['Completed Tasks'] = {
            'count': storage.execute_query("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")[0][0]
        }
        
        stats['tasks']['Pending Tasks'] = {
            'count': storage.execute_query("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")[0][0]
        }
        
        # Productivity statistics
        today = datetime.now().date().isoformat()
        stats['productivity']['Tasks Today'] = {
            'count': storage.execute_query("SELECT COUNT(*) FROM tasks WHERE DATE(created_at) = ?", (today,))[0][0]
        }
        
        # Data quality
        stats['data_quality']['Invalid Priorities'] = {
            'count': len(find_invalid_priorities(storage)),
            'details': 'Should be: low, medium, high, urgent'
        }
        
        stats['data_quality']['Duplicate Tasks'] = {
            'count': len(find_duplicate_tasks(storage)),
            'details': 'Same title and date'
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
    
    return stats


@maintenance.command()
@click.option('--backup-path', help='Custom backup file path')
def backup(backup_path: str):
    storage = Storage()
    
    if not backup_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"logbuch_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2(storage.db_path, backup_path)
        
        console.print(f"✅ [bold green]Backup created successfully![/bold green]")
        console.print(f"📁 Location: {backup_path}")
        
        # Show backup info
        import os
        size = os.path.getsize(backup_path)
        console.print(f"💾 Size: {size:,} bytes")
        
    except Exception as e:
        console.print(f"❌ [bold red]Backup failed: {e}[/bold red]")
        logger.error(f"Backup error: {e}")


if __name__ == "__main__":
    maintenance()
