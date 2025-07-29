#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/bulk.py

from rich import print as rprint
from rich.prompt import Confirm
from rich.console import Console


def bulk_complete_tasks(storage, task_ids):
    completed = []
    failed = []
    
    for task_id in task_ids:
        task = storage.complete_task(task_id)
        if task:
            completed.append(task)
        else:
            failed.append(task_id)
    
    if completed:
        rprint(f"[green]✅ Completed {len(completed)} tasks[/green]")
        for task in completed:
            rprint(f"  • {task['content']}")
    
    if failed:
        rprint(f"[red]❌ Failed to complete {len(failed)} tasks: {', '.join(failed)}[/red]")


def bulk_delete_tasks(storage, task_ids, confirm=True):
    if confirm and not Confirm.ask(f"Delete {len(task_ids)} tasks?"):
        rprint("[yellow]Operation cancelled[/yellow]")
        return
    
    deleted = []
    failed = []
    
    for task_id in task_ids:
        task = storage.delete_task(task_id)
        if task:
            deleted.append(task)
        else:
            failed.append(task_id)
    
    if deleted:
        rprint(f"[green]🗑️ Deleted {len(deleted)} tasks[/green]")
    
    if failed:
        rprint(f"[red]❌ Failed to delete {len(failed)} tasks: {', '.join(failed)}[/red]")


def bulk_move_tasks(storage, task_ids, target_board):
    moved = []
    failed = []
    
    for task_id in task_ids:
        task = storage.move_task(task_id, target_board)
        if task:
            moved.append(task)
        else:
            failed.append(task_id)
    
    if moved:
        rprint(f"[green]📋 Moved {len(moved)} tasks to '{target_board}'[/green]")
    
    if failed:
        rprint(f"[red]❌ Failed to move {len(failed)} tasks: {', '.join(failed)}[/red]")


def bulk_add_tasks(storage, tasks_data, board="default"):
    added = []
    
    for task_data in tasks_data:
        if isinstance(task_data, str):
            # Simple string task
            task = storage.add_task(task_data, board=board)
            added.append(task)
        elif isinstance(task_data, dict):
            # Task with metadata
            task = storage.add_task(
                task_data.get('content', ''),
                priority=task_data.get('priority', 'medium'),
                tags=task_data.get('tags'),
                due_date=task_data.get('due_date'),
                board=task_data.get('board', board)
            )
            added.append(task)
    
    rprint(f"[green]✨ Added {len(added)} tasks[/green]")
    return added


def cleanup_completed_tasks(storage, days_old=30):
    import datetime
    
    cutoff_date = datetime.date.today() - datetime.timedelta(days=days_old)
    tasks = storage.get_tasks()
    
    old_completed = [
        task for task in tasks 
        if task.get('done') and task.get('completed_at') and
        datetime.datetime.fromisoformat(task['completed_at'].split('T')[0]).date() < cutoff_date
    ]
    
    if not old_completed:
        rprint("[yellow]No old completed tasks to clean up[/yellow]")
        return
    
    if Confirm.ask(f"Delete {len(old_completed)} completed tasks older than {days_old} days?"):
        for task in old_completed:
            storage.delete_task(task['id'])
        rprint(f"[green]🧹 Cleaned up {len(old_completed)} old completed tasks[/green]")
    else:
        rprint("[yellow]Cleanup cancelled[/yellow]")


def smart_task_suggestions(storage):
    console = Console()
    tasks = storage.get_tasks()
    
    # Analyze patterns
    incomplete_tasks = [t for t in tasks if not t.get('done')]
    overdue_tasks = []
    high_priority_tasks = [t for t in incomplete_tasks if t.get('priority') == 'high']
    
    # Check for overdue tasks
    import datetime
    today = datetime.date.today()
    for task in incomplete_tasks:
        if task.get('due_date'):
            try:
                due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                if due_date < today:
                    overdue_tasks.append(task)
            except:
                pass
    
    console.print("[bold cyan]🤖 Smart Suggestions[/bold cyan]")
    
    if overdue_tasks:
        console.print(f"[red]⚠️ You have {len(overdue_tasks)} overdue tasks[/red]")
        for task in overdue_tasks[:3]:
            console.print(f"  • {task['content']}")
    
    if high_priority_tasks:
        console.print(f"[yellow]🔥 {len(high_priority_tasks)} high priority tasks need attention[/yellow]")
        for task in high_priority_tasks[:3]:
            console.print(f"  • {task['content']}")
    
    if len(incomplete_tasks) > 20:
        console.print("[yellow]📋 Consider breaking down large tasks or archiving old ones[/yellow]")
    
    # Suggest daily tasks if it's morning
    current_hour = datetime.datetime.now().hour
    if 6 <= current_hour <= 10:
        console.print("[cyan]🌅 Good morning! Consider adding your daily tasks[/cyan]")
