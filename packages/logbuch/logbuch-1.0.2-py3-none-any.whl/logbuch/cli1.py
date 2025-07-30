#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/cli.py

import click


class CustomGroup(click.Group):
    def format_commands(self, ctx, formatter):
        # Custom flat command list in fixed order
        cmds = [
            "calendar[c]",
            "task[k]",
            "week[w]",
            "timer[ti]",
            "kanban[k]",
            "mood[m]",
            "goal[g]",
            "journal[j]",
            "sleep[s]",
            "history[h]",
        ]
        formatter.write_text("\n".join(cmds))


import datetime
from pathlib import Path

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from logbuch.commands.calendar import display_calendar
from logbuch.commands.goal import (
    add_goal,
    delete_goal,
    list_goals,
    update_goal_progress,
)
from logbuch.commands.journal import (
    add_journal_entry,
    delete_journal_entry,
    list_journal_entries,
)
from logbuch.commands.kanban import kanban
from logbuch.commands.mood import add_mood_entry, list_mood_entries
from logbuch.commands.sleep import add_sleep_entry, list_sleep_entries
from logbuch.commands.task import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    move_task,
)
from logbuch.commands.time import (
    add_time_entry,
    delete_time_entry,
    get_current_tracking,
    list_time_entries,
    start_time_tracking,
    stop_time_tracking,
)
from logbuch.commands.week import week_command
from logbuch.storage import Storage

# Initialize console
console = Console()


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
@click.pass_context
def cli(ctx, backup, restore, export, import_file, info, format):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    """Logbuch - A personal CLI app combining journal and task management"""
    # If no subcommand is provided and no options are specified, show help
    if ctx.invoked_subcommand is None and not any(
        [backup, restore, export, import_file, info]
    ):
        click.echo(ctx.get_help())
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
@click.option("-d", "--due", help="Due date (YYYY-MM-DD)")
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
    elif list or not content:
        tasks = list_tasks(storage, all, board)
        if not tasks:
            rprint("[yellow]No tasks found[/yellow]")
            return

        table = Table(show_header=True)
        table.add_column("ID")
        table.add_column("Content")
        table.add_column("Board")
        table.add_column("Priority")
        table.add_column("Status")
        table.add_column("Due Date")

        for task in tasks:
            status = "[green]✓[/green]" if task.get("done") else "☐"
            due_date = task.get("due_date", "")
            if due_date:
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
    elif content:
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
@click.option("-d", "--date", help="Filter by date (today/yesterday/YYYY-MM-DD)")
def mood_command(mood, view, notes, limit, date):
    storage = Storage()

    if view or not mood:
        entries = list_mood_entries(storage, limit, date)
        if not entries:
            rprint("[yellow]No mood entries found[/yellow]")
            return

        table = Table(title="Mood History")
        table.add_column("Date", style="blue")
        table.add_column("Mood")
        table.add_column("Notes")

        for entry in entries:
            date_str = entry["date"].split("T")[0]
            table.add_row(date_str, entry["mood"], entry.get("notes", ""))
        console.print(table)
    elif mood:
        valid_moods = ["Good", "Neutral", "Bad"]
        if mood not in valid_moods:
            rprint(
                f"[yellow]Invalid mood. Please use one of: {', '.join(valid_moods)}[/yellow]"
            )
            return

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
@click.option("-d", "--date", help="Filter by date (today/yesterday/YYYY-MM-DD)")
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
            date_str = entry["date"].split("T")[0]
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
@click.option("-d", "--due", help="Target date for the goal (YYYY-MM-DD)")
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
            table.add_row(
                goal["id"],
                goal["description"],
                f"{goal['progress']}%",
                goal["target_date"],
                status,
            )
        console.print(table)
    elif description and due:
        # Validate date format
        try:
            datetime.datetime.strptime(due, "%Y-%m-%d")
            goal = add_goal(storage, description, due)
            rprint(f"[green]Goal added: {description}[/green]")
        except ValueError:
            rprint("[red]Invalid date format. Use YYYY-MM-DD[/red]")
    else:
        rprint(
            "[yellow]Target date required when adding a goal. Use --due YYYY-MM-DD[/yellow]"
        )


# History command for viewing all tracked data
@cli.command("history", short_help="View history of all tracked data [h]")
@click.option("-d", "--date", help="Filter by date (today/yesterday/YYYY-MM-DD)")
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
        table.add_column("Mood")
        table.add_column("Notes")

        for entry in mood_entries:
            date_str = entry["date"].split("T")[0]
            table.add_row(date_str, entry["mood"], entry.get("notes", ""))
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
            date_str = entry["date"].split("T")[0]
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
            table.add_row(
                goal["description"], f"{goal['progress']}%", goal["target_date"], status
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

# Add week command shortcut
week_cmd = cli.get_command(None, "week")
if week_cmd:
    cli.add_command(week_cmd, name="w")

# Add time command shortcut
time_cmd = cli.get_command(None, "time")
if time_cmd:
    cli.add_command(time_cmd, name="ti")
    cli.add_command(time_cmd, name="tr")


def main():
    cli()


if __name__ == "__main__":
    main()
