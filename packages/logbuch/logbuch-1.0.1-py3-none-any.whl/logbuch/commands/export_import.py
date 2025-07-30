#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/export_import.py

import json
import csv
import datetime
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


def export_data(storage, format_type='json', output_file=None, data_type='all'):
    console = Console()
    
    if not output_file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"logbuch_export_{timestamp}.{format_type}"
    
    output_path = Path(output_file)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Collecting data...", total=None)
        
        # Collect data based on type
        export_data = {}
        
        if data_type in ['all', 'tasks']:
            export_data['tasks'] = storage.get_tasks()
        
        if data_type in ['all', 'journal']:
            export_data['journal_entries'] = storage.get_journal_entries(limit=10000)
        
        if data_type in ['all', 'moods']:
            export_data['mood_entries'] = storage.get_mood_entries(limit=10000)
        
        if data_type in ['all', 'sleep']:
            export_data['sleep_entries'] = storage.get_sleep_entries(limit=10000)
        
        if data_type in ['all', 'goals']:
            export_data['goals'] = storage.get_goals()
        
        progress.update(task, description=f"Exporting to {format_type.upper()}...")
        
        # Export based on format
        if format_type == 'json':
            export_json(export_data, output_path)
        elif format_type == 'csv':
            export_csv(export_data, output_path, data_type)
        elif format_type == 'markdown':
            export_markdown(export_data, output_path)
        elif format_type == 'txt':
            export_txt(export_data, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    file_size = output_path.stat().st_size / 1024  # KB
    rprint(f"[green]✅ Data exported successfully![/green]")
    rprint(f"[blue]📁 File: {output_path}[/blue]")
    rprint(f"[blue]💾 Size: {file_size:.1f} KB[/blue]")
    rprint(f"[blue]📊 Format: {format_type.upper()}[/blue]")
    
    return output_path


def export_json(data, output_path):
    export_structure = {
        "exported_at": datetime.datetime.now().isoformat(),
        "source": "Logbuch",
        "version": "1.0",
        "data": data
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_structure, f, indent=2, ensure_ascii=False)


def export_csv(data, output_path, data_type):
    if data_type == 'tasks' and 'tasks' in data:
        export_tasks_csv(data['tasks'], output_path)
    elif data_type == 'journal' and 'journal_entries' in data:
        export_journal_csv(data['journal_entries'], output_path)
    elif data_type == 'moods' and 'mood_entries' in data:
        export_moods_csv(data['mood_entries'], output_path)
    else:
        # Export all as separate CSV files
        base_path = output_path.with_suffix('')
        
        if 'tasks' in data:
            export_tasks_csv(data['tasks'], f"{base_path}_tasks.csv")
        if 'journal_entries' in data:
            export_journal_csv(data['journal_entries'], f"{base_path}_journal.csv")
        if 'mood_entries' in data:
            export_moods_csv(data['mood_entries'], f"{base_path}_moods.csv")


def export_tasks_csv(tasks, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Content', 'Priority', 'Status', 'Board', 'Due Date', 'Created At', 'Tags'])
        
        for task in tasks:
            writer.writerow([
                task.get('id', ''),
                task.get('content', ''),
                task.get('priority', ''),
                'Done' if task.get('done') else 'Pending',
                task.get('board', ''),
                task.get('due_date', ''),
                task.get('created_at', ''),
                ', '.join(task.get('tags', []))
            ])


def export_journal_csv(entries, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Text', 'Category', 'Tags'])
        
        for entry in entries:
            writer.writerow([
                entry.get('date', ''),
                entry.get('text', ''),
                entry.get('category', ''),
                ', '.join(entry.get('tags', []))
            ])


def export_moods_csv(moods, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Mood', 'Notes'])
        
        for mood in moods:
            writer.writerow([
                mood.get('date', ''),
                mood.get('mood', ''),
                mood.get('notes', '')
            ])


def export_markdown(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Logbuch Export\n\n")
        f.write(f"Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Tasks
        if 'tasks' in data:
            f.write("## 📋 Tasks\n\n")
            for task in data['tasks']:
                status = "✅" if task.get('done') else "⏳"
                f.write(f"- {status} **{task.get('content', '')}** ")
                f.write(f"({task.get('priority', 'medium')} priority)")
                if task.get('due_date'):
                    f.write(f" - Due: {task['due_date'][:10]}")
                f.write("\n")
            f.write("\n")
        
        # Journal
        if 'journal_entries' in data:
            f.write("## 📝 Journal Entries\n\n")
            for entry in data['journal_entries']:
                date_str = entry.get('date', '')[:10]
                f.write(f"### {date_str}\n\n")
                f.write(f"{entry.get('text', '')}\n\n")
                if entry.get('tags'):
                    f.write(f"*Tags: {', '.join(entry['tags'])}*\n\n")
        
        # Moods
        if 'mood_entries' in data:
            f.write("## 😊 Mood Entries\n\n")
            for mood in data['mood_entries']:
                date_str = mood.get('date', '')[:10]
                f.write(f"- **{date_str}**: {mood.get('mood', '')}")
                if mood.get('notes'):
                    f.write(f" - {mood['notes']}")
                f.write("\n")
            f.write("\n")
        
        # Goals
        if 'goals' in data:
            f.write("## 🎯 Goals\n\n")
            for goal in data['goals']:
                status = "✅" if goal.get('completed') else "⏳"
                f.write(f"- {status} {goal.get('description', '')} ")
                f.write(f"({goal.get('progress', 0)}%)")
                if goal.get('target_date'):
                    f.write(f" - Target: {goal['target_date'][:10]}")
                f.write("\n")


def export_txt(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("LOKBUCH EXPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Tasks
        if 'tasks' in data:
            f.write("TASKS\n")
            f.write("-" * 20 + "\n")
            for task in data['tasks']:
                status = "[DONE]" if task.get('done') else "[TODO]"
                f.write(f"{status} {task.get('content', '')}\n")
                f.write(f"  Priority: {task.get('priority', 'medium')}\n")
                if task.get('due_date'):
                    f.write(f"  Due: {task['due_date'][:10]}\n")
                f.write("\n")
        
        # Journal
        if 'journal_entries' in data:
            f.write("JOURNAL ENTRIES\n")
            f.write("-" * 20 + "\n")
            for entry in data['journal_entries']:
                date_str = entry.get('date', '')[:10]
                f.write(f"{date_str}:\n")
                f.write(f"{entry.get('text', '')}\n\n")
        
        # Moods
        if 'mood_entries' in data:
            f.write("MOOD ENTRIES\n")
            f.write("-" * 20 + "\n")
            for mood in data['mood_entries']:
                date_str = mood.get('date', '')[:10]
                f.write(f"{date_str}: {mood.get('mood', '')}")
                if mood.get('notes'):
                    f.write(f" ({mood['notes']})")
                f.write("\n")


def import_data(storage, import_file, data_type='all', merge=True):
    console = Console()
    import_path = Path(import_file)
    
    if not import_path.exists():
        rprint(f"[red]❌ File not found: {import_file}[/red]")
        return False
    
    file_extension = import_path.suffix.lower()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Reading import file...", total=None)
        
        try:
            if file_extension == '.json':
                imported_data = import_json(import_path)
            elif file_extension == '.csv':
                imported_data = import_csv(import_path, data_type)
            else:
                rprint(f"[red]❌ Unsupported file format: {file_extension}[/red]")
                return False
            
            progress.update(task, description="Importing data...")
            
            # Import data
            imported_counts = {}
            
            if 'tasks' in imported_data and data_type in ['all', 'tasks']:
                count = import_tasks(storage, imported_data['tasks'])
                imported_counts['tasks'] = count
            
            if 'journal_entries' in imported_data and data_type in ['all', 'journal']:
                count = import_journal_entries(storage, imported_data['journal_entries'])
                imported_counts['journal_entries'] = count
            
            if 'mood_entries' in imported_data and data_type in ['all', 'moods']:
                count = import_mood_entries(storage, imported_data['mood_entries'])
                imported_counts['mood_entries'] = count
            
            if 'goals' in imported_data and data_type in ['all', 'goals']:
                count = import_goals(storage, imported_data['goals'])
                imported_counts['goals'] = count
            
            progress.update(task, description="Import complete!")
        
        except Exception as e:
            rprint(f"[red]❌ Import failed: {e}[/red]")
            return False
    
    rprint(f"[green]✅ Data imported successfully![/green]")
    for data_name, count in imported_counts.items():
        rprint(f"[blue]📊 {data_name}: {count} items imported[/blue]")
    
    return True


def import_json(import_path):
    with open(import_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if 'data' in data:
        return data['data']
    else:
        return data


def import_csv(import_path, data_type):
    imported_data = {}
    
    with open(import_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        # Try to detect data type from headers
        headers = reader.fieldnames if hasattr(reader, 'fieldnames') else []
        
        if 'Content' in headers and 'Priority' in headers:
            # Tasks CSV
            imported_data['tasks'] = []
            for row in rows:
                task = {
                    'content': row.get('Content', ''),
                    'priority': row.get('Priority', 'medium'),
                    'done': row.get('Status', '').lower() == 'done',
                    'board': row.get('Board', 'default'),
                    'due_date': row.get('Due Date', ''),
                    'tags': [tag.strip() for tag in row.get('Tags', '').split(',') if tag.strip()]
                }
                imported_data['tasks'].append(task)
        
        elif 'Text' in headers and 'Date' in headers:
            # Journal CSV
            imported_data['journal_entries'] = []
            for row in rows:
                entry = {
                    'text': row.get('Text', ''),
                    'date': row.get('Date', ''),
                    'category': row.get('Category', ''),
                    'tags': [tag.strip() for tag in row.get('Tags', '').split(',') if tag.strip()]
                }
                imported_data['journal_entries'].append(entry)
        
        elif 'Mood' in headers:
            # Mood CSV
            imported_data['mood_entries'] = []
            for row in rows:
                mood = {
                    'mood': row.get('Mood', ''),
                    'date': row.get('Date', ''),
                    'notes': row.get('Notes', '')
                }
                imported_data['mood_entries'].append(mood)
    
    return imported_data


def import_tasks(storage, tasks):
    count = 0
    for task_data in tasks:
        try:
            storage.add_task(
                task_data.get('content', ''),
                priority=task_data.get('priority', 'medium'),
                tags=task_data.get('tags'),
                due_date=task_data.get('due_date'),
                board=task_data.get('board', 'default')
            )
            count += 1
        except Exception as e:
            continue  # Skip invalid tasks
    return count


def import_journal_entries(storage, entries):
    count = 0
    for entry_data in entries:
        try:
            storage.add_journal_entry(
                entry_data.get('text', ''),
                tags=entry_data.get('tags'),
                category=entry_data.get('category')
            )
            count += 1
        except Exception as e:
            continue  # Skip invalid entries
    return count


def import_mood_entries(storage, moods):
    count = 0
    for mood_data in moods:
        try:
            storage.add_mood_entry(
                mood_data.get('mood', ''),
                notes=mood_data.get('notes')
            )
            count += 1
        except Exception as e:
            continue  # Skip invalid moods
    return count


def import_goals(storage, goals):
    count = 0
    for goal_data in goals:
        try:
            storage.add_goal(
                goal_data.get('description', ''),
                target_date=goal_data.get('target_date')
            )
            count += 1
        except Exception as e:
            continue  # Skip invalid goals
    return count
