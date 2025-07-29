#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import time
from typing import List, Dict

from logbuch.storage import Storage
from logbuch.core.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.command()
@click.option('--skip-intro', is_flag=True, help='Skip the introduction animation')
@click.option('--quick', is_flag=True, help='Quick setup with defaults')
def welcome(skip_intro: bool, quick: bool):
    storage = Storage()
    
    if not skip_intro:
        show_welcome_animation()
    
    console.print()
    console.print("🎉 [bold bright_blue]Welcome to Logbuch![/bold bright_blue]", justify="center")
    console.print("[dim]Your personal productivity logbook[/dim]", justify="center")
    console.print()
    
    if quick:
        quick_setup(storage)
    else:
        interactive_setup(storage)
    
    show_next_steps()


def show_welcome_animation():
    frames = [
        "📖 Logbuch",
        "📖 Logbuch ✨",
        "📖 Logbuch ✨ 🚀",
        "📖 Logbuch ✨ 🚀 💪"
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("🎬 Loading your productivity journey...", total=len(frames))
        
        for frame in frames:
            progress.update(task, description=f"✨ {frame}")
            time.sleep(0.5)
            progress.advance(task)
    
    console.clear()


def interactive_setup(storage: Storage):
    console.print("🔧 [bold]Let's set up your Logbuch![/bold]")
    console.print()
    
    # Step 1: Personal preferences
    setup_personal_preferences(storage)
    
    # Step 2: Create first tasks
    setup_initial_tasks(storage)
    
    # Step 3: Configure features
    setup_features(storage)
    
    console.print("✅ [bold green]Setup completed![/bold green]")


def quick_setup(storage: Storage):
    console.print("⚡ [bold]Quick Setup Mode[/bold]")
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        
        task = progress.add_task("🚀 Setting up Logbuch...", total=4)
        
        # Default preferences
        progress.update(task, description="⚙️ Configuring preferences...")
        set_default_preferences(storage)
        progress.advance(task)
        time.sleep(0.3)
        
        # Sample tasks
        progress.update(task, description="📋 Creating sample tasks...")
        create_sample_tasks(storage)
        progress.advance(task)
        time.sleep(0.3)
        
        # Enable features
        progress.update(task, description="🎮 Enabling features...")
        enable_default_features(storage)
        progress.advance(task)
        time.sleep(0.3)
        
        # Finalize
        progress.update(task, description="✨ Finalizing setup...")
        progress.advance(task)
        time.sleep(0.3)
    
    console.print("⚡ [bold green]Quick setup completed![/bold green]")


def setup_personal_preferences(storage: Storage):
    console.print("👤 [bold bright_cyan]Personal Preferences[/bold bright_cyan]")
    console.print()
    
    # Name
    name = Prompt.ask("What's your name?", default="Productivity Hero")
    
    # Preferred time format
    time_format = Prompt.ask(
        "Preferred time format?", 
        choices=["12h", "24h"], 
        default="24h"
    )
    
    # Default task priority
    default_priority = Prompt.ask(
        "Default task priority?",
        choices=["low", "medium", "high"],
        default="medium"
    )
    
    # Save preferences
    preferences = {
        'user_name': name,
        'time_format': time_format,
        'default_priority': default_priority
    }
    
    save_preferences(storage, preferences)
    
    console.print(f"✅ Welcome, [bold bright_green]{name}[/bold bright_green]!")
    console.print()


def setup_initial_tasks(storage: Storage):
    console.print("📋 [bold bright_cyan]Your First Tasks[/bold bright_cyan]")
    console.print()
    
    if Confirm.ask("Would you like to create some initial tasks?", default=True):
        
        suggested_tasks = [
            "📖 Learn Logbuch basics",
            "🎯 Set up my productivity goals",
            "⚡ Try the shortcuts feature",
            "🎮 Explore gamification features"
        ]
        
        console.print("💡 [dim]Here are some suggested tasks to get you started:[/dim]")
        for i, task in enumerate(suggested_tasks, 1):
            console.print(f"  {i}. {task}")
        
        console.print()
        
        if Confirm.ask("Add these suggested tasks?", default=True):
            for task in suggested_tasks:
                try:
                    storage.add_task(task, priority="medium")
                except Exception as e:
                    logger.error(f"Error adding task: {e}")
            
            console.print("✅ [green]Initial tasks created![/green]")
        
        # Allow custom tasks
        console.print()
        if Confirm.ask("Would you like to add any custom tasks?", default=False):
            while True:
                custom_task = Prompt.ask("Enter a task (or press Enter to finish)", default="")
                if not custom_task:
                    break
                
                try:
                    storage.add_task(custom_task, priority="medium")
                    console.print(f"✅ Added: {custom_task}")
                except Exception as e:
                    console.print(f"❌ Error adding task: {e}")
    
    console.print()


def setup_features(storage: Storage):
    console.print("🎮 [bold bright_cyan]Feature Configuration[/bold bright_cyan]")
    console.print()
    
    features = {
        'gamification': {
            'name': '🎮 Gamification',
            'description': 'XP points, achievements, and level progression',
            'default': True
        },
        'ai_coach': {
            'name': '🧠 AI Coach',
            'description': 'Smart suggestions and productivity insights',
            'default': True
        },
        'commuter_assistant': {
            'name': '🚂 Commuter Assistant',
            'description': 'Train delay checking and travel optimization',
            'default': False
        },
        'ascii_celebrations': {
            'name': '🎉 ASCII Celebrations',
            'description': 'Epic ASCII art for achievements',
            'default': True
        }
    }
    
    enabled_features = {}
    
    for feature_key, feature_info in features.items():
        console.print(f"[bold]{feature_info['name']}[/bold]")
        console.print(f"[dim]{feature_info['description']}[/dim]")
        
        enabled = Confirm.ask(
            f"Enable {feature_info['name']}?", 
            default=feature_info['default']
        )
        
        enabled_features[feature_key] = enabled
        console.print()
    
    # Save feature preferences
    save_feature_preferences(storage, enabled_features)
    
    enabled_count = sum(enabled_features.values())
    console.print(f"✅ [green]{enabled_count} features enabled![/green]")
    console.print()


def show_next_steps():
    console.print("🚀 [bold bright_blue]You're All Set![/bold bright_blue]", justify="center")
    console.print()
    
    next_steps = [
        ("📋 View your tasks", "logbuch list"),
        ("🎯 Add a new task", "logbuch t 'Your task here'"),
        ("📊 Check your dashboard", "logbuch d"),
        ("⚡ See all shortcuts", "logbuch shortcuts"),
        ("🎮 View achievements", "logbuch achievements"),
        ("❓ Get help anytime", "logbuch --help")
    ]
    
    console.print("💡 [bold]Quick Commands to Try:[/bold]")
    console.print()
    
    for description, command in next_steps:
        console.print(f"  {description}")
        console.print(f"  [dim bright_blue]→ {command}[/dim bright_blue]")
        console.print()
    
    # Pro tips
    tips_panel = Panel(
        "[bold bright_yellow]💡 Pro Tips:[/bold bright_yellow]\n\n"
        "• Use [bold]lb[/bold] as a shortcut for logbuch\n"
        "• Try [bold]logbuch toilet 'SUCCESS!'[/bold] for ASCII art\n"
        "• Use [bold]logbuch late[/bold] to check train delays\n"
        "• Run [bold]logbuch cleanup[/bold] to keep your data clean",
        title="🎯 Pro Tips",
        border_style="bright_yellow"
    )
    
    console.print(tips_panel)
    console.print()
    console.print("🎉 [bold green]Happy productivity![/bold green]", justify="center")


def set_default_preferences(storage: Storage):
    preferences = {
        'user_name': 'Productivity Hero',
        'time_format': '24h',
        'default_priority': 'medium',
        'theme': 'default'
    }
    save_preferences(storage, preferences)


def create_sample_tasks(storage: Storage):
    sample_tasks = [
        "📖 Explore Logbuch features",
        "🎯 Set up productivity goals",
        "⚡ Try keyboard shortcuts",
        "🎮 Check out achievements"
    ]
    
    for task in sample_tasks:
        try:
            storage.add_task(task, priority="medium")
        except Exception as e:
            logger.error(f"Error creating sample task: {e}")


def enable_default_features(storage: Storage):
    features = {
        'gamification': True,
        'ai_coach': True,
        'commuter_assistant': False,
        'ascii_celebrations': True
    }
    save_feature_preferences(storage, features)


def save_preferences(storage: Storage, preferences: Dict[str, str]):
    try:
        for key, value in preferences.items():
            storage.execute_query(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                (key, str(value))
            )
    except Exception as e:
        logger.error(f"Error saving preferences: {e}")


def save_feature_preferences(storage: Storage, features: Dict[str, bool]):
    try:
        for feature, enabled in features.items():
            storage.execute_query(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                (f"feature_{feature}", str(enabled))
            )
    except Exception as e:
        logger.error(f"Error saving feature preferences: {e}")


@click.command()
def tour():
    console.print("🎪 [bold bright_blue]Logbuch Feature Tour[/bold bright_blue]", justify="center")
    console.print()
    
    tour_steps = [
        {
            'title': '📋 Task Management',
            'description': 'Create, organize, and complete tasks with ease',
            'commands': ['logbuch t "My task"', 'logbuch list', 'logbuch complete 1']
        },
        {
            'title': '📊 Dashboard',
            'description': 'Get an overview of your productivity',
            'commands': ['logbuch d', 'logbuch stats']
        },
        {
            'title': '🎮 Gamification',
            'description': 'Earn XP, unlock achievements, level up!',
            'commands': ['logbuch achievements', 'logbuch level']
        },
        {
            'title': '🧠 AI Coach',
            'description': 'Get smart suggestions and insights',
            'commands': ['logbuch coach', 'logbuch suggestions']
        },
        {
            'title': '⚡ Shortcuts',
            'description': 'Lightning-fast productivity commands',
            'commands': ['logbuch shortcuts', 'logbuch s']
        }
    ]
    
    for i, step in enumerate(tour_steps, 1):
        console.print(f"[bold bright_cyan]Step {i}: {step['title']}[/bold bright_cyan]")
        console.print(f"[dim]{step['description']}[/dim]")
        console.print()
        
        console.print("[bold]Try these commands:[/bold]")
        for cmd in step['commands']:
            console.print(f"  [bright_blue]→ {cmd}[/bright_blue]")
        
        console.print()
        
        if i < len(tour_steps):
            if not Confirm.ask("Ready for the next step?", default=True):
                break
            console.print()
    
    console.print("🎉 [bold green]Tour completed! You're now a Logbuch pro![/bold green]")


if __name__ == "__main__":
    welcome()
