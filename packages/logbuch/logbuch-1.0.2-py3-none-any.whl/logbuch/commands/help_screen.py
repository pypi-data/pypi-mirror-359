#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/help_screen.py

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich import box

def display_help_screen():
    console = Console()
    
    # Main title with tagline
    title_text = Text()
    title_text.append("🚀 LOKBUCH", style="bold bright_cyan")
    title_text.append(" - The Ultimate Productivity Platform\n", style="bold white")
    title_text.append("AI-Powered • Gamified • Revolutionary", style="dim bright_yellow")
    
    console.print(Panel(
        Align.center(title_text),
        box=box.DOUBLE,
        border_style="bright_cyan",
        padding=(1, 2)
    ))
    
    # Revolutionary features showcase
    features_text = Text()
    features_text.append("🌟 REVOLUTIONARY FEATURES\n", style="bold bright_magenta")
    features_text.append("🧠 AI Productivity Coach", style="bold cyan")
    features_text.append(" - Your personal success strategist\n", style="white")
    features_text.append("🎮 Gamification Engine", style="bold green")
    features_text.append(" - XP, levels, achievements, daily challenges\n", style="white")
    features_text.append("🌍 Smart Environment", style="bold yellow")
    features_text.append(" - Context-aware productivity optimization\n", style="white")
    features_text.append("🚁 Productivity Autopilot", style="bold orange1")
    features_text.append(" - Hands-free productivity management\n", style="white")
    features_text.append("👥 Social Network", style="bold magenta")
    features_text.append(" - Accountability buddies and team challenges\n", style="white")
    features_text.append("🔗 Professional Integrations", style="bold blue")
    features_text.append(" - GitHub, Cloud Sync, Webhooks, Voice AI", style="white")
    
    console.print(Panel(features_text, title="✨ What Makes Logbuch Special", border_style="bright_magenta"))
    
    # Quick start commands in columns
    quick_start_left = Text()
    quick_start_left.append("🧠 AI COACHING\n", style="bold cyan")
    quick_start_left.append("logbuch coach", style="bright_cyan")
    quick_start_left.append("     # Daily AI insights\n", style="dim white")
    quick_start_left.append("logbuch insights", style="bright_cyan")
    quick_start_left.append("   # Deep analysis\n", style="dim white")
    quick_start_left.append("logbuch patterns", style="bright_cyan")
    quick_start_left.append("   # Discover patterns\n", style="dim white")
    
    quick_start_middle = Text()
    quick_start_middle.append("🎮 GAMIFICATION\n", style="bold green")
    quick_start_middle.append("logbuch profile", style="bright_green")
    quick_start_middle.append("    # Your progress\n", style="dim white")
    quick_start_middle.append("logbuch ach", style="bright_green")
    quick_start_middle.append("        # Achievements\n", style="dim white")
    quick_start_middle.append("logbuch chal", style="bright_green")
    quick_start_middle.append("       # Daily challenges\n", style="dim white")
    
    quick_start_right = Text()
    quick_start_right.append("🚀 REVOLUTIONARY\n", style="bold bright_magenta")
    quick_start_right.append("logbuch env", style="bright_yellow")
    quick_start_right.append("        # Smart environment\n", style="dim white")
    quick_start_right.append("logbuch auto", style="bright_orange1")
    quick_start_right.append("       # Productivity autopilot\n", style="dim white")
    quick_start_right.append("logbuch social", style="bright_magenta")
    quick_start_right.append("     # Social network\n", style="dim white")
    
    console.print(Panel(
        Columns([quick_start_left, quick_start_middle, quick_start_right], equal=True),
        title="🚀 Quick Start - Revolutionary Features",
        border_style="bright_yellow"
    ))
    
    # Core productivity commands
    core_commands = Table(show_header=True, header_style="bold bright_white", box=box.ROUNDED)
    core_commands.add_column("Command", style="bright_cyan", width=20)
    core_commands.add_column("Shortcut", style="bright_yellow", width=8)
    core_commands.add_column("Description", style="white", width=40)
    
    # Add core commands
    core_commands.add_row("logbuch task", "t", "📝 Advanced task management with XP rewards")
    core_commands.add_row("logbuch journal", "j", "📖 Journal with mood tracking and AI insights")
    core_commands.add_row("logbuch dashboard", "d", "📊 Comprehensive productivity overview")
    core_commands.add_row("logbuch search", "/", "🔍 Smart search across all your data")
    core_commands.add_row("logbuch kanban", "k", "📋 Visual kanban board interface")
    core_commands.add_row("logbuch time", "", "⏱️ Advanced time tracking and analytics")
    
    console.print(Panel(core_commands, title="📝 Core Productivity Commands", border_style="bright_blue"))
    
    # Getting started section
    getting_started = Text()
    getting_started.append("🎯 GET STARTED IN 30 SECONDS\n\n", style="bold bright_green")
    getting_started.append("1. ", style="bold bright_yellow")
    getting_started.append("logbuch task \"My first productive task\" --priority high\n", style="bright_cyan")
    getting_started.append("2. ", style="bold bright_yellow")
    getting_started.append("logbuch task --complete 1", style="bright_cyan")
    getting_started.append("  # Watch the XP magic! ✨\n", style="dim bright_green")
    getting_started.append("3. ", style="bold bright_yellow")
    getting_started.append("logbuch coach", style="bright_cyan")
    getting_started.append("                # Get AI insights\n", style="dim bright_green")
    getting_started.append("4. ", style="bold bright_yellow")
    getting_started.append("logbuch profile", style="bright_cyan")
    getting_started.append("              # See your progress\n", style="dim bright_green")
    
    console.print(Panel(getting_started, title="🚀 Quick Start Guide", border_style="bright_green"))
    
    # Value proposition
    value_prop = Text()
    value_prop.append("💎 WHY LOKBUCH?\n", style="bold bright_magenta")
    value_prop.append("• ", style="bright_yellow")
    value_prop.append("First AI-powered CLI productivity platform with autopilot\n", style="white")
    value_prop.append("• ", style="bright_yellow")
    value_prop.append("Smart environment that adapts to your context automatically\n", style="white")
    value_prop.append("• ", style="bright_yellow")
    value_prop.append("Social productivity network with accountability buddies\n", style="white")
    value_prop.append("• ", style="bright_yellow")
    value_prop.append("Gamification that makes productivity genuinely addictive\n", style="white")
    value_prop.append("• ", style="bright_yellow")
    value_prop.append("Revolutionary features that define the future of productivity", style="white")
    
    console.print(Panel(value_prop, title="🌟 The Future of Productivity", border_style="bright_magenta"))
    
    # Footer with help
    footer = Text()
    footer.append("💡 Need help? ", style="dim white")
    footer.append("logbuch --help", style="bright_cyan")
    footer.append(" | More commands: ", style="dim white")
    footer.append("logbuch <command> --help", style="bright_cyan")
    footer.append("\n🌐 GitHub: ", style="dim white")
    footer.append("github.com/yourusername/logbuch", style="bright_blue")
    footer.append(" | 📧 Support: ", style="dim white")
    footer.append("hello@logbuch.com", style="bright_blue")
    
    console.print(Panel(
        Align.center(footer),
        border_style="dim white"
    ))
    
    # Call to action
    cta = Text()
    cta.append("🎯 Ready to revolutionize your productivity? Start with: ", style="bold white")
    cta.append("logbuch coach", style="bold bright_cyan")
    
    console.print()
    console.print(Align.center(cta))
    console.print()


def display_options_help():
    console = Console()
    
    # Title
    title = Text("🌻 Logbuch Command Options", style="bold bright_cyan")
    console.print(Panel(Align.center(title), border_style="bright_cyan"))
    
    # Options table
    options_table = Table(show_header=True, header_style="bold bright_white", box=box.ROUNDED)
    options_table.add_column("Option", style="bright_cyan", width=25)
    options_table.add_column("Description", style="white", width=50)
    
    options_table.add_row("--version", "Show version and exit")
    options_table.add_row("--backup", "Create a backup of your data")
    options_table.add_row("--restore <path>", "Restore from backup (use 'latest' for most recent)")
    options_table.add_row("--export <path>", "Export your data to a file")
    options_table.add_row("--import-file <path>", "Import data from a file")
    options_table.add_row("--info", "Show database information and statistics")
    options_table.add_row("--format [json|markdown]", "Format for export/import operations")
    options_table.add_row("--help", "Show this help message")
    
    console.print(options_table)
    
    # Examples
    examples = Text()
    examples.append("📚 EXAMPLES\n", style="bold bright_yellow")
    examples.append("logbuch --backup", style="bright_cyan")
    examples.append("                    # Create backup\n", style="dim white")
    examples.append("logbuch --restore latest", style="bright_cyan")
    examples.append("           # Restore latest backup\n", style="dim white")
    examples.append("logbuch --export data.json", style="bright_cyan")
    examples.append("         # Export to JSON\n", style="dim white")
    examples.append("logbuch --info", style="bright_cyan")
    examples.append("                     # Show statistics", style="dim white")
    
    console.print(Panel(examples, title="💡 Usage Examples", border_style="bright_yellow"))
