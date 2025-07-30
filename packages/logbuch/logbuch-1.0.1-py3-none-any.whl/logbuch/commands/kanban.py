#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import click
import sqlite3
from rich.console import Console
from rich.table import Table
from rich import box

from logbuch.storage import Storage

console = Console()


@click.group()
def kanban():
    pass


@kanban.command(name="list", short_help="List available task boards")
@click.option(
    "--all", "-a", is_flag=True, help="Show all tasks including completed ones"
)
def list_boards(all):
    storage = Storage()

    # Get all tasks to extract unique board names
    tasks = storage.get_tasks(show_completed=all)
    boards = {task["board"] for task in tasks}

    if not boards:
        console.print("[yellow]No boards found[/yellow]")
        return

    table = Table(title="Task Boards")
    table.add_column("Board Name", style="magenta")
    table.add_column("Tasks", style="cyan", justify="right")

    for board in sorted(boards):
        # Count tasks in this board
        board_tasks = [t for t in tasks if t["board"] == board]
        completed = sum(1 for t in board_tasks if t["done"])
        total = len(board_tasks)

        table.add_row(board, f"{total - completed} active, {completed} completed")

    console.print(table)


@kanban.command(name="show", short_help="Display tasks in a kanban board view")
@click.argument("board", required=False)
@click.option("--all", "-a", is_flag=True, help="Include completed tasks")
@click.option(
    "--view",
    "-v",
    type=click.Choice(["simple", "full"]),
    default="full",
    help="View type (simple: To Do/Done, full: multiple columns)",
)
def show_board(board, all, view):
    storage = Storage()

    # If no board specified, use default
    if not board:
        board = "default"

    # Get tasks for this board
    tasks = storage.get_tasks(show_completed=all, board=board)

    if not tasks:
        console.print(f"[yellow]No tasks found in board '{board}'[/yellow]")
        return

    console.print(f"\n[bold]Kanban Board: {board}[/bold]", justify="center")

    # Define color mapping for priority
    priority_colors = {"low": "blue", "medium": "yellow", "high": "red"}

    if view == "simple":
        # Simple view with To Do and Done columns
        # Group tasks by status
        to_do = [t for t in tasks if not t["done"]]
        done = [t for t in tasks if t["done"]]

        # Further organize tasks by priority
        high_priority = [t for t in to_do if t.get("priority") == "high"]
        medium_priority = [t for t in to_do if t.get("priority") == "medium"]
        low_priority = [t for t in to_do if t.get("priority") == "low"]

        # Create tables for columns
        todo_table = Table(title="To Do", box=box.ROUNDED, width=40)
        todo_table.add_column("ID", style="cyan", no_wrap=True)
        todo_table.add_column("Task", style="white")
        todo_table.add_column("Due", style="green")

        done_table = Table(title="Done", box=box.ROUNDED, width=40)
        done_table.add_column("ID", style="cyan", no_wrap=True)
        done_table.add_column("Task", style="white")
        done_table.add_column("Completed", style="green")

        # Add high priority tasks with visual indication
        if high_priority:
            todo_table.add_section()
            todo_table.add_row("[red bold]High Priority[/red bold]", "", "")

            for task in high_priority:
                due_date = task.get("due_date", "")
                if due_date:
                    due_date = due_date.split("T")[0]
                todo_table.add_row(
                    task["id"], f"[red]{task['content']}[/red]", due_date
                )

        # Add medium priority tasks
        if medium_priority:
            todo_table.add_section()
            todo_table.add_row("[yellow]Medium Priority[/yellow]", "", "")

            for task in medium_priority:
                due_date = task.get("due_date", "")
                if due_date:
                    due_date = due_date.split("T")[0]
                todo_table.add_row(
                    task["id"], f"[yellow]{task['content']}[/yellow]", due_date
                )

        # Add low priority tasks
        if low_priority:
            todo_table.add_section()
            todo_table.add_row("[blue]Low Priority[/blue]", "", "")

            for task in low_priority:
                due_date = task.get("due_date", "")
                if due_date:
                    due_date = due_date.split("T")[0]
                todo_table.add_row(
                    task["id"], f"[blue]{task['content']}[/blue]", due_date
                )

        # Add completed tasks if requested
        if all and done:
            for task in done:
                completed_at = task.get("completed_at", "")
                if completed_at:
                    completed_at = completed_at.split("T")[0]
                done_table.add_row(task["id"], task["content"], completed_at)

        # Create a table for the board
        board_table = Table(box=None, show_header=False, padding=1)
        board_table.add_column("To Do")
        board_table.add_column("Done")

        board_table.add_row(todo_table, done_table)
        console.print(board_table)

    else:
        # Full kanban view with multiple columns
        # Create custom statuses for tasks
        todo = []
        in_progress = []
        review = []
        done = []

        # Analyze task content and due dates to create a more detailed board
        for task in tasks:
            if task["done"]:
                done.append(task)
            else:
                content_lower = task["content"].lower()

                # Check if task appears to be in progress
                if (
                    "in progress" in content_lower
                    or "working" in content_lower
                    or "started" in content_lower
                ):
                    in_progress.append(task)
                # Check if task appears to be in review
                elif (
                    "review" in content_lower
                    or "testing" in content_lower
                    or "validate" in content_lower
                ):
                    review.append(task)
                else:
                    todo.append(task)

        # Create column tables
        backlog_table = Table(title="Backlog", box=box.ROUNDED, width=30)
        backlog_table.add_column("ID", style="cyan", no_wrap=True)
        backlog_table.add_column("Task", style="white")

        in_progress_table = Table(title="In Progress", box=box.ROUNDED, width=30)
        in_progress_table.add_column("ID", style="cyan", no_wrap=True)
        in_progress_table.add_column("Task", style="white")

        review_table = Table(title="Review", box=box.ROUNDED, width=30)
        review_table.add_column("ID", style="cyan", no_wrap=True)
        review_table.add_column("Task", style="white")

        done_table = Table(title="Done", box=box.ROUNDED, width=30)
        done_table.add_column("ID", style="cyan", no_wrap=True)
        done_table.add_column("Task", style="white")

        # Populate Backlog column
        for task in todo:
            priority = task.get("priority", "medium")
            priority_color = priority_colors.get(priority, "white")
            backlog_table.add_row(
                task["id"], f"[{priority_color}]{task['content']}[/{priority_color}]"
            )

        # Populate In Progress column
        for task in in_progress:
            priority = task.get("priority", "medium")
            priority_color = priority_colors.get(priority, "white")
            in_progress_table.add_row(
                task["id"], f"[{priority_color}]{task['content']}[/{priority_color}]"
            )

        # Populate Review column
        for task in review:
            priority = task.get("priority", "medium")
            priority_color = priority_colors.get(priority, "white")
            review_table.add_row(
                task["id"], f"[{priority_color}]{task['content']}[/{priority_color}]"
            )

        # Populate Done column if requested
        if all:
            for task in done:
                done_table.add_row(task["id"], task["content"])

        # Create the board layout
        board_table = Table(box=None, show_header=False, padding=1)
        board_table.add_column("Backlog")
        board_table.add_column("In Progress")
        board_table.add_column("Review")
        board_table.add_column("Done")

        board_table.add_row(backlog_table, in_progress_table, review_table, done_table)
        console.print(board_table)

    # Command hints
    console.print("\n[dim]Commands:[/dim]")
    console.print("[dim]• Move task: logbuch task -m <id> <board>[/dim]")
    console.print("[dim]• Complete task: logbuch task -c <id>[/dim]")
    console.print('[dim]• Add task: logbuch task "Task description" -b <board>[/dim]')


@kanban.command(short_help="Move task to different board")
@click.argument("task_id")
@click.argument("board")
def move(task_id, board):
    storage = Storage()

    # Update the task's board
    with sqlite3.connect(storage.db_path) as conn:
        # Ensure the board exists
        conn.execute("INSERT OR IGNORE INTO boards (name) VALUES (?)", (board,))

        cursor = conn.execute(
            "UPDATE tasks SET board = ? WHERE id = ?", (board, task_id)
        )

        if cursor.rowcount == 0:
            console.print(f"[red]Task with ID {task_id} not found[/red]")
            return

        conn.commit()

    console.print(f"[green]Task {task_id} moved to board '{board}'[/green]")


@kanban.command(short_help="Create a new board")
@click.argument("name")
def create(name):
    storage = Storage()

    # Add the board to the database
    with sqlite3.connect(storage.db_path) as conn:
        conn.execute("INSERT OR IGNORE INTO boards (name) VALUES (?)", (name,))
        conn.commit()

    console.print(f"[green]Board '{name}' created[/green]")
    console.print(
        f'[dim]Add tasks to this board with: logbuch task "Task description" --board {name}[/dim]'
    )
