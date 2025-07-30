#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 30.06.25, 08:14.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import pytest
from unittest.mock import Mock, patch
from logbuch.storage import Storage, add_task, list_tasks


class TestStorage:
    def test_storage_initialization(self, storage):
        assert isinstance(storage, Storage)
        assert storage.db_path is not None
    
    def test_add_task(self, storage, sample_task):
        task = add_task(
            storage,
            sample_task["content"],
            sample_task["priority"],
            sample_task["tags"],
            sample_task["due_date"],
            sample_task["board"]
        )
        
        assert task["content"] == sample_task["content"]
        assert task["priority"] == sample_task["priority"]
        assert task["board"] == sample_task["board"]
        assert "id" in task
    
    def test_list_tasks(self, storage, sample_task):
        # Add a task first
        add_task(
            storage,
            sample_task["content"],
            sample_task["priority"],
            sample_task["tags"],
            sample_task["due_date"],
            sample_task["board"]
        )
        
        tasks = list_tasks(storage)
        assert len(tasks) >= 1
        assert any(task["content"] == sample_task["content"] for task in tasks)
    
    def test_task_completion(self, storage, sample_task):
        # Add a task
        task = add_task(
            storage,
            sample_task["content"],
            sample_task["priority"]
        )
        
        # Complete the task
        from logbuch.storage import complete_task
        completed_task = complete_task(storage, task["id"])
        
        assert completed_task is not None
        assert completed_task["done"] is True
    
    def test_task_deletion(self, storage, sample_task):
        # Add a task
        task = add_task(
            storage,
            sample_task["content"],
            sample_task["priority"]
        )
        
        # Delete the task
        from logbuch.storage import delete_task
        deleted_task = delete_task(storage, task["id"])
        
        assert deleted_task is not None
        
        # Verify it's gone
        tasks = list_tasks(storage)
        assert not any(t["id"] == task["id"] for t in tasks)


class TestJournalFunctionality:
    def test_add_journal_entry(self, storage, sample_journal_entry):
        from logbuch.storage import add_journal_entry
        
        entry = add_journal_entry(
            storage,
            sample_journal_entry["text"],
            sample_journal_entry["tags"],
            sample_journal_entry["category"]
        )
        
        assert entry["text"] == sample_journal_entry["text"]
        assert entry["category"] == sample_journal_entry["category"]
        assert "id" in entry
        assert "date" in entry
    
    def test_list_journal_entries(self, storage, sample_journal_entry):
        from logbuch.storage import add_journal_entry, get_journal_entries
        
        # Add an entry
        add_journal_entry(
            storage,
            sample_journal_entry["text"],
            sample_journal_entry["tags"],
            sample_journal_entry["category"]
        )
        
        entries = get_journal_entries(storage)
        assert len(entries) >= 1
        assert any(entry["text"] == sample_journal_entry["text"] for entry in entries)


class TestMoodTracking:
    def test_add_mood_entry(self, storage, sample_mood_entry):
        from logbuch.storage import add_mood_entry
        
        entry = add_mood_entry(
            storage,
            sample_mood_entry["mood"],
            sample_mood_entry["notes"]
        )
        
        assert entry["mood"] == sample_mood_entry["mood"]
        assert entry["notes"] == sample_mood_entry["notes"]
        assert "id" in entry
        assert "date" in entry
    
    def test_get_mood_entries(self, storage, sample_mood_entry):
        from logbuch.storage import add_mood_entry, get_mood_entries
        
        # Add a mood entry
        add_mood_entry(
            storage,
            sample_mood_entry["mood"],
            sample_mood_entry["notes"]
        )
        
        entries = get_mood_entries(storage)
        assert len(entries) >= 1
        assert any(entry["mood"] == sample_mood_entry["mood"] for entry in entries)


class TestErrorHandling:
    def test_invalid_task_id(self, storage):
        from logbuch.storage import complete_task, delete_task
        
        # Test with non-existent ID
        result = complete_task(storage, 99999)
        assert result is None
        
        result = delete_task(storage, 99999)
        assert result is None
    
    def test_empty_task_content(self, storage):
        with pytest.raises(ValueError):
            add_task(storage, "", "medium")
    
    def test_invalid_priority(self, storage):
        # Should default to medium or handle gracefully
        task = add_task(storage, "Test task", "invalid_priority")
        assert task["priority"] in ["low", "medium", "high"]


class TestDataValidation:
    def test_task_content_validation(self, storage):
        # Test with None
        with pytest.raises((ValueError, TypeError)):
            add_task(storage, None, "medium")
        
        # Test with empty string
        with pytest.raises(ValueError):
            add_task(storage, "", "medium")
        
        # Test with whitespace only
        with pytest.raises(ValueError):
            add_task(storage, "   ", "medium")
    
    def test_priority_validation(self, storage):
        valid_priorities = ["low", "medium", "high"]
        
        for priority in valid_priorities:
            task = add_task(storage, f"Test task {priority}", priority)
            assert task["priority"] == priority
    
    def test_date_validation(self, storage):
        # Test valid date
        task = add_task(storage, "Test task", "medium", due_date="2025-12-31")
        assert task["due_date"] is not None
        
        # Test invalid date format should be handled gracefully
        task = add_task(storage, "Test task", "medium", due_date="invalid-date")
        # Should either reject or handle gracefully
