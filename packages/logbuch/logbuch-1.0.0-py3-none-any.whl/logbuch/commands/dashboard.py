#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/dashboard.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import print as rprint
import datetime


def display_dashboard(storage):
    console = Console()
    
    # Get current date info
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    
    # Get data
    tasks = storage.get_tasks()
    incomplete_tasks = [t for t in tasks if not t.get('done', False)]
    completed_tasks = [t for t in tasks if t.get('done', False)]
    
    journal_entries = storage.get_journal_entries(limit=5)
    mood_entries = storage.get_mood_entries(limit=5)
    sleep_entries = storage.get_sleep_entries(limit=5)
    goals = storage.get_goals()
    active_goals = [g for g in goals if not g.get('completed', False)]
    
    # Create panels
    panels = []
    
    # Tasks overview
    task_text = Text()
    task_text.append(f"📋 Total Tasks: {len(tasks)}\n", style="bold")
    task_text.append(f"✅ Completed: {len(completed_tasks)}\n", style="green")
    task_text.append(f"⏳ Pending: {len(incomplete_tasks)}\n", style="yellow")
    
    if incomplete_tasks:
        task_text.append("\nNext Tasks:\n", style="bold cyan")
        for task in incomplete_tasks[:3]:
            priority_color = {"high": "red", "medium": "yellow", "low": "green"}.get(
                task.get('priority', 'medium'), "white"
            )
            task_text.append(f"• {task['content'][:30]}{'...' if len(task['content']) > 30 else ''}\n", 
                           style=priority_color)
    
    panels.append(Panel(task_text, title="📋 Tasks", border_style="blue"))
    
    # Recent activity
    activity_text = Text()
    if journal_entries:
        activity_text.append("📝 Recent Journal:\n", style="bold cyan")
        for entry in journal_entries[:2]:
            date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%m-%d")
            content = entry['text'][:40] + '...' if len(entry['text']) > 40 else entry['text']
            activity_text.append(f"{date_str}: {content}\n", style="dim")
    
    if mood_entries:
        activity_text.append("\n😊 Recent Moods:\n", style="bold cyan")
        for entry in mood_entries[:3]:
            date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%m-%d")
            activity_text.append(f"{date_str}: {entry['mood']}\n", style="dim")
    
    panels.append(Panel(activity_text, title="📈 Recent Activity", border_style="green"))
    
    # Goals overview
    goals_text = Text()
    if active_goals:
        goals_text.append(f"🎯 Active Goals: {len(active_goals)}\n", style="bold")
        for goal in active_goals[:3]:
            progress = goal.get('progress', 0)
            progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
            goals_text.append(f"• {goal['description'][:25]}{'...' if len(goal['description']) > 25 else ''}\n", style="white")
            goals_text.append(f"  {progress_bar} {progress}%\n", style="cyan")
    else:
        goals_text.append("No active goals\n", style="dim")
        goals_text.append("Add a goal: logbuch goal \"Your goal\"", style="dim cyan")
    
    panels.append(Panel(goals_text, title="🎯 Goals", border_style="magenta"))
    
    # Health overview
    health_text = Text()
    if sleep_entries:
        recent_sleep = sleep_entries[0]
        avg_sleep = sum(entry['hours'] for entry in sleep_entries[:7]) / min(len(sleep_entries), 7)
        health_text.append(f"😴 Last Sleep: {recent_sleep['hours']}h\n", style="blue")
        health_text.append(f"📊 7-day Avg: {avg_sleep:.1f}h\n", style="cyan")
    else:
        health_text.append("No sleep data\n", style="dim")
    
    if mood_entries:
        recent_mood = mood_entries[0]['mood']
        health_text.append(f"\n😊 Current Mood: {recent_mood}\n", style="yellow")
    
    panels.append(Panel(health_text, title="💪 Health", border_style="yellow"))
    
    # Display dashboard
    console.print(f"\n[bold cyan]📊 Logbuch Dashboard - {today.strftime('%A, %B %d, %Y')}[/bold cyan]\n")
    console.print(Columns(panels, equal=True, expand=True))
    
    # Quick actions
    console.print("\n[bold]Quick Actions:[/bold]")
    console.print("• Add task: [cyan]logbuch task \"Task description\"[/cyan]")
    console.print("• Add journal: [cyan]logbuch journal \"Your thoughts\"[/cyan]")
    console.print("• Track mood: [cyan]logbuch mood happy[/cyan] or [cyan]logbuch mood --random[/cyan]")
    console.print("• View kanban: [cyan]logbuch kanban show[/cyan]")
