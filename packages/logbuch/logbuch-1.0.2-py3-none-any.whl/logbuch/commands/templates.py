#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/templates.py

from rich import print as rprint
from rich.table import Table
from rich.console import Console


def get_task_templates():
    return {
        'work': [
            "Review emails and respond to urgent ones",
            "Attend team standup meeting",
            "Complete project documentation",
            "Code review for team members",
            "Plan next sprint tasks"
        ],
        'personal': [
            "Exercise for 30 minutes",
            "Read for 20 minutes",
            "Call family/friends",
            "Organize workspace",
            "Plan meals for the week"
        ],
        'health': [
            "Drink 8 glasses of water",
            "Take vitamins",
            "Go for a walk",
            "Meditate for 10 minutes",
            "Stretch or do yoga"
        ],
        'learning': [
            "Watch educational video",
            "Practice coding problem",
            "Read technical article",
            "Take online course lesson",
            "Review notes from yesterday"
        ],
        'creative': [
            "Write in journal",
            "Sketch or draw something",
            "Take photos",
            "Write a poem or story",
            "Learn a new song"
        ]
    }


def get_journal_templates():
    return {
        'daily': [
            "What am I grateful for today?",
            "What did I learn today?",
            "What challenged me today?",
            "What made me happy today?",
            "What do I want to improve tomorrow?"
        ],
        'reflection': [
            "What went well this week?",
            "What could I have done differently?",
            "What are my priorities for next week?",
            "How am I feeling about my progress?",
            "What insights did I gain?"
        ],
        'goals': [
            "What progress did I make on my goals?",
            "What obstacles am I facing?",
            "What support do I need?",
            "How can I adjust my approach?",
            "What small step can I take tomorrow?"
        ]
    }


def show_templates(template_type='task'):
    console = Console()
    
    if template_type == 'task':
        templates = get_task_templates()
        title = "📋 Task Templates"
    else:
        templates = get_journal_templates()
        title = "📝 Journal Templates"
    
    for category, items in templates.items():
        table = Table(title=f"{title} - {category.title()}")
        table.add_column("Template", style="cyan")
        
        for item in items:
            table.add_row(item)
        
        console.print(table)
        console.print()


def add_template_tasks(storage, category, board="default"):
    templates = get_task_templates()
    
    if category not in templates:
        rprint(f"[red]Template category '{category}' not found[/red]")
        return
    
    added_count = 0
    for task_content in templates[category]:
        storage.add_task(task_content, priority="medium", board=board)
        added_count += 1
    
    rprint(f"[green]Added {added_count} tasks from '{category}' template[/green]")


def create_custom_template(storage, name, tasks):
    # This would require extending the storage to handle custom templates
    # For now, just show what would be saved
    rprint(f"[cyan]Custom template '{name}' would include:[/cyan]")
    for i, task in enumerate(tasks, 1):
        rprint(f"  {i}. {task}")
