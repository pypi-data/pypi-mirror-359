#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/cli.py

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path
import datetime

# Simple base command class for compatibility
class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
    
    def execute(self, **kwargs):
        return True

class CommandContext:
    @classmethod
    def create(cls):
        from logbuch.storage import Storage
        from logbuch.core.config import get_config
        
        context = type('Context', (), {})()
        context.storage = Storage()
        context.config = get_config()
        context.console = Console()
        return context

from logbuch.storage import Storage
from logbuch.commands.task import (
    add_task,
    list_tasks,
    complete_task,
    move_task,
    delete_task,
)
from logbuch.commands.journal import (
    add_journal_entry,
    list_journal_entries,
    delete_journal_entry,
)
from logbuch.commands.calendar import display_calendar
from logbuch.commands.mood import add_mood_entry, list_mood_entries, get_random_mood, get_random_moods
from logbuch.commands.sleep import add_sleep_entry, list_sleep_entries
from logbuch.commands.goal import (
    add_goal,
    update_goal_progress,
    list_goals,
    delete_goal,
)
from logbuch.commands.kanban import kanban
from logbuch.commands.week import week_command
from logbuch.commands.time import (
    start_time_tracking,
    stop_time_tracking,
    add_time_entry,
    list_time_entries,
    get_current_tracking,
    delete_time_entry,
)
from logbuch.commands.help_screen import display_help_screen, display_options_help
from logbuch.commands.dashboard import display_dashboard
from logbuch.commands.quick import quick_add_task, quick_add_journal, quick_add_mood, quick_daily_checkin, quick_stats
from logbuch.commands.templates import show_templates, add_template_tasks
from logbuch.commands.bulk import bulk_complete_tasks, bulk_delete_tasks, bulk_move_tasks, cleanup_completed_tasks, smart_task_suggestions
from logbuch.commands.search import smart_search, display_search_results, filter_by_date_range, get_popular_tags
from logbuch.commands.notifications import (
    check_overdue_tasks, check_due_today, daily_checkin_reminder, 
    show_notification_status, smart_reminder_suggestions, schedule_reminder,
    send_system_notification
)
import datetime
# Import integrations with error handling
try:
    from logbuch.commands.integrations import (
        GitHubGistCommand, SmartSuggestionsCommand, CloudSyncCommand, WebhookCommand
    )
    INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    INTEGRATIONS_AVAILABLE = False
    INTEGRATIONS_ERROR = str(e)

# Import perfection modules
try:
    from logbuch.commands.maintenance import maintenance
    from logbuch.commands.onboarding import welcome, tour
    from logbuch.core.error_handling import graceful_shutdown, error_handler
    from logbuch.core.performance import perf_monitor
    PERFECTION_MODULES_AVAILABLE = True
except ImportError as e:
    PERFECTION_MODULES_AVAILABLE = False
    print(f"⚠️ Some perfection modules not available: {e}")
    
    # Create dummy decorator if not available
    def graceful_shutdown(func):
        return func

from logbuch.commands.gamification import (
    ProfileCommand, AchievementsCommand, ChallengesCommand, LeaderboardCommand
)
from logbuch.commands.ai_coach import (
    CoachCommand, InsightsCommand, PatternsCommand, CoachStatsCommand
)
# Import revolutionary features
try:
    from logbuch.commands.revolutionary_features import (
        SmartEnvironmentCommand, AutopilotCommand, SocialCommand
    )
    REVOLUTIONARY_AVAILABLE = True
except ImportError as e:
    REVOLUTIONARY_AVAILABLE = False
    REVOLUTIONARY_ERROR = str(e)

# Import final killer features
try:
    from logbuch.commands.final_features import (
        QuickCaptureCommand, WeatherCommand
    )
    FINAL_FEATURES_AVAILABLE = True
except ImportError as e:
    FINAL_FEATURES_AVAILABLE = False
    FINAL_FEATURES_ERROR = str(e)

# Import commuter assistant (dream feature!)
try:
    from logbuch.commands.commuter_commands import (
        CommuterCommand, CommuteSetupCommand
    )
    COMMUTER_AVAILABLE = True
except ImportError as e:
    COMMUTER_AVAILABLE = False
    COMMUTER_ERROR = str(e)

# Import toilet command (ASCII art generator!)
try:
    from logbuch.commands.toilet_command import ToiletCommand
    TOILET_AVAILABLE = True
except ImportError as e:
    TOILET_AVAILABLE = False
    TOILET_ERROR = str(e)
from logbuch.features.gamification import GamificationEngine, display_rewards
from logbuch.features.ai_coach import AIProductivityCoach

class CustomGroup(click.Group):
    def format_commands(self, ctx, formatter):
        # Don't show commands when --help is used
        if "--help" in ctx.args or "-h" in ctx.args:
            return

        cmds = []

        for cmd in cmds:
            formatter.write_text(cmd)

# Initialize console
console = Console()


def show_epic_logo():
    import subprocess
    import shutil
    import os
    
    try:
        # Check if toilet command is available and if we're in a proper terminal
        if shutil.which('toilet') and os.isatty(1):
            # Try the epic version first (without --metal to avoid ANSI issues)
            result = subprocess.run([
                'toilet', 
                '--directory', 'figlet-fonts', 
                '-f', 'speed.flf', 
                'Logbuch'
            ], capture_output=True, text=True, check=True)
            
            console.print("📖 [bold bright_blue]Logbuch - Think Locally, Act Globally[/bold bright_blue]")
            console.print("=" * 60, style="bright_blue")
            # Print the clean ASCII art
            print(result.stdout)
            console.print("=" * 60, style="bright_blue")
            console.print("🚀 [bold]The Ultimate AI-Powered CLI Productivity Platform[/bold]")
            console.print("📖 [italic]Your personal productivity logbook[/italic]")
            console.print("⚡ [bold bright_green]Built for speed, designed for excellence[/bold bright_green]")
            console.print()
            console.print("💡 [dim]Type 'logbuch --help' for commands or 'logbuch shortcuts' for quick reference[/dim]")
            
        else:
            # Fallback to built-in ASCII art
            show_fallback_logo()
            
    except Exception as e:
        # Fallback if toilet command fails
        show_fallback_logo()

def show_fallback_logo():
    console.print()
    console.print("📖 [bold bright_blue]Logbuch - Think Locally, Act Globally[/bold bright_blue]", justify="center")
    console.print("=" * 60, style="bright_blue", justify="center")
    console.print()
    
    # Epic ASCII art using built-in characters
    ascii_art = """
██      ██████   ██████  ██████  ██    ██  ██████ ██   ██ 
██     ██    ██ ██       ██   ██ ██    ██ ██      ██   ██ 
██     ██    ██ ██   ███ ██████  ██    ██ ██      ███████ 
██     ██    ██ ██    ██ ██   ██ ██    ██ ██      ██   ██ 
██████  ██████   ██████  ██████   ██████   ██████ ██   ██ 
"""
    
    console.print(ascii_art, style="bold bright_blue", justify="center")
    console.print()
    console.print("🚀 [bold]The Ultimate AI-Powered CLI Productivity Platform[/bold]", justify="center")
    console.print("📖 [italic]Your personal productivity logbook[/italic]", justify="center")
    console.print("⚡ [bold bright_green]Built for speed, designed for excellence[/bold bright_green]", justify="center")
    console.print()
    console.print("💡 [dim]Type 'logbuch --help' for commands or 'logbuch shortcuts' for quick reference[/dim]", justify="center")
    console.print()


@click.group(cls=CustomGroup, invoke_without_command=True)
@click.version_option()
@click.option("--backup", is_flag=True, help="Create a backup of the database")
@click.option("--restore", help='Restore from backup (specify "latest" or path)')
@click.option("--export", help="Export data to file (specify path)")
@click.option("--import-file", help="Import data from file")
@click.option("--info", is_flag=True, help="Show basic database information")
@click.option(
    "--format",
    type=click.Choice(["json", "markdown"]),
    default="json",
    help="Format for export/import",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
@graceful_shutdown
def cli(ctx, backup, restore, export, import_file, info, format, verbose):
    # Configure logging based on verbose flag FIRST
    if verbose:
        import os
        os.environ['LOKBUCH_VERBOSE'] = '1'
    else:
        import os
        os.environ['LOKBUCH_VERBOSE'] = '0'
    
    # Check if --help was explicitly used
    if '--help' in ctx.args or '-h' in ctx.args:
        display_options_help()
        return
        
    # If no subcommand is provided and no options are specified, show EPIC LOGO!
    if ctx.invoked_subcommand is None and not any(
        [backup, restore, export, import_file, info]
    ):
        show_epic_logo()
        return
        
    # Handle other options
    if ctx.invoked_subcommand is None and any(
        [backup, restore, export, import_file, info]
    ):
        # Check for first-time user experience
        try:
            from logbuch.commands.onboarding import check_first_run
            if check_first_run():
                return  # Onboarding was shown
        except ImportError:
            pass  # Onboarding not available
        
        display_help_screen()
        return

    # Handle database operations if specified
    if backup or restore or export or import_file or info:
        storage = Storage()

        if backup:
            backup_path = storage._create_backup()
            if backup_path:
                rprint(f"[green]Backup created: {backup_path}[/green]")
            else:
                rprint("[red]Error creating backup[/red]")

        elif restore:
            if restore.lower() == "latest":
                success = storage.restore_from_backup()
            else:
                success = storage.restore_from_backup(restore)

            if success:
                rprint("[green]Database restored successfully[/green]")
            else:
                rprint("[red]Error restoring database[/red]")

        elif export:
            data = storage.export_data(format=format)
            if data:
                export_path = Path(export)

                try:
                    with open(export_path, "w") as f:
                        f.write(data)
                    rprint(f"[green]Data exported to: {export_path}[/green]")
                except Exception as e:
                    rprint(f"[red]Error writing export file: {e}[/red]")
            else:
                rprint("[red]Error exporting data[/red]")

        elif import_file:
            import_path = Path(import_file)
            if not import_path.exists():
                rprint(f"[red]Import file not found: {import_path}[/red]")
                return

            try:
                with open(import_path, "r") as f:
                    data = f.read()

                extension = import_path.suffix.lower()
                if extension == ".json":
                    import_format = "json"
                elif extension in [".md", ".markdown"]:
                    import_format = "markdown"
                else:
                    import_format = format

                success = storage.import_data(data, format=import_format)
                if success:
                    rprint(
                        f"[green]Data imported successfully from: {import_path}[/green]"
                    )
                else:
                    rprint("[red]Error importing data[/red]")
            except Exception as e:
                rprint(f"[red]Error reading import file: {e}[/red]")

        elif info:
            home_dir = Path.home()
            default_db_path = home_dir / ".logbuch" / "logbuch.db"
            backup_dir = home_dir / ".logbuch" / "backups"

            # Count backups
            backup_count = (
                len(list(backup_dir.glob("logbuch-*.db"))) if backup_dir.exists() else 0
            )

            # Database size
            db_size = (
                default_db_path.stat().st_size / 1024 if default_db_path.exists() else 0
            )

            # Count entries
            journal_entries = len(storage.get_journal_entries())
            tasks_active = len(storage.get_tasks())
            tasks_completed = len(storage.get_tasks(show_completed=True)) - tasks_active

            # Display in a nicer format
            table = Table(title="Database Information")
            table.add_column("Property", style="blue")
            table.add_column("Value")

            table.add_row("Database Path", str(default_db_path))
            table.add_row("Database Size", f"{db_size:.2f} KB")
            table.add_row("Backup Directory", str(backup_dir))
            table.add_row("Number of Backups", str(backup_count))
            table.add_row("Journal Entries", str(journal_entries))
            table.add_row("Active Tasks", str(tasks_active))
            table.add_row("Completed Tasks", str(tasks_completed))

            console.print(table)

        # Do not continue to subcommand after handling database operations
        return


# Task commands
@cli.command("task", short_help="Manage tasks [t]")
@click.argument("content", required=False)
@click.option("-l", "--list", is_flag=True, help="List all tasks")
@click.option(
    "-a", "--all", is_flag=True, help="Show all tasks including completed ones"
)
@click.option("-t", "--tags", help="Comma-separated list of tags")
@click.option("-d", "--due", help="Due date in DD:MM format (e.g., 25:12 for Dec 25)")
@click.option("-p", "--priority", help="Priority (low, medium, high)")
@click.option("-b", "--board", help='Board name (default: "default")')
@click.option("-c", "--complete", help="Mark task as complete by ID")
@click.option(
    "-m",
    "--move",
    nargs=2,
    help="Move task to a different board: <task_id> <board_name>",
)
@click.option("--delete", help="Delete task by ID")
def task_command(
    content, list, all, tags, due, priority, board, complete, move, delete
):
    storage = Storage()

    # Input validation
    if complete:
        try:
            complete_id = int(complete)
            if complete_id <= 0:
                rprint("[red]❌ Task ID must be a positive number[/red]")
                return
        except ValueError:
            rprint("[red]❌ Task ID must be a valid number[/red]")
            return

    if delete:
        try:
            delete_id = int(delete)
            if delete_id <= 0:
                rprint("[red]❌ Task ID must be a positive number[/red]")
                return
        except ValueError:
            rprint("[red]❌ Task ID must be a valid number[/red]")
            return

    # Flexible priority validation
    if priority:
        from logbuch.core.priority_handler import validate_and_normalize_priority
        
        normalized_priority, suggestions = validate_and_normalize_priority(priority)
        
        if normalized_priority:
            priority = normalized_priority  # Use the normalized version
        else:
            # Show helpful error with suggestions
            rprint(f"[red]❌ Invalid priority: '{priority}'[/red]")
            rprint("[yellow]💡 Suggestions:[/yellow]")
            for suggestion in suggestions:
                rprint(f"   • {suggestion}")
            rprint("\n[dim]Type 'logbuch priority-help' for all options[/dim]")
            return

    if content and len(content.strip()) == 0:
        rprint("[red]❌ Task content cannot be empty[/red]")
        return

    if delete:
        task = delete_task(storage, delete)
        if task:
            rprint(f"[green]🗑️ Task deleted: {task['content']}[/green]")
        else:
            rprint(f"[red]Task with ID {delete} not found[/red]")
    elif move:
        task_id, board_name = move
        task = move_task(storage, task_id, board_name)
        if task:
            rprint(
                f"[green]Task \"{task['content']}\" moved to board '{board_name}'[/green]"
            )
        else:
            rprint(f"[red]Task with ID {task_id} not found[/red]")
    elif complete:
        task = complete_task(storage, complete)
        if task:
            rprint(f"[green]✅ Task completed: {task['content']}[/green]")
        else:
            rprint(f"[red]Task with ID {complete} not found[/red]")
    elif list or content is None:
        tasks = list_tasks(storage, all, board)
        if not tasks:
            rprint("[yellow]No tasks found[/yellow]")
            return

        # Limit tasks shown by default for better performance and readability
        if not all and len(tasks) > 20:
            tasks = tasks[:20]
            show_truncated_message = True
        else:
            show_truncated_message = False

        table = Table(show_header=True)
        table.add_column("ID")
        table.add_column("Content")
        table.add_column("Board")
        table.add_column("Priority")
        table.add_column("Status")
        table.add_column("Due Date")

        for task in tasks:
            status = "[green]✓[/green]" if task.get("done") else "☐"
            # Format the due date according to the configured date format
            due_date = task.get("due_date", "")
            if due_date:
                try:
                    # Parse the ISO format date
                    date_obj = datetime.datetime.strptime(due_date.split('T')[0], "%Y-%m-%d")
                    # Format according to user preference
                    date_format = storage.get_config('dateFormat')
                    due_date = date_obj.strftime(date_format)
                except (ValueError, TypeError):
                    due_date = due_date.split("T")[0]
            table.add_row(
                task["id"],
                task["content"],
                task.get("board", "default"),
                task.get("priority", "medium"),
                status,
                due_date,
            )
        console.print(table)
        
        # Show truncation message if tasks were limited
        if show_truncated_message:
            rprint(f"[dim]Showing 20 most recent tasks. Use --all to see all tasks.[/dim]")
    elif content:
        # Validate content before processing
        if len(content.strip()) == 0:
            rprint("[red]❌ Task content cannot be empty[/red]")
            return
            
        task = add_task(storage, content, priority, tags, due, board or "default")
        rprint(f"[green]✨ Task added: {task['content']}[/green]")


# Journal commands
@cli.command("journal", short_help="Add or view journal entries [j]")
@click.argument("content", required=False)
@click.option("-v", "--view", is_flag=True, help="View journal entries")
@click.option("-t", "--tags", help="Comma-separated list of tags")
@click.option("-c", "--category", help="Category for the journal entry")
@click.option(
    "-l", "--limit", type=int, default=10, help="Limit number of entries shown"
)
@click.option("-e", "--editor", is_flag=True, help="Open editor to write entry")
@click.option("-d", "--delete", help="Delete journal entry by ID")
def journal_command(content, view, tags, category, limit, editor, delete):
    storage = Storage()

    # Input validation
    if content is not None and len(content.strip()) == 0:
        rprint("[red]❌ Journal content cannot be empty[/red]")
        return

    if delete:
        try:
            delete_id = int(delete)
            if delete_id <= 0:
                rprint("[red]❌ Journal entry ID must be a positive number[/red]")
                return
        except ValueError:
            rprint("[red]❌ Journal entry ID must be a valid number[/red]")
            return

    if delete:
        entry = delete_journal_entry(storage, delete)
        if entry:
            rprint(
                f"[green]✅ Journal entry deleted: {entry['text'][:30]}{'...' if len(entry['text']) > 30 else ''}[/green]"
            )
        else:
            rprint(f"[red]Journal entry with ID {delete} not found[/red]")
    elif view or not content and not editor:
        entries = list_journal_entries(
            storage, limit=limit, tag=tags, category=category
        )
        if not entries:
            rprint("[yellow]No journal entries found[/yellow]")
            return

        for i, entry in enumerate(entries):
            if i > 0:
                console.print("---")
            date = entry.get("date", "").split("T")[0]
            rprint(f"[bold blue]{date}[/bold blue] [dim]ID: {entry['id']}[/dim]")
            rprint(entry["text"])
            if entry.get("tags"):
                tags_str = ", ".join([f"[magenta]{t}[/magenta]" for t in entry["tags"]])
                rprint(f"Tags: {tags_str}")
    elif editor:
        import click

        text = click.edit()
        if text:
            entry = add_journal_entry(storage, text.strip(), tags, category)
            rprint("[green]Journal entry added successfully![/green]")
    elif content:
        # Validate content before processing
        if len(content.strip()) == 0:
            rprint("[red]❌ Journal content cannot be empty[/red]")
            return
            
        entry = add_journal_entry(storage, content, tags, category)
        rprint("[green]Journal entry added successfully![/green]")


# Calendar command
@cli.command(
    "calendar", short_help="Display tasks and journal entries in a calendar [c]"
)
@click.option("-m", "--month", type=int, help="Month (1-12)")
@click.option("-y", "--year", type=int, help="Year")
def calendar_command(month, year):
    storage = Storage()
    display_calendar(storage, month, year)


# Mood tracking command
@cli.command("mood", short_help="Track and view mood [m]")
@click.argument("mood", required=False)
@click.option("-v", "--view", is_flag=True, help="View mood history")
@click.option("-n", "--notes", help="Additional notes for the mood entry")
@click.option(
    "-l", "--limit", type=int, default=10, help="Limit number of entries shown"
)
@click.option("-d", "--date", help="Filter by date in DD:MM format or natural language")
@click.option("-r", "--random", is_flag=True, help="Get a random mood suggestion")
@click.option("--random-list", type=int, help="Get multiple random mood suggestions (specify count)")
def mood_command(mood, view, notes, limit, date, random, random_list):
    storage = Storage()

    # Input validation for mood
    if mood:
        valid_moods = [
            "happy", "sad", "excited", "calm", "anxious", "angry", "content", 
            "frustrated", "energetic", "tired", "optimistic", "pessimistic",
            "grateful", "stressed", "relaxed", "motivated", "bored", "focused",
            "overwhelmed", "peaceful", "confident", "insecure", "proud", "disappointed"
        ]
        
        if mood.lower() not in valid_moods:
            rprint(f"[red]❌ Invalid mood: '{mood}'[/red]")
            rprint(f"[yellow]Valid moods: {', '.join(valid_moods[:10])}...[/yellow]")
            rprint("[dim]Use 'logbuch mood --random' for suggestions[/dim]")
            return

    if random:
        random_mood = get_random_mood()
        rprint(f"[cyan]Random mood suggestion: [bold]{random_mood}[/bold][/cyan]")
        rprint("[dim]Use this mood with: logbuch mood {random_mood}[/dim]".format(random_mood=random_mood))
    elif random_list:
        random_moods = get_random_moods(random_list)
        rprint(f"[cyan]Random mood suggestions:[/cyan]")
        for i, mood in enumerate(random_moods, 1):
            rprint(f"  {i}. [bold]{mood}[/bold]")
        rprint("[dim]Use any mood with: logbuch mood <mood_name>[/dim]")
    elif view or not mood:
        entries = list_mood_entries(storage, limit, date)
        if not entries:
            rprint("[yellow]No mood entries found[/yellow]")
            return

        table = Table(title="Mood History")
        table.add_column("Date", style="blue")
        table.add_column("Time", style="cyan")
        table.add_column("Mood")
        table.add_column("Notes")

        for entry in entries:
            # Parse the ISO format date and time
            try:
                date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
                date_str = date_obj.strftime("%d:%m")
                time_str = date_obj.strftime("%H:%M")
                table.add_row(date_str, time_str, entry["mood"], entry.get("notes", ""))
            except (ValueError, TypeError):
                # Fallback for any parsing issues
                date_parts = entry["date"].split("T")
                date_str = date_parts[0]
                time_str = date_parts[1].split(".")[0][:5] if len(date_parts) > 1 else ""
                table.add_row(date_str, time_str, entry["mood"], entry.get("notes", ""))
        console.print(table)
    elif mood:
        # Allow any word as a mood
        entry = add_mood_entry(storage, mood, notes)
        rprint(f"[green]Mood entry added: {mood}[/green]")


# Sleep tracking command
@cli.command("sleep", short_help="Track and view sleep [s]")
@click.argument("hours", type=float, required=False)
@click.option("-v", "--view", is_flag=True, help="View sleep history")
@click.option("-n", "--notes", help="Additional notes for the sleep entry")
@click.option(
    "-l", "--limit", type=int, default=10, help="Limit number of entries shown"
)
@click.option("-d", "--date", help="Filter by date in DD:MM format or natural language")
def sleep_command(hours, view, notes, limit, date):
    storage = Storage()

    if view or hours is None:
        entries = list_sleep_entries(storage, limit, date)
        if not entries:
            rprint("[yellow]No sleep entries found[/yellow]")
            return

        table = Table(title="Sleep History")
        table.add_column("Date", style="blue")
        table.add_column("Hours")
        table.add_column("Notes")

        for entry in entries:
            date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%d:%m")
            table.add_row(date_str, str(entry["hours"]), entry.get("notes", ""))
        console.print(table)
    elif hours is not None:
        if hours <= 0:
            rprint("[red]Hours of sleep must be positive[/red]")
            return

        entry = add_sleep_entry(storage, hours, notes)
        rprint(f"[green]Sleep entry added: {hours} hours[/green]")


# Goal management command
@cli.command("goal", short_help="Set and track goals [g]")
@click.argument("description", required=False)
@click.option("-v", "--view", is_flag=True, help="View all goals")
@click.option("-a", "--all", is_flag=True, help="Include completed goals when viewing")
@click.option("-d", "--due", help="Target date in DD:MM format (e.g., 31:12 for Dec 31)")
@click.option("-p", "--progress", help="Update progress (0-100) for a goal ID")
@click.option("-g", "--goal-id", help="Goal ID for updating progress")
@click.option("-r", "--remove", help="Delete a goal by ID")
def goal_command(description, view, all, due, progress, goal_id, remove):
    storage = Storage()

    if remove:
        goal = delete_goal(storage, remove)
        if goal:
            rprint(f"[green]Goal deleted: {goal['description']}[/green]")
        else:
            rprint(f"[red]Goal with ID {remove} not found[/red]")
    elif progress and goal_id:
        try:
            progress_val = int(progress)
            if 0 <= progress_val <= 100:
                goal = update_goal_progress(storage, goal_id, progress_val)
                if goal:
                    status = "completed" if goal["completed"] else "in progress"
                    rprint(
                        f"[green]Goal progress updated: {goal['description']} ({progress_val}% {status})[/green]"
                    )
                else:
                    rprint(f"[red]Goal with ID {goal_id} not found[/red]")
            else:
                rprint("[red]Progress must be between 0 and 100[/red]")
        except ValueError:
            rprint("[red]Invalid progress value[/red]")
    elif view or not description:
        goals = list_goals(storage, all)
        if not goals:
            rprint("[yellow]No goals found[/yellow]")
            return

        table = Table(title="Goals")
        table.add_column("ID")
        table.add_column("Description")
        table.add_column("Progress")
        table.add_column("Target Date")
        table.add_column("Status")

        for goal in goals:
            status = "Completed" if goal["completed"] else "In Progress"
            
            # Format the target date according to the configured date format
            target_date = goal["target_date"]
            if target_date:
                try:
                    # Parse the ISO format date
                    date_obj = datetime.datetime.strptime(target_date.split('T')[0], "%Y-%m-%d")
                    # Format according to user preference
                    date_format = storage.get_config('dateFormat')
                    formatted_date = date_obj.strftime(date_format)
                except (ValueError, TypeError):
                    formatted_date = target_date
            else:
                formatted_date = ""
                
            table.add_row(
                goal["id"],
                goal["description"],
                f"{goal['progress']}%",
                formatted_date,
                status,
            )
        console.print(table)
    elif description and due:
        # Validate date format
        try:
            # Get the configured date format
            date_format = storage.get_config('dateFormat')
            
            # Add current year if not in the format (to handle the deprecation warning)
            if '%Y' not in date_format:
                # Parse with the configured format
                parsed_date = datetime.datetime.strptime(due, date_format)
                # Add current year
                current_year = datetime.datetime.now().year
                parsed_date = parsed_date.replace(year=current_year)
            else:
                # Parse with the configured format that includes year
                parsed_date = datetime.datetime.strptime(due, date_format)
            
            # Convert to YYYY-MM-DD for storage
            formatted_date = parsed_date.strftime("%Y-%m-%d")
            
            goal = add_goal(storage, description, formatted_date)
            rprint(f"[green]Goal added: {description}[/green]")
        except ValueError:
            # Show the expected format based on configuration
            date_format = storage.get_config('dateFormat').replace('%d', 'DD').replace('%m', 'MM').replace('%Y', 'YYYY')
            rprint(f"[red]Invalid date format. Use {date_format}[/red]")
    else:
        rprint(
            "[yellow]Target date required when adding a goal. Use --due YYYY-MM-DD[/yellow]"
        )


# History command for viewing all tracked data
@cli.command("history", short_help="View history of all tracked data [h]")
@click.option("-d", "--date", help="Filter by date in DD:MM format or natural language")
@click.option(
    "-l",
    "--limit",
    type=int,
    default=5,
    help="Limit number of entries shown per category",
)
def history_command(date, limit):
    storage = Storage()

    # Mood history
    mood_entries = list_mood_entries(storage, limit, date)

    # Sleep history
    sleep_entries = list_sleep_entries(storage, limit, date)

    # Goals
    goals = list_goals(storage, include_completed=True)

    # Journal entries
    journal_entries = list_journal_entries(storage, limit=limit, date=date)

    # Tasks
    tasks = list_tasks(storage, show_completed=True)

    # Display in a nice format
    console.print("\n[bold blue]===== Tracking History =====[/bold blue]\n")

    console.print("[bold]Mood History:[/bold]")
    if mood_entries:
        table = Table(show_header=True)
        table.add_column("Date")
        table.add_column("Time")
        table.add_column("Mood")
        table.add_column("Notes")

        for entry in mood_entries:
            date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%d:%m")
            time_str = date_obj.strftime("%H:%M")
            table.add_row(date_str, time_str, entry["mood"], entry.get("notes", ""))
        console.print(table)
    else:
        console.print("[italic]No mood entries found[/italic]")

    console.print("\n[bold]Sleep History:[/bold]")
    if sleep_entries:
        table = Table(show_header=True)
        table.add_column("Date")
        table.add_column("Hours")
        table.add_column("Notes")

        for entry in sleep_entries:
            date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%d:%m")
            table.add_row(date_str, str(entry["hours"]), entry.get("notes", ""))
        console.print(table)
    else:
        console.print("[italic]No sleep entries found[/italic]")

    console.print("\n[bold]Goals:[/bold]")
    if goals:
        table = Table(show_header=True)
        table.add_column("Description")
        table.add_column("Progress")
        table.add_column("Target Date")
        table.add_column("Status")

        for goal in goals:
            status = "Completed" if goal["completed"] else "In Progress"
            
            # Format the target date according to the configured date format
            target_date = goal["target_date"]
            if target_date:
                try:
                    # Parse the ISO format date
                    date_obj = datetime.datetime.strptime(target_date.split('T')[0], "%Y-%m-%d")
                    # Format according to user preference
                    date_format = storage.get_config('dateFormat')
                    formatted_date = date_obj.strftime(date_format)
                except (ValueError, TypeError):
                    formatted_date = target_date
            else:
                formatted_date = ""
                
            table.add_row(
                goal["description"], f"{goal['progress']}%", formatted_date, status
            )
        console.print(table)
    else:
        console.print("[italic]No goals found[/italic]")

    console.print("\n[bold]Journal Entries:[/bold]")
    if journal_entries:
        for i, entry in enumerate(journal_entries):
            if i > 0:
                console.print("---")
            date = entry.get("date", "").split("T")[0]
            rprint(f"[bold blue]{date}[/bold blue]")
            rprint(entry["text"][:100] + ("..." if len(entry["text"]) > 100 else ""))
    else:
        console.print("[italic]No journal entries found[/italic]")

    console.print("\n[bold]Active Tasks:[/bold]")
    active_tasks = [t for t in tasks if not t["done"]]
    if active_tasks:
        table = Table(show_header=True)
        table.add_column("Content")
        table.add_column("Priority")
        table.add_column("Due Date")

        for task in active_tasks[:limit]:
            table.add_row(
                task["content"],
                task.get("priority", "medium"),
                task.get("due_date", ""),
            )
        console.print(table)
    else:
        console.print("[italic]No active tasks found[/italic]")

    console.print("\n[bold]Recently Completed Tasks:[/bold]")
    completed_tasks = [t for t in tasks if t["done"]]
    if completed_tasks:
        table = Table(show_header=True)
        table.add_column("Content")
        table.add_column("Completed At")

        for task in completed_tasks[:limit]:
            completed_at = task.get("completed_at", "").split("T")[0]
            table.add_row(task["content"], completed_at)
        console.print(table)
    else:
        console.print("[italic]No completed tasks found[/italic]")


# Week planning command
@cli.command("week", short_help="View tasks for the week [w]")
@click.option("--prev", "-p", is_flag=True, help="Show previous week")
@click.option("--next", "-n", is_flag=True, help="Show next week")
@click.option("--week", "-w", type=int, help="Show specific week number (1-52/53)")
@click.option("--year", "-y", type=int, help="Show week for specific year")
@click.option("--board", "-b", help="Filter tasks by board")
def week_view(prev, next, week, year, board):
    week_command(prev, next, week, year, board)


# Time tracking command
@cli.command("time", short_help="Track time spent on tasks [ti/tr]")
@click.argument("duration", required=False, type=float)
@click.option("-s", "--start", is_flag=True, help="Start time tracking")
@click.option("-t", "--stop", is_flag=True, help="Stop current time tracking")
@click.option("-v", "--view", is_flag=True, help="View time entries")
@click.option("-c", "--current", is_flag=True, help="Show current tracking session")
@click.option("--task", help="Task ID to associate with time entry")
@click.option("-d", "--description", help="Description for the time entry")
@click.option(
    "-l", "--limit", type=int, default=10, help="Limit number of entries shown"
)
@click.option("--date", help="Filter by date (today/yesterday/YYYY-MM-DD)")
@click.option("--delete", help="Delete time entry by ID")
def time_command(
    duration, start, stop, view, current, task, description, limit, date, delete
):
    storage = Storage()

    if delete:
        entry = delete_time_entry(storage, delete)
        if entry:
            rprint(
                f"[green]🗑️ Time entry deleted: {entry.get('description') or 'No description'}[/green]"
            )
        else:
            rprint(f"[red]Time entry with ID {delete} not found[/red]")
    elif current:
        # Show the current tracking session
        active = get_current_tracking(storage)
        if active:
            description_txt = active.get("description", "No description")
            task_txt = (
                f" for task '{active.get('task_content', '')}'"
                if active.get("task_content")
                else ""
            )

            rprint(
                f"[bold green]⏱️ Currently tracking:[/bold green] {description_txt}{task_txt}"
            )
            rprint(f"[blue]Started at:[/blue] {active['start_time'].split('T')[1][:8]}")
            rprint(f"[blue]Elapsed time:[/blue] {active['elapsed_formatted']}")
        else:
            rprint("[yellow]No active time tracking session[/yellow]")
    elif stop:
        # Stop the current tracking session
        entry = stop_time_tracking(storage)
        if entry:
            minutes, seconds = divmod(entry["duration"], 60)
            hours, minutes = divmod(minutes, 60)
            duration_formatted = f"{hours}h {minutes}m {seconds}s"

            description_txt = entry.get("description", "No description")
            rprint(f"[green]⏱️ Time tracking stopped: {description_txt}[/green]")
            rprint(f"[blue]Duration:[/blue] {duration_formatted}")
        else:
            rprint("[yellow]No active time tracking session to stop[/yellow]")
    elif start:
        # Start a new tracking session
        active = get_current_tracking(storage)
        if active:
            rprint(
                "[yellow]A time tracking session is already active. Stop it first.[/yellow]"
            )
            return

        # If task ID is provided, verify it exists
        if task:
            task_list = list_tasks(storage, show_completed=False)
            if not any(t["id"] == task for t in task_list):
                rprint(f"[red]Task with ID {task} not found[/red]")
                return

        entry = start_time_tracking(storage, task, description)
        if entry:
            description_txt = description or "No description"
            task_txt = (
                f" for task '{entry.get('task_content', '')}'"
                if entry.get("task_content")
                else ""
            )

            rprint(
                f"[green]⏱️ Time tracking started: {description_txt}{task_txt}[/green]"
            )
        else:
            rprint("[red]Failed to start time tracking[/red]")
    elif view or (not duration and not start and not stop and not current):
        # List time entries
        entries = list_time_entries(storage, limit=limit, date=date, task_id=task)
        if not entries:
            rprint("[yellow]No time entries found[/yellow]")
            return

        table = Table(title="Time Entries")
        table.add_column("ID")
        table.add_column("Date", style="blue")
        table.add_column("Task")
        table.add_column("Description")
        table.add_column("Duration")
        table.add_column("Status")

        for entry in entries:
            date_str = entry["date"]
            task_str = entry.get("task_content", "") if entry.get("task_id") else ""
            description_str = entry.get("description", "") or ""

            # Format duration
            if entry.get("duration"):
                duration_str = entry.get("duration_formatted", "")
                status = "[green]Completed[/green]"
            else:
                duration_str = "-"
                status = "[yellow]In Progress[/yellow]"

            table.add_row(
                entry["id"], date_str, task_str, description_str, duration_str, status
            )

        console.print(table)
    elif duration is not None:
        # Add a manual time entry
        if duration <= 0:
            rprint("[red]Duration must be positive[/red]")
            return

        entry = add_time_entry(storage, duration, task, description)
        if entry:
            description_txt = description or "No description"
            task_txt = (
                f" for task '{entry.get('task_content', '')}'"
                if entry.get("task_content")
                else ""
            )

            rprint(f"[green]⏱️ Time entry added: {description_txt}{task_txt}[/green]")
            rprint(f"[blue]Duration:[/blue] {entry.get('duration_formatted', '')}")
        else:
            rprint("[red]Failed to add time entry[/red]")


# Quick commands for convenience
@cli.command("add", short_help="Quick add task, journal, or mood [+]")
@click.argument("content", required=False)
@click.option("-t", "--type", type=click.Choice(['task', 'journal', 'mood']), default='task', help="Type of entry to add")
@click.option("-p", "--priority", type=click.Choice(['low', 'medium', 'high']), default='medium', help="Task priority")
@click.option("-r", "--random-mood", is_flag=True, help="Use random mood")
def quick_add_command(content, type, priority, random_mood):
    storage = Storage()
    
    if not content and type != 'mood':
        rprint(f"[red]Content required for {type}[/red]")
        return
    
    if type == 'task':
        task = quick_add_task(storage, content, priority)
        rprint(f"[green]✨ Task added: {task['content']}[/green]")
    elif type == 'journal':
        entry = quick_add_journal(storage, content)
        rprint(f"[green]📝 Journal entry added[/green]")
    elif type == 'mood':
        mood = content if content and not random_mood else None
        entry = quick_add_mood(storage, mood)
        rprint(f"[green]😊 Mood entry added: {entry['mood']}[/green]")


@cli.command("checkin", short_help="Interactive daily check-in")
def checkin_command():
    storage = Storage()
    quick_daily_checkin(storage)


@cli.command("stats", short_help="Quick statistics overview")
def stats_command():
    storage = Storage()
    quick_stats(storage)


@cli.command("templates", short_help="Show and use task/journal templates")
@click.option("-t", "--type", type=click.Choice(['task', 'journal']), default='task', help="Template type")
@click.option("-a", "--add", help="Add all tasks from template category")
@click.option("-b", "--board", default="default", help="Board for template tasks")
def templates_command(type, add, board):
    storage = Storage()
    
    if add:
        add_template_tasks(storage, add, board)
    else:
        show_templates(type)


@cli.command("bulk", short_help="Bulk operations on tasks")
@click.option("-c", "--complete", help="Complete tasks by IDs (comma-separated)")
@click.option("-d", "--delete", help="Delete tasks by IDs (comma-separated)")
@click.option("-m", "--move", nargs=2, help="Move tasks to board: <task_ids> <board>")
@click.option("--cleanup", type=int, help="Clean up completed tasks older than X days")
@click.option("--suggest", is_flag=True, help="Show smart task suggestions")
def bulk_command(complete, delete, move, cleanup, suggest):
    storage = Storage()
    
    if complete:
        task_ids = [id.strip() for id in complete.split(',')]
        bulk_complete_tasks(storage, task_ids)
    elif delete:
        task_ids = [id.strip() for id in delete.split(',')]
        bulk_delete_tasks(storage, task_ids)
    elif move:
        task_ids_str, target_board = move
        task_ids = [id.strip() for id in task_ids_str.split(',')]
        bulk_move_tasks(storage, task_ids, target_board)
    elif cleanup:
        cleanup_completed_tasks(storage, cleanup)
    elif suggest:
        smart_task_suggestions(storage)
    else:
        rprint("[yellow]Please specify a bulk operation. Use --help for options.[/yellow]")


# Search command
@cli.command("search", short_help="Smart search across all content [/]")
@click.argument("query")
@click.option("-t", "--type", type=click.Choice(['all', 'tasks', 'journal', 'moods', 'goals']), default='all', help="Content type to search")
@click.option("--from-date", help="Start date in DD:MM format")
@click.option("--to-date", help="End date in DD:MM format")
@click.option("--tags", is_flag=True, help="Show popular tags instead of searching")
def search_command(query, type, from_date, to_date, tags):
    storage = Storage()
    
    if tags:
        popular_tags = get_popular_tags(storage, type)
        if popular_tags:
            rprint("[bold cyan]🏷️ Popular Tags:[/bold cyan]")
            for tag, count in popular_tags:
                rprint(f"  {tag} ({count} uses)")
        else:
            rprint("[yellow]No tags found[/yellow]")
        return
    
    if from_date and to_date:
        results = filter_by_date_range(storage, from_date, to_date, type)
        rprint(f"[cyan]📅 Results from {from_date} to {to_date}[/cyan]")
    else:
        results = smart_search(storage, query, type)
    
    display_search_results(results, query)


# Enhanced task command with natural language dates
@cli.command("qtask", short_help="Quick task with natural language dates")
@click.argument("content")
@click.option("-d", "--due", help="Due date (supports 'tomorrow', 'next week', etc.)")
@click.option("-p", "--priority", type=click.Choice(['low', 'medium', 'high']), default='medium')
@click.option("-b", "--board", default="default")
def quick_task_command(content, due, priority, board):
    storage = Storage()
    
    # Parse natural language date
    if due:
        parsed_due = parse_natural_date(due)
        if parsed_due != due:
            rprint(f"[cyan]Interpreted '{due}' as {parsed_due.split(' ')[0]}[/cyan]")
        due = parsed_due
    
    task = storage.add_task(content, priority=priority, due_date=due, board=board)
    rprint(f"[green]✨ Task added: {task['content']}[/green]")
    if due:
        rprint(f"[blue]📅 Due: {due.split(' ')[0]}[/blue]")


# Backup and data management
@cli.command("backup", short_help="Data backup and recovery system [bk]")
@click.argument("action", type=click.Choice(['create', 'list', 'restore', 'health', 'cleanup', 'auto']), required=False, default='list')
@click.argument("name", required=False)
@click.option("--force", is_flag=True, help="Force restore without confirmation")
@click.option("--days", default=30, help="Days to keep for cleanup")
@click.option("--max", default=10, help="Maximum backups to keep")
def backup_command(action, name, force, days, max):
    storage = Storage()
    
    if action == 'create':
        backup_path = create_backup(storage, name)
        rprint(f"[green]💾 Backup saved to: {backup_path}[/green]")
    
    elif action == 'list':
        list_backups()
    
    elif action == 'restore':
        if not name:
            rprint("[red]Backup name required for restore. Use 'latest' for most recent.[/red]")
            return
        
        if not force:
            from rich.prompt import Confirm
            if not Confirm.ask(f"[red]⚠️ This will REPLACE all current data with backup '{name}'. Continue?[/red]"):
                rprint("[yellow]Restore cancelled[/yellow]")
                return
        
        # Create a safety backup before restore
        safety_backup = f"pre_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        rprint("[blue]Creating safety backup before restore...[/blue]")
        create_backup(storage, safety_backup, auto=True)
        
        success = restore_backup(storage, name)
        if success:
            rprint(f"[green]✅ Data restored from backup '{name}'[/green]")
            rprint(f"[blue]💡 Safety backup created: {safety_backup}[/blue]")
    
    elif action == 'health':
        backup_health_check()
    
    elif action == 'cleanup':
        cleanup_old_backups(days, max)
    
    elif action == 'auto':
        # Skip auto backup for now
        rprint("[blue]ℹ️ Auto-backup feature temporarily disabled[/blue]")


# Project management
@cli.command("project", short_help="Project management system [p]")
@click.argument("action", type=click.Choice(['create', 'list', 'show', 'timeline', 'stats', 'suggest']), required=False, default='list')
@click.argument("name", required=False)
@click.option("-d", "--description", help="Project description")
@click.option("--deadline", help="Project deadline (YYYY-MM-DD)")
@click.option("--id", help="Project ID for show command")
def project_command(action, name, description, deadline, id):
    storage = Storage()
    
    if action == 'create':
        if not name:
            rprint("[red]Project name required for create action[/red]")
            return
        
        # Parse deadline if provided
        parsed_deadline = None
        if deadline:
            from logbuch.utils.date_parser import parse_natural_date
            parsed_deadline = parse_natural_date(deadline)
            if parsed_deadline != deadline:
                rprint(f"[cyan]Interpreted deadline as {parsed_deadline.split(' ')[0]}[/cyan]")
        
        create_project(storage, name, description or "", parsed_deadline)
    
    elif action == 'list':
        list_projects(storage)
    
    elif action == 'show':
        project_id = id or name
        if not project_id:
            rprint("[red]Project ID required for show action[/red]")
            return
        show_project_details(storage, project_id)
    
    elif action == 'timeline':
        project_timeline(storage)
    
    elif action == 'stats':
        project_stats(storage)
    
    elif action == 'suggest':
        if not name:
            rprint("[red]Project name required for suggest action[/red]")
            return
        suggest_project_tasks(storage, name)


# Notifications and reminders
@cli.command("notify", short_help="Smart notifications and reminders [!]")
@click.option("--check", is_flag=True, help="Check notification status")
@click.option("--overdue", is_flag=True, help="Check overdue tasks")
@click.option("--today", is_flag=True, help="Check tasks due today")
@click.option("--checkin", is_flag=True, help="Daily check-in reminder")
@click.option("--suggest", is_flag=True, help="Smart reminder suggestions")
@click.option("--test", help="Test notification with message")
@click.option("--schedule", nargs=2, help="Schedule reminder: <task_id> <time>")
def notify_command(check, overdue, today, checkin, suggest, test, schedule):
    storage = Storage()
    
    if test:
        success = send_system_notification("Logbuch Test", test)
        if success:
            rprint("[green]✅ Test notification sent![/green]")
        else:
            rprint("[red]❌ Failed to send notification[/red]")
    elif check:
        show_notification_status(storage)
    elif overdue:
        overdue_tasks = check_overdue_tasks(storage)
        if not overdue_tasks:
            rprint("[green]✅ No overdue tasks![/green]")
    elif today:
        due_today = check_due_today(storage)
        if not due_today:
            rprint("[green]✅ No tasks due today![/green]")
    elif checkin:
        reminded = daily_checkin_reminder(storage)
        if reminded:
            rprint("[blue]📱 Daily check-in reminder sent![/blue]")
        else:
            rprint("[green]✅ You're already active today![/green]")
    elif suggest:
        smart_reminder_suggestions(storage)
    elif schedule:
        task_id, reminder_time = schedule
        schedule_reminder(storage, task_id, reminder_time)
    else:
        # Default: show status
        show_notification_status(storage)


# Export and import data
@cli.command("export", short_help="Export data to various formats [ex]")
@click.option("-f", "--format", type=click.Choice(['json', 'csv', 'markdown', 'txt']), default='json', help="Export format")
@click.option("-o", "--output", help="Output file name")
@click.option("-t", "--type", type=click.Choice(['all', 'tasks', 'journal', 'moods', 'sleep', 'goals']), default='all', help="Data type to export")
def export_command(format, output, type):
    storage = Storage()
    
    try:
        output_path = export_data(storage, format, output, type)
        rprint(f"[green]🚀 Export complete! File: {output_path}[/green]")
    except Exception as e:
        rprint(f"[red]❌ Export failed: {e}[/red]")


@cli.command("import", short_help="Import data from files [im]")
@click.argument("file_path")
@click.option("-t", "--type", type=click.Choice(['all', 'tasks', 'journal', 'moods', 'goals']), default='all', help="Data type to import")
@click.option("--merge", is_flag=True, default=True, help="Merge with existing data")
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def import_command(file_path, type, merge, force):
    storage = Storage()
    
    if not force:
        from rich.prompt import Confirm
        if not Confirm.ask(f"Import data from {file_path}? This will add to your existing data."):
            rprint("[yellow]Import cancelled[/yellow]")
            return
    
    success = import_data(storage, file_path, type, merge)
    if success:
        rprint("[green]🎉 Import successful![/green]")
    else:
        rprint("[red]❌ Import failed[/red]")


# GitHub Gists integration
@cli.command("gist", short_help="GitHub Gists integration [gh]")
@click.argument("action", type=click.Choice(['setup', 'test', 'share', 'list', 'backup', 'restore']))
@click.option("--content", type=click.Choice(['tasks', 'journal', 'dashboard']), help="Content type to share")
@click.option("--task-ids", help="Comma-separated task IDs to share")
@click.option("--public", is_flag=True, help="Make gist public")
@click.option("--gist-id", help="Gist ID for restore operation")
def gist_command(action, content, task_ids, public, gist_id):
    if not INTEGRATIONS_AVAILABLE:
        print(f"❌ GitHub Gists integration not available: {INTEGRATIONS_ERROR}")
        print("💡 Install dependencies with: pip install requests")
        return
        
    storage = Storage()
    command = GitHubGistCommand(storage)
    
    kwargs = {
        'content_type': content,
        'public': public,
        'gist_id': gist_id
    }
    
    if task_ids:
        kwargs['task_ids'] = [id.strip() for id in task_ids.split(',')]
    
    command.run(action=action, **kwargs)


# Smart suggestions
@cli.command("suggest", short_help="AI-powered productivity suggestions [ai]")
def suggest_command():
    context = CommandContext.create()
    command = SmartSuggestionsCommand(context)
    command.run()


# Cloud synchronization
@cli.command("cloud", short_help="Cloud synchronization [cl]")
@click.argument("action", type=click.Choice(['providers', 'setup', 'sync', 'status', 'backup', 'restore']))
@click.option("--provider", help="Cloud provider name")
@click.option("--direction", type=click.Choice(['upload', 'download', 'both']), default='both', help="Sync direction")
@click.option("--backup-id", help="Backup ID for restore operation")
def cloud_command(action, provider, direction, backup_id):
    context = CommandContext.create()
    command = CloudSyncCommand(context)
    
    kwargs = {
        'provider_name': provider,
        'direction': direction,
        'backup_id': backup_id
    }
    
    command.run(action=action, **kwargs)


# Webhook server
@cli.command("webhook", short_help="Webhook server for integrations [wh]")
@click.argument("action", type=click.Choice(['start', 'stop', 'status', 'events', 'setup']))
@click.option("--port", default=8080, help="Server port")
@click.option("--host", default="localhost", help="Server host")
def webhook_command(action, port, host):
    context = CommandContext.create()
    command = WebhookCommand(context)
    
    kwargs = {
        'port': port,
        'host': host
    }
    
    command.run(action=action, **kwargs)


# Dashboard command
@cli.command("dashboard", short_help="Show overview dashboard [d]")
def dashboard_command():
    storage = Storage()
    
    # Skip auto-backup check for now to avoid errors
    # auto_backup_check(storage)
    
    display_dashboard(storage)


# Gamification commands
@cli.command("profile", short_help="View player profile and stats [prof]")
def profile_command():
    storage = Storage()
    gamification = GamificationEngine(storage)
    
    cmd = ProfileCommand(storage, gamification)
    cmd.execute({})


@cli.command("achievements", short_help="View achievements and progress [ach]")
@click.option('--type', help='Filter achievements by type')
@click.option('--show-locked/--hide-locked', default=True, help='Show locked achievements')
def achievements_command(type, show_locked):
    storage = Storage()
    gamification = GamificationEngine(storage)
    
    cmd = AchievementsCommand(storage, gamification)
    cmd.execute({'type': type, 'show_locked': show_locked})


@cli.command("challenges", short_help="View daily challenges [chal]")
def challenges_command():
    storage = Storage()
    gamification = GamificationEngine(storage)
    
    cmd = ChallengesCommand(storage, gamification)
    cmd.execute({})


@cli.command("leaderboard", short_help="View leaderboard [lead]")
def leaderboard_command():
    storage = Storage()
    gamification = GamificationEngine(storage)
    
    cmd = LeaderboardCommand(storage, gamification)
    cmd.execute({})


# AI Coach commands
@cli.command("coach", short_help="AI productivity coaching dashboard [ai]")
def coach_command():
    storage = Storage()
    ai_coach = AIProductivityCoach(storage)
    
    cmd = CoachCommand(storage, ai_coach)
    cmd.execute({})


@cli.command("insights", short_help="Detailed AI coaching insights [in]")
def insights_command():
    storage = Storage()
    ai_coach = AIProductivityCoach(storage)
    
    cmd = InsightsCommand(storage, ai_coach)
    cmd.execute({})


@cli.command("patterns", short_help="Productivity patterns analysis [pat]")
def patterns_command():
    storage = Storage()
    ai_coach = AIProductivityCoach(storage)
    
    cmd = PatternsCommand(storage, ai_coach)
    cmd.execute({})


@cli.command("coach-stats", short_help="AI coach performance statistics [cs]")
def coach_stats_command():
    storage = Storage()
    ai_coach = AIProductivityCoach(storage)
    
    cmd = CoachStatsCommand(storage, ai_coach)
    cmd.execute({})


# Revolutionary Features Commands
@cli.command("environment", short_help="Smart environment integration [env]")
def environment_command():
    if not REVOLUTIONARY_AVAILABLE:
        print(f"❌ Revolutionary features not available: {REVOLUTIONARY_ERROR}")
        return
        
    storage = Storage()
    cmd = SmartEnvironmentCommand(storage)
    cmd.execute()


@cli.command("autopilot", short_help="Productivity autopilot system [auto]")
@click.argument("action", type=click.Choice(['dashboard', 'analyze', 'auto-tasks', 'schedule']), default='dashboard')
def autopilot_command(action):
    if not REVOLUTIONARY_AVAILABLE:
        print(f"❌ Revolutionary features not available: {REVOLUTIONARY_ERROR}")
        return
        
    storage = Storage()
    cmd = AutopilotCommand(storage)
    cmd.execute(action=action)


@cli.command("social", short_help="Social productivity network [soc]")
@click.argument("action", type=click.Choice(['dashboard', 'buddies', 'challenges', 'leaderboard', 'feed']), default='dashboard')
def social_command(action):
    if not REVOLUTIONARY_AVAILABLE:
        print(f"❌ Revolutionary features not available: {REVOLUTIONARY_ERROR}")
        return
        
    storage = Storage()
    cmd = SocialCommand(storage)
    cmd.execute(action=action)


# Final Killer Features Commands
@cli.command("capture", short_help="Lightning-fast idea capture [cap]")
@click.argument("action", type=click.Choice(['add', 'list', 'process', 'stats', 'search']), default='list')
@click.argument("content", required=False)
@click.option("--type", "capture_type", type=click.Choice(['auto', 'idea', 'task', 'note', 'quote', 'link', 'reminder', 'goal']), default='auto')
def capture_command(action, content, capture_type):
    if not FINAL_FEATURES_AVAILABLE:
        print(f"❌ Final features not available: {FINAL_FEATURES_ERROR}")
        return
        
    storage = Storage()
    cmd = QuickCaptureCommand(storage)
    cmd.execute(action=action, content=content, capture_type=capture_type)


@cli.command("weather", short_help="Weather-based productivity optimization [w]")
@click.argument("action", type=click.Choice(['current', 'advice', 'week']), default='current')
def weather_command(action):
    if not FINAL_FEATURES_AVAILABLE:
        print(f"❌ Final features not available: {FINAL_FEATURES_ERROR}")
        return
        
    storage = Storage()
    cmd = WeatherCommand(storage)
    cmd.execute(action=action)


# Commuter Assistant Commands (Your Dream Feature!)
@cli.command("commute", short_help="Train delay checker and commute intelligence [late]")
@click.argument("action", type=click.Choice(['check', 'late', 'setup', 'routes', 'patterns', 'dashboard']), default='check')
def commute_command(action):
    if not COMMUTER_AVAILABLE:
        print(f"❌ Commuter assistant not available: {COMMUTER_ERROR}")
        return
        
    storage = Storage()
    cmd = CommuterCommand(storage)
    cmd.execute(action=action)


@cli.command("add-route", short_help="Add a new commute route")
@click.option("--name", required=True, help="Route name (e.g., 'Work Commute')")
@click.option("--from", "from_station", required=True, help="Departure station")
@click.option("--to", "to_station", required=True, help="Destination station")
@click.option("--mode", type=click.Choice(['train', 'bus', 'subway', 'tram', 'ferry']), default='train', help="Transport mode")
@click.option("--departure", required=True, help="Usual departure time (HH:MM)")
@click.option("--duration", type=int, required=True, help="Journey duration in minutes")
@click.option("--line", help="Line number/name (e.g., 'S1', 'ICE 123')")
@click.option("--operator", help="Transport operator")
@click.option("--default", "set_default", is_flag=True, help="Set as default route")
def add_route_command(name, from_station, to_station, mode, departure, duration, line, operator, set_default):
    if not COMMUTER_AVAILABLE:
        print(f"❌ Commuter assistant not available: {COMMUTER_ERROR}")
        return
        
    storage = Storage()
    cmd = CommuteSetupCommand(storage)
    cmd.execute(
        name=name,
        from_station=from_station,
        to_station=to_station,
        mode=mode,
        departure=departure,
        duration=duration,
        line=line,
        operator=operator,
        set_default=set_default
    )


# The ULTIMATE shortcut - your dream command!
@cli.command("late", short_help="Quick train delay check - your dream feature! 🚂")
def late_command():
    if not COMMUTER_AVAILABLE:
        print(f"❌ Commuter assistant not available: {COMMUTER_ERROR}")
        return
        
    storage = Storage()
    cmd = CommuterCommand(storage)
    cmd.execute(action="late")


# Data cleanup command for perfection
@cli.command("cleanup", short_help="Clean up test data and optimize database")
@click.option("--test-data", is_flag=True, help="Remove test and duplicate data")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def cleanup_command(test_data, confirm):
    storage = Storage()
    
    if test_data:
        if not confirm:
            rprint("[yellow]⚠️ This will remove test tasks and duplicate entries.[/yellow]")
            rprint("[yellow]This action cannot be undone![/yellow]")
            
            import click
            if not click.confirm("Do you want to continue?"):
                rprint("[blue]Cleanup cancelled.[/blue]")
                return
        
        # Get all tasks
        tasks = storage.get_tasks(show_completed=True)
        
        # Identify test tasks
        test_patterns = [
            "test", "Test", "TEST", 
            "Concurrent test", "System check",
            "Integrity test", "Persistence test",
            "Quick task via shortcut", "Quick add test",
            "AAAAAAAAA", "'; DROP TABLE",
            "测试任务", "Task with émojis",
            "Core task", "Stress test"
        ]
        
        tasks_to_remove = []
        for task in tasks:
            content = task.get('content', '')
            if any(pattern in content for pattern in test_patterns):
                tasks_to_remove.append(task)
        
        # Remove test tasks
        removed_count = 0
        for task in tasks_to_remove:
            try:
                storage.delete_task(task['id'])
                removed_count += 1
            except:
                pass
        
        # Fix invalid priorities
        remaining_tasks = storage.get_tasks(show_completed=True)
        fixed_priorities = 0
        for task in remaining_tasks:
            if task.get('priority') not in ['low', 'medium', 'high']:
                try:
                    storage.update_task(task['id'], priority='medium')
                    fixed_priorities += 1
                except:
                    pass
        
        rprint(f"[green]✅ Cleanup completed![/green]")
        rprint(f"[green]• Removed {removed_count} test tasks[/green]")
        rprint(f"[green]• Fixed {fixed_priorities} invalid priorities[/green]")
        rprint(f"[blue]Database is now optimized for better performance![/blue]")
    else:
        rprint("[yellow]Use --test-data flag to clean up test data[/yellow]")
        rprint("[dim]Example: logbuch cleanup --test-data[/dim]")


# First-time setup command for better onboarding
@cli.command("setup", short_help="First-time setup and onboarding")
@click.option("--first-time", is_flag=True, help="Complete first-time setup")
def setup_command(first_time):
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    
    console = Console()
    storage = Storage()
    
    if first_time:
        # Welcome message
        welcome_text = Text()
        welcome_text.append("🌻 WELCOME TO LOKBUCH! 🌻\n", style="bold bright_green")
        welcome_text.append("Your AI-powered productivity companion\n", style="bright_white")
        welcome_text.append("Let's get you set up for maximum productivity!", style="dim white")
        
        console.print(Panel(
            Align.center(welcome_text),
            title="🚀 First-Time Setup",
            border_style="bright_green"
        ))
        
        # Quick tour
        tour_text = Text()
        tour_text.append("🎯 WHAT LOKBUCH CAN DO:\n", style="bold bright_cyan")
        tour_text.append("• 📋 Manage tasks with AI coaching\n", style="white")
        tour_text.append("• 📝 Track journal entries and mood\n", style="white")
        tour_text.append("• 🎮 Gamify your productivity with XP and achievements\n", style="white")
        tour_text.append("• 🚂 Check train delays (your commute assistant)\n", style="white")
        tour_text.append("• ⚡ Quick capture ideas and thoughts\n", style="white")
        tour_text.append("• 🌤️ Weather-based productivity optimization\n", style="white")
        tour_text.append("• 🚽 Create epic ASCII art celebrations\n", style="white")
        
        console.print(Panel(tour_text, title="✨ Features", border_style="bright_cyan"))
        
        # Essential shortcuts
        shortcuts_text = Text()
        shortcuts_text.append("⚡ ESSENTIAL SHORTCUTS:\n", style="bold bright_yellow")
        shortcuts_text.append("logbuch t \"My first task\"", style="cyan")
        shortcuts_text.append("     # Add a task\n", style="dim white")
        shortcuts_text.append("logbuch j \"Today was great!\"", style="cyan")
        shortcuts_text.append("   # Journal entry\n", style="dim white")
        shortcuts_text.append("logbuch m happy", style="cyan")
        shortcuts_text.append("               # Track mood\n", style="dim white")
        shortcuts_text.append("logbuch d", style="cyan")
        shortcuts_text.append("                     # Dashboard\n", style="dim white")
        shortcuts_text.append("logbuch late", style="cyan")
        shortcuts_text.append("                # Check train delays\n", style="dim white")
        shortcuts_text.append("logbuch shortcuts", style="cyan")
        shortcuts_text.append("           # See all shortcuts", style="dim white")
        
        console.print(Panel(shortcuts_text, title="🚀 Get Started", border_style="bright_yellow"))
        
        # Create first task
        console.print("\n[bold bright_green]Let's create your first task![/bold bright_green]")
        
        import click
        first_task = click.prompt("What's your first task?", default="Get familiar with Logbuch")
        
        # Add the task
        from logbuch.storage import add_task
        task = add_task(storage, first_task, priority="medium")
        rprint(f"[green]✨ Great! Your first task has been added: {first_task}[/green]")
        
        # Add welcome journal entry
        from logbuch.storage import add_journal_entry
        welcome_entry = f"Started using Logbuch today! My first task: {first_task}"
        add_journal_entry(storage, welcome_entry)
        rprint(f"[green]📝 Added a welcome journal entry![/green]")
        
        # Show next steps
        next_steps_text = Text()
        next_steps_text.append("🎉 YOU'RE ALL SET!\n", style="bold bright_green")
        next_steps_text.append("Next steps:\n", style="bright_white")
        next_steps_text.append("1. Try 'logbuch d' to see your dashboard\n", style="white")
        next_steps_text.append("2. Use 'logbuch co' to get AI coaching\n", style="white")
        next_steps_text.append("3. Complete your first task and earn XP!\n", style="white")
        next_steps_text.append("4. Explore with 'logbuch shortcuts'\n", style="white")
        next_steps_text.append("\nWelcome to the most advanced CLI productivity platform! 🚀", style="dim white")
        
        console.print(Panel(next_steps_text, title="🎊 Welcome Aboard!", border_style="bright_green"))
        
    else:
        rprint("[yellow]Use --first-time for complete setup[/yellow]")
        rprint("[dim]Example: logbuch setup --first-time[/dim]")


@cli.command("toilet", short_help="ASCII art generator - make your achievements EPIC! 🚽")
@click.argument("text", required=False)
@click.option("--font", "-f", default="standard", help="Font style (standard, big, block, bubble, etc.)")
@click.option("--width", "-w", type=int, help="Output width")
@click.option("--justify", "-j", type=click.Choice(['left', 'center', 'right']), default='left', help="Text alignment")
@click.option("--border", "-b", is_flag=True, help="Add border around text")
@click.option("--color", "-c", help="Text color (red, green, blue, yellow, etc.)")
@click.option("--list-fonts", "-l", is_flag=True, help="List available fonts")
@click.option("--celebrate", help="Celebration mode for achievements")
def toilet_command(text, font, width, justify, border, color, list_fonts, celebrate):
    if not TOILET_AVAILABLE:
        print(f"❌ Toilet command not available: {TOILET_ERROR}")
        return
        
    storage = Storage()
    cmd = ToiletCommand(storage)
    cmd.execute(
        text=text,
        font=font,
        width=width,
        justify=justify,
        border=border,
        color=color,
        list_fonts=list_fonts,
        celebrate=celebrate
    )


# Add commands and their shortcuts to the CLI
cli.add_command(kanban)
cli.add_command(kanban, name="k")

# Add shortcuts for all commands
task_cmd = cli.get_command(None, "task")
if task_cmd:
    cli.add_command(task_cmd, name="t")

journal_cmd = cli.get_command(None, "journal")
if journal_cmd:
    cli.add_command(journal_cmd, name="j")

calendar_cmd = cli.get_command(None, "calendar")
if calendar_cmd:
    cli.add_command(calendar_cmd, name="c")

mood_cmd = cli.get_command(None, "mood")
if mood_cmd:
    cli.add_command(mood_cmd, name="m")

sleep_cmd = cli.get_command(None, "sleep")
if sleep_cmd:
    cli.add_command(sleep_cmd, name="s")

goal_cmd = cli.get_command(None, "goal")
if goal_cmd:
    cli.add_command(goal_cmd, name="g")

history_cmd = cli.get_command(None, "history")
if history_cmd:
    cli.add_command(history_cmd, name="h")

# Add week command shortcut (but weather conflicts with 'w', so use 'wk')
week_cmd = cli.get_command(None, "week")
if week_cmd:
    cli.add_command(week_cmd, name="wk")

# Add time command shortcut
time_cmd = cli.get_command(None, "time")
if time_cmd:
    cli.add_command(time_cmd, name="ti")
    cli.add_command(time_cmd, name="tr")

# Add dashboard command shortcut
dashboard_cmd = cli.get_command(None, "dashboard")
if dashboard_cmd:
    cli.add_command(dashboard_cmd, name="d")

# Add quick command shortcuts
add_cmd = cli.get_command(None, "add")
if add_cmd:
    cli.add_command(add_cmd, name="+")

qtask_cmd = cli.get_command(None, "qtask")
if qtask_cmd:
    cli.add_command(qtask_cmd, name="qt")

checkin_cmd = cli.get_command(None, "checkin")
if checkin_cmd:
    cli.add_command(checkin_cmd, name="ci")

stats_cmd = cli.get_command(None, "stats")
if stats_cmd:
    cli.add_command(stats_cmd, name="st")

templates_cmd = cli.get_command(None, "templates")
if templates_cmd:
    cli.add_command(templates_cmd, name="tpl")

bulk_cmd = cli.get_command(None, "bulk")
if bulk_cmd:
    cli.add_command(bulk_cmd, name="b")

search_cmd = cli.get_command(None, "search")
if search_cmd:
    cli.add_command(search_cmd, name="/")

notify_cmd = cli.get_command(None, "notify")
if notify_cmd:
    cli.add_command(notify_cmd, name="!")

project_cmd = cli.get_command(None, "project")
if project_cmd:
    cli.add_command(project_cmd, name="p")

backup_cmd = cli.get_command(None, "backup")
if backup_cmd:
    cli.add_command(backup_cmd, name="bk")

export_cmd = cli.get_command(None, "export")
if export_cmd:
    cli.add_command(export_cmd, name="ex")

import_cmd = cli.get_command(None, "import")
if import_cmd:
    cli.add_command(import_cmd, name="im")

gist_cmd = cli.get_command(None, "gist")
if gist_cmd:
    cli.add_command(gist_cmd, name="gh")

suggest_cmd = cli.get_command(None, "suggest")
if suggest_cmd:
    cli.add_command(suggest_cmd, name="ai")

cloud_cmd = cli.get_command(None, "cloud")
if cloud_cmd:
    cli.add_command(cloud_cmd, name="cl")

webhook_cmd = cli.get_command(None, "webhook")
if webhook_cmd:
    cli.add_command(webhook_cmd, name="wh")

# Gamification shortcuts
profile_cmd = cli.get_command(None, "profile")
if profile_cmd:
    cli.add_command(profile_cmd, name="prof")

achievements_cmd = cli.get_command(None, "achievements")
if achievements_cmd:
    cli.add_command(achievements_cmd, name="ach")

challenges_cmd = cli.get_command(None, "challenges")
if challenges_cmd:
    cli.add_command(challenges_cmd, name="chal")

leaderboard_cmd = cli.get_command(None, "leaderboard")
if leaderboard_cmd:
    cli.add_command(leaderboard_cmd, name="lead")

# AI Coach shortcuts (coach conflicts with 'ai', so use 'co')
coach_cmd = cli.get_command(None, "coach")
if coach_cmd:
    cli.add_command(coach_cmd, name="co")

insights_cmd = cli.get_command(None, "insights")
if insights_cmd:
    cli.add_command(insights_cmd, name="in")

patterns_cmd = cli.get_command(None, "patterns")
if patterns_cmd:
    cli.add_command(patterns_cmd, name="pat")

coach_stats_cmd = cli.get_command(None, "coach-stats")
if coach_stats_cmd:
    cli.add_command(coach_stats_cmd, name="cs")

# Revolutionary features shortcuts
if REVOLUTIONARY_AVAILABLE:
    environment_cmd = cli.get_command(None, "environment")
    if environment_cmd:
        cli.add_command(environment_cmd, name="env")

    autopilot_cmd = cli.get_command(None, "autopilot")
    if autopilot_cmd:
        cli.add_command(autopilot_cmd, name="auto")

    social_cmd = cli.get_command(None, "social")
    if social_cmd:
        cli.add_command(social_cmd, name="soc")

# Final killer features shortcuts
if FINAL_FEATURES_AVAILABLE:
    capture_cmd = cli.get_command(None, "capture")
    if capture_cmd:
        cli.add_command(capture_cmd, name="cap")

    weather_cmd = cli.get_command(None, "weather")
    if weather_cmd:
        cli.add_command(weather_cmd, name="w")

# Commuter assistant shortcuts (dream feature!)
if COMMUTER_AVAILABLE:
    commute_cmd = cli.get_command(None, "commute")
    if commute_cmd:
        cli.add_command(commute_cmd, name="train")
    
    # The ultimate shortcut is already defined as "late" command above!

# Toilet command shortcuts (ASCII art!)
if TOILET_AVAILABLE:
    toilet_cmd = cli.get_command(None, "toilet")
    if toilet_cmd:
        cli.add_command(toilet_cmd, name="art")  # Alternative name
        cli.add_command(toilet_cmd, name="ascii")  # Another alternative

# Additional useful shortcuts
profile_cmd = cli.get_command(None, "profile")
if profile_cmd:
    cli.add_command(profile_cmd, name="me")  # Alternative to 'prof'

# Quick shortcuts for power users
task_cmd = cli.get_command(None, "task")
if task_cmd:
    cli.add_command(task_cmd, name="todo")  # Alternative to 't'

journal_cmd = cli.get_command(None, "journal")
if journal_cmd:
    cli.add_command(journal_cmd, name="log")  # Alternative to 'j'

# Ultra-short shortcuts for most common commands
dashboard_cmd = cli.get_command(None, "dashboard")
if dashboard_cmd:
    cli.add_command(dashboard_cmd, name=".")  # Super quick dashboard

# Help shortcut
help_cmd = cli.get_command(None, "help")
if help_cmd:
    cli.add_command(help_cmd, name="?")


@cli.command("shortcuts", short_help="Show all available shortcuts")
def shortcuts_command():
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    # Header
    header_text = Text()
    header_text.append("⚡ LOKBUCH SHORTCUTS\n", style="bold bright_cyan")
    header_text.append("Lightning-fast productivity commands", style="dim bright_white")
    
    console.print(Panel(
        header_text,
        title="🚀 Speed Reference",
        border_style="bright_cyan"
    ))
    
    # Core shortcuts table
    core_table = Table(title="📋 Core Commands", show_header=True, header_style="bold bright_yellow")
    core_table.add_column("Shortcut", style="cyan", width=10)
    core_table.add_column("Command", style="white", width=15)
    core_table.add_column("Description", style="dim white", width=40)
    
    core_shortcuts = [
        ("t", "task", "Add or list tasks"),
        ("todo", "task", "Alternative task command"),
        ("j", "journal", "Add or view journal entries"),
        ("log", "journal", "Alternative journal command"),
        ("m", "mood", "Track your mood"),
        ("c", "calendar", "View calendar"),
        ("k", "kanban", "Kanban board view"),
        ("g", "goal", "Manage goals"),
        ("s", "sleep", "Track sleep"),
        ("h", "history", "View history"),
        ("d", "dashboard", "Main dashboard"),
        (".", "dashboard", "Ultra-quick dashboard"),
        ("+", "add", "Quick add anything"),
    ]
    
    for shortcut, command, description in core_shortcuts:
        core_table.add_row(shortcut, command, description)
    
    console.print(core_table)
    
    # Advanced shortcuts table
    advanced_table = Table(title="🚀 Advanced Features", show_header=True, header_style="bold bright_green")
    advanced_table.add_column("Shortcut", style="cyan", width=10)
    advanced_table.add_column("Command", style="white", width=15)
    advanced_table.add_column("Description", style="dim white", width=40)
    
    advanced_shortcuts = [
        ("co", "coach", "AI productivity coach"),
        ("prof", "profile", "Your productivity profile"),
        ("me", "profile", "Alternative profile command"),
        ("ach", "achievements", "View achievements"),
        ("cap", "capture", "Quick idea capture"),
        ("w", "weather", "Weather-based productivity"),
        ("late", "late", "Check train delays (dream feature!)"),
        ("train", "commute", "Commuter assistant"),
        ("toilet", "toilet", "ASCII art generator 🚽"),
        ("art", "toilet", "ASCII art (alternative)"),
        ("ascii", "toilet", "ASCII art (alternative)"),
        ("ai", "suggest", "AI suggestions"),
        ("env", "environment", "Smart environment"),
        ("auto", "autopilot", "Productivity autopilot"),
        ("soc", "social", "Social productivity network"),
    ]
    
    for shortcut, command, description in advanced_shortcuts:
        advanced_table.add_row(shortcut, command, description)
    
    console.print(advanced_table)
    
    # Utility shortcuts table
    utility_table = Table(title="🛠️ Utilities", show_header=True, header_style="bold bright_blue")
    utility_table.add_column("Shortcut", style="cyan", width=10)
    utility_table.add_column("Command", style="white", width=15)
    utility_table.add_column("Description", style="dim white", width=40)
    
    utility_shortcuts = [
        ("/", "search", "Search everything"),
        ("!", "notify", "Notifications"),
        ("p", "project", "Project management"),
        ("b", "bulk", "Bulk operations"),
        ("st", "stats", "Statistics"),
        ("ex", "export", "Export data"),
        ("im", "import", "Import data"),
        ("bk", "backup", "Backup data"),
        ("?", "help", "Show help"),
        ("wk", "week", "Weekly view"),
        ("ti", "time", "Time tracking"),
    ]
    
    for shortcut, command, description in utility_shortcuts:
        utility_table.add_row(shortcut, command, description)
    
    console.print(utility_table)
    
    # Pro tips
    tips_text = Text()
    tips_text.append("💡 Pro Tips:\n", style="bold bright_yellow")
    tips_text.append("• Use 'logbuch .' for instant dashboard\n", style="white")
    tips_text.append("• Use 'logbuch late' to check if your train is delayed\n", style="white")
    tips_text.append("• Use 'logbuch +' for quick adding anything\n", style="white")
    tips_text.append("• Use 'logbuch /' to search across all your data\n", style="white")
    tips_text.append("• Use 'logbuch ?' for help anytime", style="white")
    
    console.print(Panel(tips_text, title="⚡ Power User Tips", border_style="bright_yellow"))


def main():
    cli()


# Import perfection modules
from logbuch.commands.maintenance import maintenance
from logbuch.commands.onboarding import welcome, tour
from logbuch.core.error_handling import graceful_shutdown, error_handler
from logbuch.core.performance import perf_monitor

# Add maintenance commands
cli.add_command(maintenance)

# Add onboarding commands  
cli.add_command(welcome)
cli.add_command(tour)

# Add performance monitoring command
@cli.command()
def perf():
    stats = perf_monitor.get_stats()
    
    console.print("📊 [bold bright_blue]Performance Statistics[/bold bright_blue]")
    console.print("=" * 40)
    
    for key, value in stats.items():
        console.print(f"{key}: [bright_yellow]{value}[/bright_yellow]")

# Add error statistics command
@cli.command()
def errors():
    stats = error_handler.get_error_stats()
    
    console.print("🛡️ [bold bright_blue]Error Statistics[/bold bright_blue]")
    console.print("=" * 40)
    
    console.print(f"Total errors: [bright_yellow]{stats['total_errors']}[/bright_yellow]")
    console.print(f"Unique errors: [bright_yellow]{stats['unique_errors']}[/bright_yellow]")
    
    if stats['most_common']:
        console.print("\n🔥 Most common errors:")
        for error, count in stats['most_common']:
            console.print(f"  • {error[:50]}... ({count}x)")


@cli.command("priority-help")
def priority_help():
    from logbuch.core.priority_handler import get_priority_help
    
    console.print(get_priority_help())


# Add perfection commands if available
if PERFECTION_MODULES_AVAILABLE:
    cli.add_command(maintenance)
    cli.add_command(welcome)
    cli.add_command(tour)
    
    # Add performance monitoring command
    @cli.command()
    def perf():
        stats = perf_monitor.get_stats()
        
        console.print("📊 [bold bright_blue]Performance Statistics[/bold bright_blue]")
        console.print("=" * 40)
        
        for key, value in stats.items():
            console.print(f"{key}: [bright_yellow]{value}[/bright_yellow]")

    # Add error statistics command
    @cli.command()
    def errors():
        stats = error_handler.get_error_stats()
        
        console.print("🛡️ [bold bright_blue]Error Statistics[/bold bright_blue]")
        console.print("=" * 40)
        
        console.print(f"Total errors: [bright_yellow]{stats['total_errors']}[/bright_yellow]")
        console.print(f"Unique errors: [bright_yellow]{stats['unique_errors']}[/bright_yellow]")
        
        if stats['most_common']:
            console.print("\n🔥 Most common errors:")
            for error, count in stats['most_common']:
                console.print(f"  • {error[:50]}... ({count}x)")


if __name__ == "__main__":
    main()
