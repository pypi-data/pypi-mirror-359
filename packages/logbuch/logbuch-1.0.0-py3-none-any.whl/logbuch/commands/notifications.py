#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/notifications.py

import datetime
import subprocess
import platform
from rich import print as rprint
from rich.table import Table
from rich.console import Console


def send_system_notification(title, message, urgency="normal"):
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            subprocess.run(["osascript", "-e", script], check=True)
        elif system == "Linux":
            subprocess.run([
                "notify-send", 
                f"--urgency={urgency}",
                title, 
                message
            ], check=True)
        elif system == "Windows":
            # Windows toast notification
            subprocess.run([
                "powershell", 
                "-Command",
                f"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); $template.SelectSingleNode('//text[@id=\"1\"]').AppendChild($template.CreateTextNode('{title}')) | Out-Null; $template.SelectSingleNode('//text[@id=\"2\"]').AppendChild($template.CreateTextNode('{message}')) | Out-Null; $toast = [Windows.UI.Notifications.ToastNotification]::new($template); [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Logbuch').Show($toast)"
            ], check=True)
        return True
    except Exception as e:
        rprint(f"[red]Failed to send notification: {e}[/red]")
        return False


def check_overdue_tasks(storage):
    tasks = storage.get_tasks()
    today = datetime.date.today()
    overdue_tasks = []
    
    for task in tasks:
        if not task.get('done') and task.get('due_date'):
            try:
                due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                if due_date < today:
                    overdue_tasks.append(task)
            except:
                continue
    
    if overdue_tasks:
        count = len(overdue_tasks)
        title = f"⚠️ {count} Overdue Task{'s' if count > 1 else ''}"
        
        if count == 1:
            message = f"'{overdue_tasks[0]['content'][:50]}'"
        else:
            message = f"You have {count} overdue tasks that need attention"
        
        send_system_notification(title, message, "critical")
        return overdue_tasks
    
    return []


def check_due_today(storage):
    tasks = storage.get_tasks()
    today = datetime.date.today()
    due_today = []
    
    for task in tasks:
        if not task.get('done') and task.get('due_date'):
            try:
                due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                if due_date == today:
                    due_today.append(task)
            except:
                continue
    
    if due_today:
        count = len(due_today)
        title = f"📅 {count} Task{'s' if count > 1 else ''} Due Today"
        
        if count == 1:
            message = f"'{due_today[0]['content'][:50]}'"
        else:
            message = f"{count} tasks are due today"
        
        send_system_notification(title, message, "normal")
        return due_today
    
    return []


def daily_checkin_reminder(storage):
    # Check if user has done any activity today
    today = datetime.date.today().isoformat()
    
    # Check recent entries
    journal_entries = storage.get_journal_entries(limit=5)
    mood_entries = storage.get_mood_entries(limit=5)
    
    has_journal_today = any(entry['date'].startswith(today) for entry in journal_entries)
    has_mood_today = any(entry['date'].startswith(today) for entry in mood_entries)
    
    if not has_journal_today and not has_mood_today:
        title = "🌅 Daily Check-in"
        message = "Haven't seen you today! How are you feeling?"
        send_system_notification(title, message, "low")
        return True
    
    return False


def productivity_reminder(storage):
    tasks = storage.get_tasks()
    incomplete_tasks = [t for t in tasks if not t.get('done')]
    high_priority = [t for t in incomplete_tasks if t.get('priority') == 'high']
    
    if len(high_priority) >= 3:
        title = "🔥 High Priority Alert"
        message = f"You have {len(high_priority)} high priority tasks waiting"
        send_system_notification(title, message, "normal")
        return True
    
    return False


def show_notification_status(storage):
    console = Console()
    
    # Check various notification triggers
    overdue = check_overdue_tasks(storage)
    due_today = check_due_today(storage)
    
    table = Table(title="🔔 Notification Status")
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="yellow")
    table.add_column("Action", style="green")
    
    table.add_row("Overdue Tasks", str(len(overdue)), "🚨 Critical" if overdue else "✅ None")
    table.add_row("Due Today", str(len(due_today)), "⚠️ Attention" if due_today else "✅ None")
    
    console.print(table)
    
    # Show details if any issues
    if overdue:
        console.print("\n[red]⚠️ Overdue Tasks:[/red]")
        for task in overdue[:3]:
            console.print(f"  • {task['content']}")
    
    if due_today:
        console.print("\n[yellow]📅 Due Today:[/yellow]")
        for task in due_today[:3]:
            console.print(f"  • {task['content']}")


def smart_reminder_suggestions(storage):
    console = Console()
    
    console.print("[bold cyan]🤖 Smart Reminder Suggestions:[/bold cyan]")
    
    # Analyze patterns
    tasks = storage.get_tasks()
    incomplete = [t for t in tasks if not t.get('done')]
    
    suggestions = []
    
    if len(incomplete) > 15:
        suggestions.append("Consider setting up daily task review reminders")
    
    # Check for tasks without due dates
    no_due_date = [t for t in incomplete if not t.get('due_date')]
    if len(no_due_date) > 5:
        suggestions.append("Add due dates to tasks for better time management")
    
    # Check for old tasks
    old_tasks = []
    cutoff = datetime.date.today() - datetime.timedelta(days=30)
    for task in incomplete:
        if task.get('created_at'):
            try:
                created = datetime.datetime.fromisoformat(task['created_at'].split('T')[0]).date()
                if created < cutoff:
                    old_tasks.append(task)
            except:
                pass
    
    if old_tasks:
        suggestions.append(f"Review {len(old_tasks)} tasks older than 30 days")
    
    # Show suggestions
    for i, suggestion in enumerate(suggestions, 1):
        console.print(f"  {i}. {suggestion}")
    
    if not suggestions:
        console.print("  ✅ Your task management looks great!")


def schedule_reminder(storage, task_id, reminder_time):
    task = None
    tasks = storage.get_tasks()
    
    for t in tasks:
        if t['id'] == task_id:
            task = t
            break
    
    if not task:
        rprint(f"[red]Task {task_id} not found[/red]")
        return False
    
    # For now, just show what would be scheduled
    rprint(f"[green]✅ Reminder scheduled for task: '{task['content']}'[/green]")
    rprint(f"[blue]📅 Reminder time: {reminder_time}[/blue]")
    rprint(f"[yellow]💡 Note: Actual scheduling requires system cron/task scheduler integration[/yellow]")
    
    return True
