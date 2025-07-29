#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/projects.py

import datetime
from rich.table import Table
from rich.console import Console
from rich import print as rprint
from rich.progress import Progress, BarColumn, TextColumn


def create_project(storage, name, description="", deadline=None):
    project_data = {
        'name': name,
        'description': description,
        'deadline': deadline,
        'created_at': datetime.datetime.now().isoformat(),
        'status': 'active',
        'progress': 0
    }
    
    # For now, store as a special goal (we'd need to extend storage for proper projects)
    project = storage.add_goal(f"PROJECT: {name}", deadline or "2025-12-31 23:59")
    rprint(f"[green]📁 Project created: {name}[/green]")
    return project


def list_projects(storage):
    console = Console()
    
    # Get goals that are projects (start with "PROJECT:")
    goals = storage.get_goals()
    projects = [g for g in goals if g['description'].startswith('PROJECT:')]
    
    if not projects:
        rprint("[yellow]No projects found. Create one with: logbuch project create \"Project Name\"[/yellow]")
        return
    
    table = Table(title="📁 Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Progress", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Deadline", style="blue")
    
    for project in projects:
        name = project['description'].replace('PROJECT: ', '')
        progress_bar = "█" * (project.get('progress', 0) // 10) + "░" * (10 - (project.get('progress', 0) // 10))
        status = "✅ Complete" if project.get('completed') else "🔄 Active"
        
        deadline = ""
        if project.get('target_date'):
            try:
                date_obj = datetime.datetime.fromisoformat(project['target_date'].replace('Z', '+00:00'))
                deadline = date_obj.strftime('%m-%d')
            except:
                deadline = project.get('target_date', '')[:10]
        
        table.add_row(
            project['id'],
            name,
            f"{progress_bar} {project.get('progress', 0)}%",
            status,
            deadline
        )
    
    console.print(table)


def show_project_details(storage, project_id):
    console = Console()
    
    # Get project
    goals = storage.get_goals()
    project = None
    for g in goals:
        if g['id'] == project_id and g['description'].startswith('PROJECT:'):
            project = g
            break
    
    if not project:
        rprint(f"[red]Project {project_id} not found[/red]")
        return
    
    name = project['description'].replace('PROJECT: ', '')
    
    console.print(f"\n[bold cyan]📁 Project: {name}[/bold cyan]")
    console.print(f"[blue]ID:[/blue] {project['id']}")
    console.print(f"[blue]Progress:[/blue] {project.get('progress', 0)}%")
    console.print(f"[blue]Status:[/blue] {'✅ Complete' if project.get('completed') else '🔄 Active'}")
    
    if project.get('target_date'):
        console.print(f"[blue]Deadline:[/blue] {project['target_date'][:10]}")
    
    # Show related tasks (tasks with project name in content or tags)
    tasks = storage.get_tasks()
    related_tasks = []
    
    for task in tasks:
        if (name.lower() in task['content'].lower() or 
            (task.get('tags') and any(name.lower() in tag.lower() for tag in task['tags']))):
            related_tasks.append(task)
    
    if related_tasks:
        console.print(f"\n[bold]📋 Related Tasks ({len(related_tasks)}):[/bold]")
        task_table = Table()
        task_table.add_column("ID", style="cyan")
        task_table.add_column("Task", style="white")
        task_table.add_column("Status", style="green")
        task_table.add_column("Priority", style="yellow")
        
        for task in related_tasks[:10]:  # Show max 10
            status = "✅" if task.get('done') else "⏳"
            task_table.add_row(
                task['id'],
                task['content'][:50] + ('...' if len(task['content']) > 50 else ''),
                status,
                task.get('priority', 'medium')
            )
        
        console.print(task_table)
    
    # Calculate project health
    if related_tasks:
        completed_tasks = len([t for t in related_tasks if t.get('done')])
        total_tasks = len(related_tasks)
        task_completion = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        console.print(f"\n[bold]📊 Project Health:[/bold]")
        console.print(f"Tasks: {completed_tasks}/{total_tasks} completed ({task_completion:.1f}%)")
        
        # Suggest progress update
        if abs(task_completion - project.get('progress', 0)) > 10:
            suggested_progress = int(task_completion)
            console.print(f"[yellow]💡 Suggested progress update: {suggested_progress}%[/yellow]")
            console.print(f"[dim]Run: logbuch goal -p {suggested_progress} -g {project_id}[/dim]")


def project_timeline(storage):
    console = Console()
    
    goals = storage.get_goals()
    projects = [g for g in goals if g['description'].startswith('PROJECT:')]
    
    if not projects:
        rprint("[yellow]No projects found[/yellow]")
        return
    
    # Sort by deadline
    projects_with_dates = []
    projects_without_dates = []
    
    for project in projects:
        if project.get('target_date'):
            try:
                date_obj = datetime.datetime.fromisoformat(project['target_date'].replace('Z', '+00:00'))
                projects_with_dates.append((project, date_obj))
            except:
                projects_without_dates.append(project)
        else:
            projects_without_dates.append(project)
    
    projects_with_dates.sort(key=lambda x: x[1])
    
    console.print("[bold cyan]📅 Project Timeline[/bold cyan]\n")
    
    today = datetime.date.today()
    
    for project, deadline in projects_with_dates:
        name = project['description'].replace('PROJECT: ', '')
        days_left = (deadline.date() - today).days
        
        if days_left < 0:
            status_color = "red"
            status_text = f"⚠️ {abs(days_left)} days overdue"
        elif days_left == 0:
            status_color = "yellow"
            status_text = "🔥 Due today!"
        elif days_left <= 7:
            status_color = "yellow"
            status_text = f"⏰ {days_left} days left"
        else:
            status_color = "green"
            status_text = f"📅 {days_left} days left"
        
        progress = project.get('progress', 0)
        progress_bar = "█" * (progress // 10) + "░" * (10 - (progress // 10))
        
        console.print(f"[bold]{name}[/bold]")
        console.print(f"  {progress_bar} {progress}%")
        console.print(f"  [{status_color}]{status_text}[/{status_color}]")
        console.print(f"  [dim]{deadline.strftime('%Y-%m-%d')}[/dim]\n")
    
    if projects_without_dates:
        console.print("[bold]📋 Projects without deadlines:[/bold]")
        for project in projects_without_dates:
            name = project['description'].replace('PROJECT: ', '')
            progress = project.get('progress', 0)
            progress_bar = "█" * (progress // 10) + "░" * (10 - (progress // 10))
            console.print(f"  • {name} {progress_bar} {progress}%")


def project_stats(storage):
    console = Console()
    
    goals = storage.get_goals()
    projects = [g for g in goals if g['description'].startswith('PROJECT:')]
    
    if not projects:
        rprint("[yellow]No projects found[/yellow]")
        return
    
    # Calculate stats
    total_projects = len(projects)
    completed_projects = len([p for p in projects if p.get('completed')])
    active_projects = total_projects - completed_projects
    
    avg_progress = sum(p.get('progress', 0) for p in projects) / total_projects if total_projects > 0 else 0
    
    # Overdue projects
    today = datetime.date.today()
    overdue_projects = 0
    
    for project in projects:
        if not project.get('completed') and project.get('target_date'):
            try:
                deadline = datetime.datetime.fromisoformat(project['target_date'].replace('Z', '+00:00')).date()
                if deadline < today:
                    overdue_projects += 1
            except:
                pass
    
    table = Table(title="📊 Project Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Projects", str(total_projects))
    table.add_row("Active Projects", str(active_projects))
    table.add_row("Completed Projects", str(completed_projects))
    table.add_row("Average Progress", f"{avg_progress:.1f}%")
    table.add_row("Overdue Projects", str(overdue_projects))
    
    console.print(table)
    
    if overdue_projects > 0:
        console.print(f"\n[red]⚠️ {overdue_projects} project{'s' if overdue_projects > 1 else ''} overdue![/red]")


def suggest_project_tasks(storage, project_name):
    console = Console()
    
    # Common project task templates
    templates = {
        'website': [
            'Design wireframes and mockups',
            'Set up development environment',
            'Implement frontend components',
            'Develop backend API',
            'Write tests',
            'Deploy to production',
            'Set up monitoring and analytics'
        ],
        'app': [
            'Define app requirements',
            'Create user interface designs',
            'Set up project structure',
            'Implement core features',
            'Add user authentication',
            'Test on different devices',
            'Prepare for app store submission'
        ],
        'research': [
            'Define research questions',
            'Literature review',
            'Design methodology',
            'Collect data',
            'Analyze results',
            'Write report',
            'Present findings'
        ],
        'marketing': [
            'Define target audience',
            'Create content strategy',
            'Design marketing materials',
            'Set up social media campaigns',
            'Launch advertising campaigns',
            'Track and analyze metrics',
            'Optimize based on results'
        ]
    }
    
    # Try to match project name to template
    project_lower = project_name.lower()
    suggested_template = None
    
    for template_name, tasks in templates.items():
        if template_name in project_lower:
            suggested_template = template_name
            break
    
    if suggested_template:
        console.print(f"[cyan]💡 Suggested tasks for '{project_name}' ({suggested_template} project):[/cyan]")
        for i, task in enumerate(templates[suggested_template], 1):
            console.print(f"  {i}. {task}")
        
        console.print(f"\n[dim]Add these tasks with project tag:[/dim]")
        console.print(f"[dim]logbuch task \"Task description\" --tags {project_name.lower().replace(' ', '-')}[/dim]")
    else:
        console.print(f"[yellow]No specific template found for '{project_name}'[/yellow]")
        console.print("[cyan]💡 General project tasks to consider:[/cyan]")
        general_tasks = [
            'Define project scope and requirements',
            'Break down into smaller tasks',
            'Set up project timeline',
            'Identify required resources',
            'Create project documentation',
            'Set up regular check-ins',
            'Plan testing and quality assurance',
            'Prepare for project completion'
        ]
        
        for i, task in enumerate(general_tasks, 1):
            console.print(f"  {i}. {task}")
