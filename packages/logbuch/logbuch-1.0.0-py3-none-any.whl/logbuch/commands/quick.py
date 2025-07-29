#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/quick.py

import datetime
from rich import print as rprint
from logbuch.commands.mood import get_random_mood


def quick_add_task(storage, content, priority="medium"):
    return storage.add_task(content, priority=priority, board="default")


def quick_add_journal(storage, content):
    return storage.add_journal_entry(content)


def quick_add_mood(storage, mood=None, notes=None):
    if not mood:
        mood = get_random_mood()
        rprint(f"[cyan]Using random mood: {mood}[/cyan]")
    return storage.add_mood_entry(mood, notes)


def quick_daily_checkin(storage):
    from rich.prompt import Prompt, Confirm
    from rich.console import Console
    
    console = Console()
    console.print("\n[bold cyan]🌅 Daily Check-in[/bold cyan]")
    
    # Mood check
    mood = Prompt.ask("How are you feeling today?", default=get_random_mood())
    mood_notes = Prompt.ask("Any notes about your mood?", default="")
    storage.add_mood_entry(mood, mood_notes if mood_notes else None)
    
    # Sleep check
    if Confirm.ask("Did you sleep well?"):
        hours = Prompt.ask("How many hours?", default="8")
        try:
            hours_float = float(hours)
            storage.add_sleep_entry(hours_float)
        except ValueError:
            pass
    
    # Quick task
    if Confirm.ask("Add a quick task for today?"):
        task = Prompt.ask("What do you want to accomplish?")
        storage.add_task(task, priority="medium", board="default")
    
    # Journal prompt
    if Confirm.ask("Add a journal entry?"):
        entry = Prompt.ask("What's on your mind?")
        storage.add_journal_entry(entry)
    
    console.print("\n[green]✨ Daily check-in complete![/green]")


def quick_stats(storage):
    from rich.table import Table
    from rich.console import Console
    
    console = Console()
    
    # Get data
    tasks = storage.get_tasks()
    completed_today = len([t for t in tasks if t.get('completed_at') and 
                          t['completed_at'].startswith(datetime.date.today().isoformat())])
    
    journal_entries = storage.get_journal_entries(limit=100)
    entries_this_week = len([e for e in journal_entries if 
                           datetime.datetime.fromisoformat(e['date'].replace('Z', '+00:00')).date() >= 
                           datetime.date.today() - datetime.timedelta(days=7)])
    
    mood_entries = storage.get_mood_entries(limit=100)
    moods_this_week = len([m for m in mood_entries if 
                          datetime.datetime.fromisoformat(m['date'].replace('Z', '+00:00')).date() >= 
                          datetime.date.today() - datetime.timedelta(days=7)])
    
    table = Table(title="📊 Quick Stats")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Tasks completed today", str(completed_today))
    table.add_row("Journal entries this week", str(entries_this_week))
    table.add_row("Mood entries this week", str(moods_this_week))
    table.add_row("Total tasks", str(len(tasks)))
    
    console.print(table)
