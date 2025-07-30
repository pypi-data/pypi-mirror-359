#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import datetime
from rich.console import Console
from rich.table import Table
from rich import box

from logbuch.storage import Storage

console = Console()


def get_week_dates(week_number=None, year=None):
    # Default to current week and year if not specified
    today = datetime.date.today()
    if year is None:
        year = today.year
    if week_number is None:
        week_number = today.isocalendar()[1]

    # Calculate the date of the first day of the week (Monday)
    first_day = datetime.date.fromisocalendar(year, week_number, 1)

    # Create a list of dates for the entire week
    dates = [first_day + datetime.timedelta(days=i) for i in range(7)]

    return dates


def get_current_week_number():
    today = datetime.date.today()
    return (today.isocalendar()[1], today.year)


def display_week_view(storage, week_number=None, year=None, board=None):
    # Get the dates for the week
    dates = get_week_dates(week_number, year)
    today = datetime.date.today()

    # Get tasks for the entire month to filter by date later
    all_tasks = storage.get_tasks(show_completed=True)

    # Create a header that shows the week number and date range
    first_day = dates[0]
    last_day = dates[6]
    week_number = first_day.isocalendar()[1]

    header_text = f"Week {week_number}: {first_day.strftime('%b %d')} - {last_day.strftime('%b %d, %Y')}"
    console.print(f"[bold cyan]{header_text}[/bold cyan]", justify="center")

    # Create the week table
    week_table = Table(box=box.ROUNDED, expand=True)

    # Add columns for each day
    for date in dates:
        day_name = date.strftime("%a")
        day_date = date.strftime("%d")

        # Highlight the current day
        if date == today:
            header = f"[bold white on blue]{day_name} {day_date}[/bold white on blue]"
        else:
            header = f"[bold]{day_name} {day_date}[/bold]"

        week_table.add_column(header, justify="left", vertical="top", min_width=20)

    # Filter and organize tasks by day and priority
    day_tasks = {date: [] for date in dates}

    for task in all_tasks:
        if board and task.get("board") != board:
            continue

        if task.get("due_date"):
            try:
                due_date = datetime.datetime.fromisoformat(task["due_date"]).date()

                # Check if the task is due on any of the days in this week
                if due_date in dates:
                    day_tasks[due_date].append(task)
            except (ValueError, TypeError):
                # Skip tasks with invalid due dates
                pass

    # Sort tasks by priority and done status
    for date, tasks in day_tasks.items():
        day_tasks[date] = sorted(
            tasks,
            key=lambda t: (
                t.get("done", False),  # Done tasks last
                {"high": 0, "medium": 1, "low": 2}.get(
                    t.get("priority", "medium"), 1
                ),  # Sort by priority
            ),
        )

    # Create content for each day
    day_contents = []
    for date in dates:
        tasks = day_tasks[date]
        content = []

        # Add tasks for the day
        for task in tasks:
            priority = task.get("priority", "medium")
            priority_color = {
                "high": "red",
                "medium": "yellow",
                "low": "blue",
            }.get(priority, "white")

            done = task.get("done", False)

            if done:
                task_line = f"[dim]✓ {task['content']}[/dim]"
            else:
                task_line = f"[{priority_color}]• {task['content']}[/{priority_color}]"

            content.append(task_line)

        # If no tasks, add placeholder
        if not content:
            content = ["[dim]No tasks due[/dim]"]

        day_contents.append("\n".join(content))

    # Add the row to the table
    week_table.add_row(*day_contents)

    # Display the table
    console.print(week_table)

    # Show navigation help
    console.print("\n[dim]Navigation:[/dim]")
    console.print("[dim]• Previous week: logbuch week --prev[/dim]")
    console.print("[dim]• Next week: logbuch week --next[/dim]")
    console.print(
        "[dim]• Specific week: logbuch week --week <number> --year <year>[/dim]"
    )


def week_command(prev=False, next=False, week=None, year=None, board=None):
    storage = Storage()

    current_week, current_year = get_current_week_number()

    if week is None:
        week = current_week

    if year is None:
        year = current_year

    # Handle navigation
    if prev:
        if week > 1:
            week -= 1
        else:
            # Go to the last week of the previous year
            year -= 1
            last_day = datetime.date(year, 12, 31)
            week = last_day.isocalendar()[1]
    elif next:
        if week < 52:  # Most years have 52 weeks
            week += 1
        else:
            # Check if the year has 53 weeks
            last_day = datetime.date(year, 12, 31)
            last_week = last_day.isocalendar()[1]

            if week < last_week:
                week += 1
            else:
                # Go to the first week of the next year
                year += 1
                week = 1

    display_week_view(storage, week, year, board)
