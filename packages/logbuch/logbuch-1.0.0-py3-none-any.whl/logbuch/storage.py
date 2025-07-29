#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/storage.py

import os
import json
import sqlite3
import datetime
import shutil
from pathlib import Path


class Storage:
    def __init__(self, db_path=None, keep_test_db=False, max_backups=20):
        self.keep_test_db = keep_test_db
        self.max_backups = max_backups
        self.is_test_db = False

        if db_path is None:
            home_dir = Path.home()
            self.storage_dir = home_dir / ".logbuch"
            self.storage_dir.mkdir(exist_ok=True)
            self.db_path = self.storage_dir / "logbuch.db"
        else:
            self.db_path = Path(db_path)
            self.storage_dir = self.db_path.parent

            # Check if this is likely a test database
            if "test" in str(db_path).lower() or "temp" in str(db_path).lower():
                self.is_test_db = True

        self.backup_dir = self.storage_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Initialize database
        self._init_db()

        # Verify database integrity
        if self.db_path.exists() and self.db_path.stat().st_size > 0:
            self._verify_integrity()

    def _init_db(self):
        create_tables = """
        -- Config table
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        
        -- Journal entries
        CREATE TABLE IF NOT EXISTS journal_entries (
            id TEXT PRIMARY KEY,
            date TEXT,
            text TEXT,
            category TEXT
        );
        
        -- Tags for journal entries
        CREATE TABLE IF NOT EXISTS journal_tags (
            entry_id TEXT,
            tag TEXT,
            PRIMARY KEY (entry_id, tag),
            FOREIGN KEY (entry_id) REFERENCES journal_entries(id)
        );
        
        -- Tasks
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            content TEXT,
            board TEXT DEFAULT 'default',
            priority TEXT DEFAULT 'medium',
            done BOOLEAN DEFAULT 0,
            created_at TEXT,
            completed_at TEXT,
            due_date TEXT
        );
        
        -- Tags for tasks
        CREATE TABLE IF NOT EXISTS task_tags (
            task_id TEXT,
            tag TEXT,
            PRIMARY KEY (task_id, tag),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );
        
        -- Boards
        CREATE TABLE IF NOT EXISTS boards (
            name TEXT PRIMARY KEY
        );
        
        -- Mood Tracking
        CREATE TABLE IF NOT EXISTS mood_entries (
            id TEXT PRIMARY KEY,
            mood TEXT,
            date TEXT,
            notes TEXT
        );
        
        -- Sleep Tracking
        CREATE TABLE IF NOT EXISTS sleep_entries (
            id TEXT PRIMARY KEY,
            hours REAL,
            date TEXT,
            notes TEXT
        );
        
        -- Goals
        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            description TEXT,
            created_date TEXT,
            target_date TEXT,
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            completed_date TEXT
        );
        
        -- Time Tracking
        CREATE TABLE IF NOT EXISTS time_entries (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER, -- Duration in seconds
            date TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        );
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(create_tables)

            # Add default board if not exists
            conn.execute("INSERT OR IGNORE INTO boards (name) VALUES (?)", ("default",))

            # Initialize default config values
            config_defaults = [
                ("displayCompleteTasks", "true"),
                ("displayProgressOverview", "true"),
                ("defaultBoard", "default"),
                ("defaultPriority", "medium"),
                ("backupFrequency", "daily"),
                ("dateFormat", "%d:%m"),
                ("editor", os.environ.get("EDITOR", "nano")),
            ]

            conn.executemany(
                "INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
                config_defaults,
            )

            conn.commit()

    def _verify_integrity(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()

                if result[0] != "ok":
                    print(f"Warning: Database integrity check failed: {result[0]}")
                    # Auto-recover by restoring from most recent backup
                    latest_backup = self._get_latest_backup()
                    if latest_backup:
                        self._restore_from_backup(latest_backup)
                    else:
                        print("No backup available for recovery")

            return True
        except Exception as e:
            print(f"Error during integrity check: {e}")
            return False

    def _get_all_backups(self):
        backups = list(self.backup_dir.glob("logbuch-*.db"))
        return sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)

    def _get_latest_backup(self):
        backups = self._get_all_backups()
        return backups[0] if backups else None

    def _rotate_backups(self):
        if not self.is_test_db or self.keep_test_db:
            backups = self._get_all_backups()
            if len(backups) > self.max_backups:
                for old_backup in backups[self.max_backups :]:
                    try:
                        old_backup.unlink()
                    except Exception as e:
                        print(f"Error deleting old backup {old_backup}: {e}")

    def _create_backup(self):
        # Don't create backups for test databases unless keep_test_db is True
        if self.is_test_db and not self.keep_test_db:
            return None

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        backup_path = self.backup_dir / f"logbuch-{timestamp}.db"

        try:
            # Wait for any pending write operations to complete
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA wal_checkpoint")

            # Create the backup copy
            shutil.copy2(self.db_path, backup_path)

            # Rotate old backups
            self._rotate_backups()

            return str(backup_path)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    def restore_from_backup(self, backup_path=None):
        if backup_path:
            backup_file = Path(backup_path)
        else:
            backup_file = self._get_latest_backup()

        return self._restore_from_backup(backup_file)

    def _restore_from_backup(self, backup_file):
        if not backup_file or not backup_file.exists():
            print("Backup file not found")
            return False

        try:
            # Create a backup of current db before restoration (just in case)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            pre_restore_backup = self.backup_dir / f"pre-restore-{timestamp}.db"

            # Only backup the current DB if it exists and has content
            if self.db_path.exists() and self.db_path.stat().st_size > 0:
                shutil.copy2(self.db_path, pre_restore_backup)

            # Restore from backup
            shutil.copy2(backup_file, self.db_path)

            # Verify the restored database
            self._verify_integrity()

            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False

    # Journal methods
    def add_journal_entry(self, text, tags=None, category=None):
        date = datetime.datetime.now().isoformat()

        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the next available ID
                cursor = conn.execute(
                    "SELECT MAX(CAST(id AS INTEGER)) FROM journal_entries"
                )
                result = cursor.fetchone()[0]
                entry_id = "1" if result is None else str(int(result) + 1)

                # Insert the journal entry
                conn.execute(
                    "INSERT INTO journal_entries (id, date, text, category) VALUES (?, ?, ?, ?)",
                    (entry_id, date, text, category),
                )

                # Insert tags if provided
                if tags:
                    if isinstance(tags, str):
                        tag_list = [t.strip() for t in tags.split(",")]
                    else:
                        tag_list = tags

                    for tag in tag_list:
                        conn.execute(
                            "INSERT INTO journal_tags (entry_id, tag) VALUES (?, ?)",
                            (entry_id, tag),
                        )

                conn.commit()

            # Return the created entry
            return {
                "id": entry_id,
                "date": date,
                "text": text,
                "tags": tag_list if tags else [],
                "category": category,
            }
        except Exception as e:
            print(f"Error adding journal entry: {e}")
            return None

    def get_journal_entries(self, limit=None, tag=None, category=None, date=None):
        try:
            query = """
            SELECT e.id, e.date, e.text, e.category, GROUP_CONCAT(t.tag) as tags
            FROM journal_entries e
            LEFT JOIN journal_tags t ON e.id = t.entry_id
            """

            params = []
            where_clauses = []

            if tag:
                where_clauses.append(
                    "e.id IN (SELECT entry_id FROM journal_tags WHERE tag = ?)"
                )
                params.append(tag)

            if category:
                where_clauses.append("e.category = ?")
                params.append(category)

            if date:
                if date == "today":
                    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                elif date == "yesterday":
                    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                    date_str = yesterday.strftime("%Y-%m-%d")
                else:
                    date_str = date

                where_clauses.append("date(e.date) = date(?)")
                params.append(date_str)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " GROUP BY e.id ORDER BY e.date DESC"

            if limit:
                query += " LIMIT ?"
                params.append(int(limit))

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)

                entries = []
                for row in cursor:
                    entry = dict(row)
                    entry["tags"] = entry["tags"].split(",") if entry["tags"] else []
                    entries.append(entry)

                return entries
        except Exception as e:
            print(f"Error getting journal entries: {e}")
            return []

    # Task methods
    def add_task(
        self, content, priority=None, tags=None, due_date=None, board="default"
    ):
        created_at = datetime.datetime.now().isoformat()

        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Ensure the board exists
                conn.execute("INSERT OR IGNORE INTO boards (name) VALUES (?)", (board,))

                # Get the next available ID
                cursor = conn.execute("SELECT MAX(CAST(id AS INTEGER)) FROM tasks")
                result = cursor.fetchone()[0]
                task_id = "1" if result is None else str(int(result) + 1)

                # Insert the task
                conn.execute(
                    """INSERT INTO tasks 
                       (id, content, board, priority, done, created_at, due_date) 
                       VALUES (?, ?, ?, ?, 0, ?, ?)""",
                    (
                        task_id,
                        content,
                        board,
                        priority or "medium",
                        created_at,
                        due_date,
                    ),
                )

                # Insert tags if provided
                if tags:
                    if isinstance(tags, str):
                        tag_list = [t.strip() for t in tags.split(",")]
                    else:
                        tag_list = tags

                    for tag in tag_list:
                        conn.execute(
                            "INSERT INTO task_tags (task_id, tag) VALUES (?, ?)",
                            (task_id, tag),
                        )

                conn.commit()

            # Return the created task
            return {
                "id": task_id,
                "content": content,
                "board": board,
                "priority": priority or "medium",
                "done": False,
                "created_at": created_at,
                "completed_at": None,
                "due_date": due_date,
                "tags": tag_list if tags else [],
            }
        except Exception as e:
            print(f"Error adding task: {e}")
            return None

    def get_tasks(self, show_completed=False, board=None, priority=None, tag=None):
        try:
            query = """
            SELECT t.id, t.content, t.board, t.priority, t.done, 
                   t.created_at, t.completed_at, t.due_date, GROUP_CONCAT(tt.tag) as tags
            FROM tasks t
            LEFT JOIN task_tags tt ON t.id = tt.task_id
            """

            params = []
            where_clauses = []

            if not show_completed:
                where_clauses.append("t.done = 0")

            if board:
                where_clauses.append("t.board = ?")
                params.append(board)

            if priority:
                where_clauses.append("t.priority = ?")
                params.append(priority)

            if tag:
                where_clauses.append(
                    "t.id IN (SELECT task_id FROM task_tags WHERE tag = ?)"
                )
                params.append(tag)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " GROUP BY t.id"
            query += " ORDER BY "
            query += "CASE t.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, "
            query += "t.due_date IS NULL, t.due_date, t.created_at DESC"

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)

                tasks = []
                for row in cursor:
                    task = dict(row)
                    task["tags"] = task["tags"].split(",") if task["tags"] else []
                    # Convert SQLite integers to booleans
                    task["done"] = bool(task["done"])
                    tasks.append(task)

                return tasks
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []

    def complete_task(self, task_id):
        completed_at = datetime.datetime.now().isoformat()

        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "UPDATE tasks SET done = 1, completed_at = ? WHERE id = ?",
                    (completed_at, task_id),
                )

                if cursor.rowcount == 0:
                    return None  # No task found with this ID

                conn.commit()

                # Get the updated task
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """SELECT t.*, GROUP_CONCAT(tt.tag) as tags 
                       FROM tasks t 
                       LEFT JOIN task_tags tt ON t.id = tt.task_id 
                       WHERE t.id = ? 
                       GROUP BY t.id""",
                    (task_id,),
                )

                task = dict(cursor.fetchone())
                task["tags"] = task["tags"].split(",") if task["tags"] else []
                task["done"] = bool(task["done"])

                return task
        except Exception as e:
            print(f"Error completing task: {e}")
            return None

    def delete_task(self, task_id):
        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the task before deleting it
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """SELECT t.*, GROUP_CONCAT(tt.tag) as tags 
                       FROM tasks t 
                       LEFT JOIN task_tags tt ON t.id = tt.task_id 
                       WHERE t.id = ? 
                       GROUP BY t.id""",
                    (task_id,),
                )

                task_row = cursor.fetchone()
                if not task_row:
                    return None  # No task found with this ID

                task = dict(task_row)

                # Delete task tags
                conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))

                # Delete the task
                conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

                conn.commit()

                # Format the task for return
                task["tags"] = task["tags"].split(",") if task["tags"] else []
                task["done"] = bool(task["done"])

                return task
        except Exception as e:
            print(f"Error deleting task: {e}")
            return None

    def move_task(self, task_id, board):
        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Ensure the board exists
                conn.execute("INSERT OR IGNORE INTO boards (name) VALUES (?)", (board,))

                # Update the task's board
                cursor = conn.execute(
                    "UPDATE tasks SET board = ? WHERE id = ?", (board, task_id)
                )

                if cursor.rowcount == 0:
                    return None  # No task found with this ID

                conn.commit()

                # Get the updated task
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """SELECT t.*, GROUP_CONCAT(tt.tag) as tags 
                       FROM tasks t 
                       LEFT JOIN task_tags tt ON t.id = tt.task_id 
                       WHERE t.id = ? 
                       GROUP BY t.id""",
                    (task_id,),
                )

                task = dict(cursor.fetchone())
                task["tags"] = task["tags"].split(",") if task["tags"] else []
                task["done"] = bool(task["done"])

                return task
        except Exception as e:
            print(f"Error moving task: {e}")
            return None

    # Search functionality
    def search(self, query):
        try:
            results = {"entries": [], "tasks": []}

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Search journal entries
                cursor = conn.execute(
                    """SELECT e.*, GROUP_CONCAT(t.tag) as tags 
                       FROM journal_entries e 
                       LEFT JOIN journal_tags t ON e.id = t.entry_id 
                       WHERE e.text LIKE ? OR e.id IN (SELECT entry_id FROM journal_tags WHERE tag LIKE ?) 
                       GROUP BY e.id""",
                    (f"%{query}%", f"%{query}%"),
                )

                for row in cursor:
                    entry = dict(row)
                    entry["tags"] = entry["tags"].split(",") if entry["tags"] else []
                    results["entries"].append(entry)

                # Search tasks
                cursor = conn.execute(
                    """SELECT t.*, GROUP_CONCAT(tt.tag) as tags 
                       FROM tasks t 
                       LEFT JOIN task_tags tt ON t.id = tt.task_id 
                       WHERE t.content LIKE ? OR t.board LIKE ? OR t.id IN (SELECT task_id FROM task_tags WHERE tag LIKE ?) 
                       GROUP BY t.id""",
                    (f"%{query}%", f"%{query}%", f"%{query}%"),
                )

                for row in cursor:
                    task = dict(row)
                    task["tags"] = task["tags"].split(",") if task["tags"] else []
                    task["done"] = bool(task["done"])
                    results["tasks"].append(task)

            return results
        except Exception as e:
            print(f"Error searching content: {e}")
            return {"entries": [], "tasks": []}

    # Config methods
    def get_config(self, key=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                if key:
                    cursor = conn.execute(
                        "SELECT value FROM config WHERE key = ?", (key,)
                    )
                    row = cursor.fetchone()
                    return row[0] if row else None
                else:
                    cursor = conn.execute("SELECT key, value FROM config")
                    return {row[0]: row[1] for row in cursor}
        except Exception as e:
            print(f"Error getting config: {e}")
            return {} if key is None else None

    def update_config(self, key, value):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                    (key, value),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False

    # Database management methods
    def get_backups(self):
        backups = []
        for backup_file in self._get_all_backups():
            backup_info = {
                "path": str(backup_file),
                "filename": backup_file.name,
                "size": backup_file.stat().st_size,
                "created": datetime.datetime.fromtimestamp(
                    backup_file.stat().st_mtime
                ).isoformat(),
            }
            backups.append(backup_info)
        return backups

    def delete_backup(self, backup_path):
        backup_file = Path(backup_path)

        # Ensure the file is actually in the backup directory to prevent deletion of other files
        if not str(backup_file).startswith(str(self.backup_dir)):
            print("Error: Cannot delete files outside the backup directory")
            return False

        try:
            backup_file.unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False

    def optimize_database(self):
        try:
            # Create a backup before optimization
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA auto_vacuum = FULL")
                conn.execute("VACUUM")
                conn.execute("PRAGMA optimize")
                conn.execute("PRAGMA integrity_check")
            return True
        except Exception as e:
            print(f"Error optimizing database: {e}")
            return False

    def delete_journal_entry(self, entry_id):
        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the entry before deleting it
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """SELECT e.*, GROUP_CONCAT(t.tag) as tags 
                       FROM journal_entries e 
                       LEFT JOIN journal_tags t ON e.id = t.entry_id 
                       WHERE e.id = ? 
                       GROUP BY e.id""",
                    (entry_id,),
                )

                entry_row = cursor.fetchone()
                if not entry_row:
                    return None  # No entry found with this ID

                entry = dict(entry_row)

                # Delete entry tags
                conn.execute("DELETE FROM journal_tags WHERE entry_id = ?", (entry_id,))

                # Delete the entry
                conn.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))

                conn.commit()

                # Format the entry for return
                entry["tags"] = entry["tags"].split(",") if entry["tags"] else []

                return entry
        except Exception as e:
            print(f"Error deleting journal entry: {e}")
            return None

    # Export/Import functionality
    def export_data(self, format="json"):
        try:
            data = {
                "journal": self.get_journal_entries(),
                "tasks": self.get_tasks(show_completed=True),
                "mood_entries": self.get_mood_entries(),
                "sleep_entries": self.get_sleep_entries(),
                "goals": self.get_goals(include_completed=True),
                "time_entries": self.get_time_entries(),
                "config": self.get_config(),
                "export_date": datetime.datetime.now().isoformat(),
                "version": "0.1.0",
            }

            if format == "json":
                return json.dumps(data, indent=2)
            elif format == "markdown":
                md = "# Logbuch Export\n\n"
                md += f"Export Date: {datetime.datetime.now().isoformat()}\n\n"

                md += "## Journal Entries\n\n"
                for entry in data["journal"]:
                    date = entry["date"].split("T")[0]
                    md += f"### {date}\n\n"
                    md += f"{entry['text']}\n\n"
                    if entry["tags"]:
                        md += f"Tags: {', '.join(entry['tags'])}\n\n"

                md += "## Tasks\n\n"
                boards = {}
                for task in data["tasks"]:
                    board = task["board"]
                    if board not in boards:
                        boards[board] = []
                    boards[board].append(task)

                for board, tasks in boards.items():
                    md += f"### {board}\n\n"
                    for task in tasks:
                        status = "[x]" if task["done"] else "[ ]"
                        priority = "!" * (
                            3
                            if task["priority"] == "high"
                            else 2
                            if task["priority"] == "medium"
                            else 1
                        )
                        md += f"- {status} {task['content']} {priority}\n"
                    md += "\n"

                md += "## Mood Entries\n\n"
                for entry in data["mood_entries"]:
                    date = entry["date"].split("T")[0]
                    md += f"- **{date}**: {entry['mood']}"
                    if entry.get("notes"):
                        md += f" - {entry['notes']}"
                    md += "\n"
                md += "\n"

                md += "## Sleep Entries\n\n"
                for entry in data["sleep_entries"]:
                    date = entry["date"].split("T")[0]
                    md += f"- **{date}**: {entry['hours']} hours"
                    if entry.get("notes"):
                        md += f" - {entry['notes']}"
                    md += "\n"
                md += "\n"

                md += "## Goals\n\n"
                for goal in data["goals"]:
                    status = (
                        "Completed"
                        if goal["completed"]
                        else f"In Progress ({goal['progress']}%)"
                    )
                    created = goal["created_date"].split("T")[0]
                    target = goal["target_date"]
                    md += f"### {goal['description']}\n\n"
                    md += f"- Status: {status}\n"
                    md += f"- Created: {created}\n"
                    md += f"- Target Date: {target}\n\n"

                md += "## Time Entries\n\n"
                for entry in data["time_entries"]:
                    date = entry["date"]
                    description = entry.get("description", "")
                    if entry.get("task_content"):
                        description = (
                            f"{entry['task_content']} - {description}"
                            if description
                            else entry["task_content"]
                        )

                    if entry.get("duration_formatted"):
                        md += f"- **{date}**: {description} ({entry['duration_formatted']})\n"
                    else:
                        md += f"- **{date}**: {description} (In progress)\n"
                md += "\n"

                return md

            return None
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None

    # Mood tracking methods
    def add_mood_entry(self, mood, notes=None):
        date = datetime.datetime.now().isoformat()

        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the next available ID
                cursor = conn.execute(
                    "SELECT MAX(CAST(id AS INTEGER)) FROM mood_entries"
                )
                result = cursor.fetchone()[0]
                entry_id = "1" if result is None else str(int(result) + 1)

                conn.execute(
                    "INSERT INTO mood_entries (id, mood, date, notes) VALUES (?, ?, ?, ?)",
                    (entry_id, mood, date, notes),
                )
                conn.commit()

            return {"id": entry_id, "mood": mood, "date": date, "notes": notes}
        except Exception as e:
            print(f"Error adding mood entry: {e}")
            return None

    def get_mood_entries(self, limit=None, date=None):
        try:
            query = "SELECT * FROM mood_entries"
            params = []

            if date:
                if date == "today":
                    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                elif date == "yesterday":
                    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                    date_str = yesterday.strftime("%Y-%m-%d")
                else:
                    date_str = date

                query += " WHERE date(date) = date(?)"
                params.append(date_str)

            query += " ORDER BY date DESC"

            if limit:
                query += " LIMIT ?"
                params.append(int(limit))

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)

                entries = [dict(row) for row in cursor]
                return entries
        except Exception as e:
            print(f"Error getting mood entries: {e}")
            return []

    # Sleep tracking methods
    def add_sleep_entry(self, hours, notes=None):
        date = datetime.datetime.now().isoformat()

        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the next available ID
                cursor = conn.execute(
                    "SELECT MAX(CAST(id AS INTEGER)) FROM sleep_entries"
                )
                result = cursor.fetchone()[0]
                entry_id = "1" if result is None else str(int(result) + 1)

                conn.execute(
                    "INSERT INTO sleep_entries (id, hours, date, notes) VALUES (?, ?, ?, ?)",
                    (entry_id, hours, date, notes),
                )
                conn.commit()

            return {"id": entry_id, "hours": hours, "date": date, "notes": notes}
        except Exception as e:
            print(f"Error adding sleep entry: {e}")
            return None

    def get_sleep_entries(self, limit=None, date=None):
        try:
            query = "SELECT * FROM sleep_entries"
            params = []

            if date:
                if date == "today":
                    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                elif date == "yesterday":
                    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                    date_str = yesterday.strftime("%Y-%m-%d")
                else:
                    date_str = date

                query += " WHERE date(date) = date(?)"
                params.append(date_str)

            query += " ORDER BY date DESC"

            if limit:
                query += " LIMIT ?"
                params.append(int(limit))

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)

                entries = [dict(row) for row in cursor]
                return entries
        except Exception as e:
            print(f"Error getting sleep entries: {e}")
            return []

    # Goal management methods
    def add_goal(self, description, target_date):
        created_date = datetime.datetime.now().isoformat()

        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the next available ID
                cursor = conn.execute("SELECT MAX(CAST(id AS INTEGER)) FROM goals")
                result = cursor.fetchone()[0]
                goal_id = "1" if result is None else str(int(result) + 1)

                conn.execute(
                    """INSERT INTO goals 
                       (id, description, created_date, target_date, progress) 
                       VALUES (?, ?, ?, ?, 0)""",
                    (goal_id, description, created_date, target_date),
                )
                conn.commit()

            return {
                "id": goal_id,
                "description": description,
                "created_date": created_date,
                "target_date": target_date,
                "progress": 0,
                "completed": False,
                "completed_date": None,
            }
        except Exception as e:
            print(f"Error adding goal: {e}")
            return None

    def update_goal_progress(self, goal_id, progress):
        try:
            # Create backup before modification
            self._create_backup()

            # If progress is 100, mark as completed
            completed = progress >= 100
            completed_date = datetime.datetime.now().isoformat() if completed else None

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """UPDATE goals 
                       SET progress = ?, completed = ?, completed_date = ?
                       WHERE id = ?""",
                    (progress, completed, completed_date, goal_id),
                )

                if conn.total_changes == 0:
                    return None  # No goal found with this ID

                conn.commit()

                # Get the updated goal
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
                goal = dict(cursor.fetchone())
                goal["completed"] = bool(goal["completed"])

                return goal
        except Exception as e:
            print(f"Error updating goal progress: {e}")
            return None

    def get_goals(self, include_completed=False):
        try:
            query = "SELECT * FROM goals"
            params = []

            if not include_completed:
                query += " WHERE completed = 0"

            query += " ORDER BY target_date, created_date"

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)

                goals = []
                for row in cursor:
                    goal = dict(row)
                    goal["completed"] = bool(goal["completed"])
                    goals.append(goal)

                return goals
        except Exception as e:
            print(f"Error getting goals: {e}")
            return []

    def delete_goal(self, goal_id):
        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the goal before deleting it
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))

                goal_row = cursor.fetchone()
                if not goal_row:
                    return None  # No goal found with this ID

                goal = dict(goal_row)
                goal["completed"] = bool(goal["completed"])

                # Delete the goal
                conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
                conn.commit()

                return goal
        except Exception as e:
            print(f"Error deleting goal: {e}")
            return None

    def import_data(self, data, format="json"):
        try:
            # Create backup before import
            self._create_backup()

            if format == "json":
                import_data = json.loads(data)

                # Import journal entries
                for entry in import_data.get("journal", []):
                    # Skip entries that already exist
                    existing = self.get_journal_entries(
                        limit=1, tag=None, category=None, date=None
                    )
                    if existing and any(e["id"] == entry["id"] for e in existing):
                        continue

                    self.add_journal_entry(
                        entry["text"], entry.get("tags"), entry.get("category")
                    )

                # Import tasks
                for task in import_data.get("tasks", []):
                    # Skip tasks that already exist
                    existing = self.get_tasks(show_completed=True)
                    if existing and any(t["id"] == task["id"] for t in existing):
                        continue

                    new_task = self.add_task(
                        task["content"],
                        task.get("priority"),
                        task.get("tags"),
                        task.get("due_date"),
                        task.get("board", "default"),
                    )

                    # Mark as completed if needed
                    if task.get("done") and new_task:
                        self.complete_task(new_task["id"])

                # Import mood entries
                for entry in import_data.get("mood_entries", []):
                    self.add_mood_entry(entry["mood"], entry.get("notes"))

                # Import sleep entries
                for entry in import_data.get("sleep_entries", []):
                    self.add_sleep_entry(entry["hours"], entry.get("notes"))

                # Import goals
                for goal in import_data.get("goals", []):
                    new_goal = self.add_goal(goal["description"], goal["target_date"])
                    if new_goal and goal.get("progress"):
                        self.update_goal_progress(new_goal["id"], goal["progress"])

                # Import time entries if available
                for entry in import_data.get("time_entries", []):
                    if entry.get("duration"):
                        # Divide by 60 to convert seconds to minutes
                        duration_minutes = entry["duration"] / 60
                        self.add_time_entry(
                            duration_minutes,
                            entry.get("task_id"),
                            entry.get("description"),
                            entry.get("date"),
                        )

                return True
            else:
                print(f"Unsupported import format: {format}")
                return False

        except Exception as e:
            print(f"Error importing data: {e}")
            return False

    # Time tracking methods
    def start_time_tracking(self, task_id=None, description=None):
        # Check if there's already an active tracking session
        active_session = self.get_current_tracking()
        if active_session:
            print("A time tracking session is already active. Stop it first.")
            return None

        start_time = datetime.datetime.now().isoformat()
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the next available ID
                cursor = conn.execute(
                    "SELECT MAX(CAST(id AS INTEGER)) FROM time_entries"
                )
                result = cursor.fetchone()[0]
                entry_id = "1" if result is None else str(int(result) + 1)

                # If task_id is provided, verify it exists
                if task_id:
                    cursor = conn.execute(
                        "SELECT id FROM tasks WHERE id = ?", (task_id,)
                    )
                    task = cursor.fetchone()
                    if not task:
                        print(f"Task with ID {task_id} not found")
                        return None

                # Create a new time entry with start_time but no end_time or duration yet
                conn.execute(
                    """INSERT INTO time_entries 
                       (id, task_id, description, start_time, date) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (entry_id, task_id, description, start_time, date),
                )
                conn.commit()

            return {
                "id": entry_id,
                "task_id": task_id,
                "description": description,
                "start_time": start_time,
                "end_time": None,
                "duration": None,
                "date": date,
            }
        except Exception as e:
            print(f"Error starting time tracking: {e}")
            return None

    def stop_time_tracking(self):
        try:
            # Find the active tracking session (no end_time)
            active_session = self.get_current_tracking()
            if not active_session:
                print("No active time tracking session found")
                return None

            # Create backup before modification
            self._create_backup()

            entry_id = active_session["id"]
            start_time = datetime.datetime.fromisoformat(active_session["start_time"])
            end_time = datetime.datetime.now()
            end_time_iso = end_time.isoformat()

            # Calculate duration in seconds
            duration = int((end_time - start_time).total_seconds())

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """UPDATE time_entries 
                       SET end_time = ?, duration = ? 
                       WHERE id = ?""",
                    (end_time_iso, duration, entry_id),
                )
                conn.commit()

                # Get the updated entry
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM time_entries WHERE id = ?", (entry_id,)
                )

                entry = dict(cursor.fetchone())

                return entry
        except Exception as e:
            print(f"Error stopping time tracking: {e}")
            return None

    def add_time_entry(self, duration, task_id=None, description=None, date=None):
        try:
            # Create backup before modification
            self._create_backup()

            # Use current date if not specified
            if not date:
                date = datetime.datetime.now().strftime("%Y-%m-%d")

            # Convert duration from minutes to seconds
            duration_seconds = int(duration * 60)

            # Generate start and end times based on current time and duration
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(seconds=duration_seconds)

            with sqlite3.connect(self.db_path) as conn:
                # Get the next available ID
                cursor = conn.execute(
                    "SELECT MAX(CAST(id AS INTEGER)) FROM time_entries"
                )
                result = cursor.fetchone()[0]
                entry_id = "1" if result is None else str(int(result) + 1)

                # If task_id is provided, verify it exists
                if task_id:
                    cursor = conn.execute(
                        "SELECT id FROM tasks WHERE id = ?", (task_id,)
                    )
                    task = cursor.fetchone()
                    if not task:
                        print(f"Task with ID {task_id} not found")
                        return None

                # Create a new completed time entry
                conn.execute(
                    """INSERT INTO time_entries 
                       (id, task_id, description, start_time, end_time, duration, date) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        entry_id,
                        task_id,
                        description,
                        start_time.isoformat(),
                        end_time.isoformat(),
                        duration_seconds,
                        date,
                    ),
                )
                conn.commit()

            return {
                "id": entry_id,
                "task_id": task_id,
                "description": description,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration_seconds,
                "date": date,
            }
        except Exception as e:
            print(f"Error adding time entry: {e}")
            return None

    def get_time_entries(self, limit=None, date=None, task_id=None):
        try:
            query = "SELECT * FROM time_entries"
            params = []
            where_clauses = []

            if date:
                if date == "today":
                    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                elif date == "yesterday":
                    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                    date_str = yesterday.strftime("%Y-%m-%d")
                else:
                    date_str = date

                where_clauses.append("date = ?")
                params.append(date_str)

            if task_id:
                where_clauses.append("task_id = ?")
                params.append(task_id)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            query += " ORDER BY start_time DESC"

            if limit:
                query += " LIMIT ?"
                params.append(int(limit))

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)

                entries = []
                for row in cursor:
                    entry = dict(row)

                    # If a task_id is associated, get the task info
                    if entry["task_id"]:
                        task_cursor = conn.execute(
                            "SELECT content FROM tasks WHERE id = ?",
                            (entry["task_id"],),
                        )
                        task = task_cursor.fetchone()
                        if task:
                            entry["task_content"] = task["content"]

                    # Format duration as human-readable if present
                    if entry["duration"]:
                        minutes, seconds = divmod(entry["duration"], 60)
                        hours, minutes = divmod(minutes, 60)
                        entry["duration_formatted"] = f"{hours}h {minutes}m {seconds}s"
                        entry["duration_minutes"] = round(entry["duration"] / 60, 2)

                    entries.append(entry)

                return entries
        except Exception as e:
            print(f"Error getting time entries: {e}")
            return []

    def get_current_tracking(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM time_entries WHERE end_time IS NULL LIMIT 1"
                )

                entry = cursor.fetchone()
                if entry:
                    result = dict(entry)

                    # Calculate elapsed time so far
                    start_time = datetime.datetime.fromisoformat(result["start_time"])
                    current_time = datetime.datetime.now()
                    elapsed_seconds = int((current_time - start_time).total_seconds())

                    # Format elapsed time
                    minutes, seconds = divmod(elapsed_seconds, 60)
                    hours, minutes = divmod(minutes, 60)
                    result["elapsed_formatted"] = f"{hours}h {minutes}m {seconds}s"
                    result["elapsed_seconds"] = elapsed_seconds

                    # If a task_id is associated, get the task info
                    if result["task_id"]:
                        task_cursor = conn.execute(
                            "SELECT content FROM tasks WHERE id = ?",
                            (result["task_id"],),
                        )
                        task = task_cursor.fetchone()
                        if task:
                            result["task_content"] = task["content"]

                    return result
                return None
        except Exception as e:
            print(f"Error getting current tracking: {e}")
            return None

    def delete_time_entry(self, entry_id):
        try:
            # Create backup before modification
            self._create_backup()

            with sqlite3.connect(self.db_path) as conn:
                # Get the entry before deleting it
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM time_entries WHERE id = ?", (entry_id,)
                )

                entry_row = cursor.fetchone()
                if not entry_row:
                    return None  # No entry found with this ID

                entry = dict(entry_row)

                # Delete the entry
                conn.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
                conn.commit()

                return entry
        except Exception as e:
            print(f"Error deleting time entry: {e}")
            return None
