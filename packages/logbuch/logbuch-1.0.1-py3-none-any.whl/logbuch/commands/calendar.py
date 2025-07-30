#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/calendar.py

import calendar
import datetime
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def display_calendar(storage, month=None, year=None):
    today = datetime.date.today()
    month = month or today.month
    year = year or today.year

    # Get calendar for the specified month
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Get tasks and journal entries for this month
    month_start = datetime.date(year, month, 1).isoformat()
    if month == 12:
        next_month_start = datetime.date(year + 1, 1, 1).isoformat()
    else:
        next_month_start = datetime.date(year, month + 1, 1).isoformat()

    # Retrieve all tasks that aren't completed
    tasks = storage.get_tasks(show_completed=False)

    # Retrieve journal entries for this month
    journal_entries = storage.get_journal_entries()

    # Filter tasks for this month's due dates
    month_tasks = {}
    for task in tasks:
        if task.get("due_date"):
            due_date = task["due_date"].split("T")[0]
            if month_start <= due_date < next_month_start:
                day = int(due_date.split("-")[2])
                if day not in month_tasks:
                    month_tasks[day] = []
                month_tasks[day].append(task)

    # Filter journal entries for this month
    month_journal = {}
    for entry in journal_entries:
        entry_date = entry["date"].split("T")[0]
        if month_start <= entry_date < next_month_start:
            day = int(entry_date.split("-")[2])
            if day not in month_journal:
                month_journal[day] = []
            month_journal[day].append(entry)

    # Create table for calendar
    table = Table(title=f"{month_name} {year}", box=box.SIMPLE)

    # Add day header columns
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        table.add_column(day, justify="center")

    # Fill calendar with data
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                # Empty day cell
                content = ""
            else:
                # Format each day cell
                # Check if this is today
                is_today = (
                    day == today.day and month == today.month and year == today.year
                )

                # Count tasks and journal entries for this day
                task_count = len(month_tasks.get(day, []))
                journal_count = len(month_journal.get(day, []))

                # Build the cell content
                if is_today:
                    day_str = f"[bold white on blue]{day}[/]"
                else:
                    day_str = f"{day}"

                content = day_str
                if task_count > 0:
                    content += f"\n[red]{task_count} ✓[/]"
                if journal_count > 0:
                    content += f"\n[green]{journal_count} 📝[/]"

            row.append(content)

        table.add_row(*row)

    # Display the calendar
    console.print(table)

    # Display summary
    total_tasks = sum(len(tasks) for tasks in month_tasks.values())
    total_entries = sum(len(entries) for entries in month_journal.values())

    console.print("\n[blue]Month Summary:[/]")
    console.print(f"[red]📌 Tasks: {total_tasks}[/]")
    console.print(f"[green]📝 Journal Entries: {total_entries}[/]")


def display_day_view(storage, day, month=None, year=None):
    today = datetime.date.today()
    month = month or today.month
    year = year or today.year

    # Get the date
    try:
        date = datetime.date(year, month, day)
    except ValueError:
        console.print(f"[red]Invalid date: {year}-{month}-{day}[/]")
        return

    date_str = date.isoformat()

    # Get tasks due on this day
    tasks = storage.get_tasks()
    day_tasks = []
    for task in tasks:
        if task.get("due_date") and task["due_date"].startswith(date_str):
            day_tasks.append(task)

    # Get journal entries for this day
    journal_entries = storage.get_journal_entries()
    day_journal = []
    for entry in journal_entries:
        if entry["date"].startswith(date_str):
            day_journal.append(entry)

    # Display the day view
    weekday = calendar.day_name[date.weekday()]
    formatted_date = date.strftime("%B %d, %Y")
    console.print(f"\n[bold blue]{weekday}, {formatted_date}[/]\n")

    # Display tasks
    if day_tasks:
        console.print("[yellow]📌 Tasks:[/]")
        for task in day_tasks:
            status = "[green]✅[/]" if task.get("done") else "⬜"
            priority = task.get("priority", "medium")
            if priority == "high":
                priority_mark = "[red](!)[/]"
            elif priority == "medium":
                priority_mark = "[yellow](!)[/]"
            else:
                priority_mark = ""

            console.print(f"{status} {task['content']} {priority_mark}")
    else:
        console.print("[yellow]📌 No tasks for this day[/]")

    console.print()

    # Display journal entries
    if day_journal:
        console.print("[green]📝 Journal Entries:[/]")
        for entry in day_journal:
            time_str = entry["date"].split("T")[1][
                :5
            ]  # Extract HH:MM from the time part
            console.print(
                f"[dim]{time_str}[/] {entry['text'][:50]}{'...' if len(entry['text']) > 50 else ''}"
            )
    else:
        console.print("[green]📝 No journal entries for this day[/]")
