#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_storage.py
# tests/test_storage.py

import os
import tempfile
from pathlib import Path

import pytest

from logbuch.storage import Storage


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_path = Path(path)
    yield db_path
    # Note: We don't delete the database file here, as it will be managed by the Storage class
    # based on the keep_test_db flag


@pytest.fixture
def storage(temp_db):
    return Storage(db_path=temp_db, keep_test_db=False)


@pytest.fixture
def persistent_storage(temp_db):
    return Storage(db_path=temp_db, keep_test_db=True)


def test_init_db(storage):
    assert storage.db_path.exists()


def test_add_journal_entry(storage):
    # Add a journal entry
    entry = storage.add_journal_entry("Test journal entry", "test,journal")

    # Verify the entry was added
    assert entry is not None
    assert entry["text"] == "Test journal entry"
    assert "test" in entry["tags"]
    assert "journal" in entry["tags"]

    # Retrieve the entry
    entries = storage.get_journal_entries()
    assert len(entries) == 1
    assert entries[0]["text"] == "Test journal entry"


def test_add_task(storage):
    # Add a task
    task = storage.add_task("Test task", "high", "test,task", "2023-12-31")

    # Verify the task was added
    assert task is not None
    assert task["content"] == "Test task"
    assert task["priority"] == "high"
    assert "test" in task["tags"]
    assert "task" in task["tags"]
    assert task["due_date"] == "2023-12-31"

    # Retrieve the task
    tasks = storage.get_tasks()
    assert len(tasks) == 1
    assert tasks[0]["content"] == "Test task"


def test_complete_task(storage):
    # Add a task
    task = storage.add_task("Test task")
    task_id = task["id"]

    # Complete the task
    completed_task = storage.complete_task(task_id)

    # Verify the task was completed
    assert completed_task is not None
    assert completed_task["done"] is True
    assert completed_task["completed_at"] is not None

    # Verify completed tasks don't show up in default task list
    tasks = storage.get_tasks()
    assert len(tasks) == 0

    # Verify completed tasks show up when specifically requested
    tasks = storage.get_tasks(show_completed=True)
    assert len(tasks) == 1
    assert tasks[0]["done"] is True


def test_search(storage):
    # Add some content to search through
    storage.add_journal_entry("Test journal entry about searching", "test,search")
    storage.add_journal_entry("Another entry", "test")
    storage.add_task("Test task with search term", tags="test,search")
    storage.add_task("Another task", tags="test")

    # Search for 'search'
    results = storage.search("search")

    # Verify search results
    assert len(results["entries"]) == 1
    assert "searching" in results["entries"][0]["text"]
    assert len(results["tasks"]) == 1
    assert "search term" in results["tasks"][0]["content"]

    # Search by tag
    results = storage.search("search")
    assert len(results["entries"]) == 1
    assert len(results["tasks"]) == 1


def test_delete_journal_entry(storage):
    # Add a journal entry
    entry = storage.add_journal_entry("Test journal entry to delete", "test,delete")
    entry_id = entry["id"]

    # Verify the entry was added
    entries = storage.get_journal_entries()
    assert len(entries) == 1

    # Delete the entry
    deleted_entry = storage.delete_journal_entry(entry_id)

    # Verify the return value
    assert deleted_entry is not None
    assert deleted_entry["id"] == entry_id
    assert deleted_entry["text"] == "Test journal entry to delete"

    # Verify the entry was deleted
    entries = storage.get_journal_entries()
    assert len(entries) == 0


def test_backup_and_restore(persistent_storage):
    # Add some data to backup
    persistent_storage.add_journal_entry("Test journal entry for backup", "test,backup")
    persistent_storage.add_task("Test task for backup", tags="test,backup")

    # Create a backup
    backup_path = persistent_storage._create_backup()
    assert backup_path is not None

    # Verify the backup was created
    backup_file = Path(backup_path)
    assert backup_file.exists()

    # Add more data
    persistent_storage.add_journal_entry("Another journal entry after backup", "test")

    # Get entries count before restore
    entries_before = len(persistent_storage.get_journal_entries())
    assert entries_before == 2

    # Restore from backup
    success = persistent_storage.restore_from_backup(backup_path)
    assert success

    # Verify data was restored to the state at backup time
    entries_after = persistent_storage.get_journal_entries()
    assert len(entries_after) == 1
    assert entries_after[0]["text"] == "Test journal entry for backup"


def test_database_optimization(persistent_storage):
    # Add some data
    for i in range(5):
        persistent_storage.add_journal_entry(f"Test journal entry {i}", "test")
        persistent_storage.add_task(f"Test task {i}", tags="test")

    # Optimize the database
    success = persistent_storage.optimize_database()
    assert success

    # Verify data is still intact
    entries = persistent_storage.get_journal_entries()
    tasks = persistent_storage.get_tasks()
    assert len(entries) == 5
    assert len(tasks) == 5


def test_backup_management(persistent_storage):
    # Create multiple backups
    backups = []
    for i in range(3):
        persistent_storage.add_journal_entry(f"Journal entry for backup {i}", "test")
        backup_path = persistent_storage._create_backup()
        backups.append(backup_path)

    # Verify backups were created
    assert len(backups) == 3
    for backup in backups:
        assert Path(backup).exists()

    # List backups
    backup_list = persistent_storage.get_backups()
    assert len(backup_list) >= 3  # Might be more if previous tests created backups

    # Delete a backup
    success = persistent_storage.delete_backup(backups[0])
    assert success
    assert not Path(backups[0]).exists()

    # Verify backup was deleted from list
    updated_backup_list = persistent_storage.get_backups()
    assert len(updated_backup_list) == len(backup_list) - 1


def test_export_import(storage):
    # Add some data to export
    storage.add_journal_entry("Test journal entry for export", "test,export")
    storage.add_task("Test task for export", tags="test,export")

    # Export data
    export_data = storage.export_data(format="json")
    assert export_data is not None

    # Create a new storage instance with a different database
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    new_storage = Storage(db_path=Path(path))

    # Import data
    success = new_storage.import_data(export_data)
    assert success

    # Verify data was imported
    entries = new_storage.get_journal_entries()
    tasks = new_storage.get_tasks()
    assert len(entries) == 1
    assert len(tasks) == 1
    assert entries[0]["text"] == "Test journal entry for export"
    assert tasks[0]["content"] == "Test task for export"
