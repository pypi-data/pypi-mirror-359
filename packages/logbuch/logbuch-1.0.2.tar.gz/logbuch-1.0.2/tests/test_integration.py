#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_integration.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import tempfile
import json
import sqlite3
from pathlib import Path

from tests.test_mocks import (
    MockStorage, MockConsole, MockConfig, PerformanceTimer,
    generate_large_test_dataset, create_sample_task_data
)

from logbuch.storage import Storage
from logbuch.commands.task import add_task, list_tasks, complete_task
from logbuch.commands.journal import add_journal_entry, list_journal_entries
from logbuch.commands.mood import add_mood_entry, list_mood_entries
from logbuch.commands.goal import add_goal, update_goal_progress, list_goals


class TestStorageIntegration:
    def test_real_storage_task_workflow(self, temp_dir):
        db_path = temp_dir / "test_integration.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Add tasks
            task_id1 = storage.add_task("Integration test task 1", "high", ["test"])
            task_id2 = storage.add_task("Integration test task 2", "medium", ["test"])
            
            # Verify tasks were added
            tasks = storage.get_tasks()
            assert len(tasks) == 2
            
            # Complete one task
            result = storage.complete_task(task_id1)
            assert result is True
            
            # Verify completion
            active_tasks = storage.get_tasks(show_completed=False)
            completed_tasks = storage.get_tasks(show_completed=True)
            
            assert len(active_tasks) == 1
            assert len(completed_tasks) == 2
            
            # Delete a task
            result = storage.delete_task(task_id2)
            assert result is True
            
            # Verify deletion
            remaining_tasks = storage.get_tasks(show_completed=True)
            assert len(remaining_tasks) == 1
            
        finally:
            # Cleanup
            if db_path.exists():
                db_path.unlink()
    
    def test_real_storage_journal_workflow(self, temp_dir):
        db_path = temp_dir / "test_journal.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Add journal entries
            entry_id1 = storage.add_journal_entry(
                "First integration test entry", 
                ["test", "integration"], 
                "testing"
            )
            entry_id2 = storage.add_journal_entry(
                "Second integration test entry",
                ["test"],
                "testing"
            )
            
            # Verify entries were added
            entries = storage.get_journal_entries()
            assert len(entries) == 2
            
            # Test filtering
            test_entries = storage.get_journal_entries(tag="test")
            assert len(test_entries) == 2
            
            integration_entries = storage.get_journal_entries(tag="integration")
            assert len(integration_entries) == 1
            
            # Test category filtering
            testing_entries = storage.get_journal_entries(category="testing")
            assert len(testing_entries) == 2
            
            # Delete an entry
            result = storage.delete_journal_entry(entry_id1)
            assert result is True
            
            # Verify deletion
            remaining_entries = storage.get_journal_entries()
            assert len(remaining_entries) == 1
            
        finally:
            # Cleanup
            if db_path.exists():
                db_path.unlink()
    
    def test_storage_backup_functionality(self, temp_dir):
        db_path = temp_dir / "test_backup.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Add some data
            storage.add_task("Backup test task", "high")
            storage.add_journal_entry("Backup test entry", ["test"])
            
            # Create backup
            backup_path = storage.create_backup()
            assert backup_path is not None
            assert Path(backup_path).exists()
            
            # Verify backup contains data
            backup_storage = Storage(backup_path, keep_test_db=True)
            backup_tasks = backup_storage.get_tasks()
            backup_entries = backup_storage.get_journal_entries()
            
            assert len(backup_tasks) == 1
            assert len(backup_entries) == 1
            assert backup_tasks[0]['content'] == "Backup test task"
            
        finally:
            # Cleanup
            if db_path.exists():
                db_path.unlink()


class TestCLIIntegration:
    @patch('logbuch.cli.Storage')
    @patch('logbuch.cli.Console')
    def test_cli_task_commands(self, mock_console_class, mock_storage_class):
        mock_storage = MockStorage()
        mock_console = MockConsole()
        mock_storage_class.return_value = mock_storage
        mock_console_class.return_value = mock_console
        
        # Import CLI after mocking
        from logbuch.cli import add_task_command, list_tasks_command
        
        # Test adding task through CLI
        result = add_task_command("Test CLI task", priority="high", tags=["cli", "test"])
        assert result is not None
        
        # Verify task was added
        tasks = mock_storage.get_tasks()
        assert len(tasks) == 1
        assert tasks[0]['content'] == "Test CLI task"
    
    def test_command_context_creation(self):
        from logbuch.cli import CommandContext
        
        with patch('logbuch.storage.Storage') as mock_storage:
            with patch('logbuch.core.config.get_config') as mock_config:
                mock_storage.return_value = MockStorage()
                mock_config.return_value = MockConfig()
                
                context = CommandContext.create()
                
                assert hasattr(context, 'storage')
                assert hasattr(context, 'config')
                assert hasattr(context, 'console')


class TestFeatureIntegration:
    def test_gamification_integration(self, mock_storage):
        with patch('logbuch.features.gamification.GamificationEngine') as mock_gamification:
            mock_engine = Mock()
            mock_rewards = [{'type': 'task_completion', 'points': 10}]
            mock_engine.process_task_completion.return_value = mock_rewards
            mock_gamification.return_value = mock_engine
            
            # Add and complete a task
            task_id = add_task(mock_storage, "Gamification test task", priority="high")
            result = complete_task(mock_storage, task_id)
            
            assert result is True
            mock_engine.process_task_completion.assert_called_once()
    
    def test_notification_integration(self, mock_storage):
        with patch('logbuch.commands.notifications.send_system_notification') as mock_notify:
            mock_notify.return_value = True
            
            # Add a task with due date (would trigger notification in real app)
            task_id = add_task(mock_storage, "Notification test", due_date="2024-12-31")
            
            # In a real integration, this would trigger notifications
            # For now, just verify the task was created
            tasks = list_tasks(mock_storage)
            assert len(tasks) == 1
    
    def test_search_integration(self, mock_storage):
        # Add various content
        add_task(mock_storage, "Important project task", tags=["work", "project"])
        add_task(mock_storage, "Personal shopping task", tags=["personal"])
        add_journal_entry(mock_storage, "Today I worked on an important project", tags=["work"])
        add_journal_entry(mock_storage, "Personal reflection about life", tags=["personal"])
        
        # Test task search
        work_tasks = list_tasks(mock_storage, tag="work")
        assert len(work_tasks) == 1
        assert "project" in work_tasks[0]['content']
        
        # Test journal search
        work_entries = list_journal_entries(mock_storage, tag="work")
        assert len(work_entries) == 1
        assert "project" in work_entries[0]['text']
    
    def test_export_import_integration(self, mock_storage, temp_dir):
        # Add sample data
        add_task(mock_storage, "Export test task", priority="high", tags=["test"])
        add_journal_entry(mock_storage, "Export test entry", tags=["test"])
        add_mood_entry(mock_storage, "happy", "Export test mood")
        
        # Mock export functionality
        export_data = {
            'tasks': mock_storage.get_tasks(show_completed=True),
            'journal_entries': mock_storage.get_journal_entries(),
            'mood_entries': mock_storage.get_mood_entries(),
            'export_date': datetime.now().isoformat()
        }
        
        # Write to file
        export_file = temp_dir / "test_export.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # Verify export file
        assert export_file.exists()
        
        # Read back and verify
        with open(export_file, 'r') as f:
            imported_data = json.load(f)
        
        assert len(imported_data['tasks']) == 1
        assert len(imported_data['journal_entries']) == 1
        assert len(imported_data['mood_entries']) == 1


class TestPerformanceIntegration:
    def test_large_dataset_performance(self, mock_storage):
        # Generate large dataset
        tasks, journal_entries = generate_large_test_dataset(100, 50)
        
        with PerformanceTimer() as timer:
            # Add tasks
            for task_data in tasks:
                add_task(
                    mock_storage,
                    task_data['content'],
                    priority=task_data['priority'],
                    tags=task_data['tags'],
                    board=task_data['board']
                )
            
            # Add journal entries
            for entry_data in journal_entries:
                add_journal_entry(
                    mock_storage,
                    entry_data['text'],
                    tags=entry_data['tags'],
                    category=entry_data['category']
                )
        
        # Performance should be reasonable (adjust threshold as needed)
        assert timer.elapsed < 5.0  # Should complete in under 5 seconds
        
        # Verify all data was added
        stored_tasks = list_tasks(mock_storage)
        stored_entries = list_journal_entries(mock_storage)
        
        assert len(stored_tasks) == 100
        assert len(stored_entries) == 50
    
    def test_search_performance(self, mock_storage):
        # Add data with various tags
        for i in range(200):
            add_task(mock_storage, f"Task {i}", tags=[f"tag{i%10}", "common"])
        
        with PerformanceTimer() as timer:
            # Search for common tag
            common_tasks = list_tasks(mock_storage, tag="common")
        
        # Search should be fast
        assert timer.elapsed < 1.0
        assert len(common_tasks) == 200
        
        with PerformanceTimer() as timer:
            # Search for specific tag
            specific_tasks = list_tasks(mock_storage, tag="tag5")
        
        assert timer.elapsed < 1.0
        assert len(specific_tasks) == 20  # Every 10th task


class TestErrorHandlingIntegration:
    def test_storage_corruption_handling(self, temp_dir):
        db_path = temp_dir / "corrupted.db"
        
        # Create a corrupted database file
        with open(db_path, 'w') as f:
            f.write("This is not a valid SQLite database")
        
        # Storage should handle corruption gracefully
        with pytest.raises(Exception):
            storage = Storage(str(db_path))
    
    def test_concurrent_access_handling(self, temp_dir):
        db_path = temp_dir / "concurrent.db"
        
        # Create storage instance
        storage1 = Storage(str(db_path), keep_test_db=True)
        storage2 = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Both instances should be able to add data
            task_id1 = storage1.add_task("Task from storage 1")
            task_id2 = storage2.add_task("Task from storage 2")
            
            # Both should see all tasks
            tasks1 = storage1.get_tasks()
            tasks2 = storage2.get_tasks()
            
            assert len(tasks1) == 2
            assert len(tasks2) == 2
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_network_failure_simulation(self, mock_storage):
        with patch('requests.post', side_effect=Exception("Network error")):
            # Operations should continue even if external integrations fail
            task_id = add_task(mock_storage, "Task during network failure")
            assert task_id is not None
            
            entry_id = add_journal_entry(mock_storage, "Entry during network failure")
            assert entry_id is not None


class TestRealWorldScenarios:
    def test_daily_workflow_scenario(self, mock_storage):
        # Morning: Add tasks for the day
        morning_tasks = [
            ("Check emails", "high", ["work"]),
            ("Team meeting", "high", ["work", "meeting"]),
            ("Grocery shopping", "medium", ["personal"]),
            ("Exercise", "medium", ["health"])
        ]
        
        task_ids = []
        for content, priority, tags in morning_tasks:
            task_id = add_task(mock_storage, content, priority=priority, tags=tags)
            task_ids.append(task_id)
        
        # Add morning journal entry
        add_journal_entry(
            mock_storage,
            "Starting the day with a clear plan. Feeling motivated!",
            tags=["morning", "planning"]
        )
        
        # Add morning mood
        add_mood_entry(mock_storage, "motivated", "Ready to tackle the day")
        
        # Midday: Complete some tasks
        with patch('logbuch.commands.task.GamificationEngine'):
            complete_task(mock_storage, task_ids[0])  # Check emails
            complete_task(mock_storage, task_ids[1])  # Team meeting
        
        # Add midday journal entry
        add_journal_entry(
            mock_storage,
            "Productive morning! Completed important work tasks.",
            tags=["work", "productivity"]
        )
        
        # Evening: Complete remaining tasks and reflect
        with patch('logbuch.commands.task.GamificationEngine'):
            complete_task(mock_storage, task_ids[2])  # Grocery shopping
            complete_task(mock_storage, task_ids[3])  # Exercise
        
        # Add evening journal entry
        add_journal_entry(
            mock_storage,
            "Great day overall. Completed all planned tasks and feel accomplished.",
            tags=["evening", "reflection", "accomplishment"]
        )
        
        # Add evening mood
        add_mood_entry(mock_storage, "satisfied", "All tasks completed")
        
        # Verify the day's activities
        completed_tasks = list_tasks(mock_storage, show_completed=True)
        journal_entries = list_journal_entries(mock_storage)
        mood_entries = list_mood_entries(mock_storage)
        
        assert len([t for t in completed_tasks if t['completed']]) == 4
        assert len(journal_entries) == 3
        assert len(mood_entries) == 2
    
    def test_weekly_review_scenario(self, mock_storage):
        # Simulate a week of activities
        for day in range(7):
            # Add daily tasks
            add_task(mock_storage, f"Day {day+1} work task", priority="high", tags=["work"])
            add_task(mock_storage, f"Day {day+1} personal task", priority="medium", tags=["personal"])
            
            # Complete work tasks
            work_tasks = list_tasks(mock_storage, tag="work")
            if work_tasks:
                with patch('logbuch.commands.task.GamificationEngine'):
                    complete_task(mock_storage, work_tasks[-1]['id'])
            
            # Add daily journal entry
            add_journal_entry(
                mock_storage,
                f"Day {day+1}: Productive day with good progress on work tasks.",
                tags=["daily", "work"]
            )
            
            # Add daily mood
            moods = ["productive", "focused", "satisfied", "motivated", "accomplished", "content", "grateful"]
            add_mood_entry(mock_storage, moods[day], f"Day {day+1} reflection")
        
        # Weekly review
        all_tasks = list_tasks(mock_storage, show_completed=True)
        completed_tasks = [t for t in all_tasks if t['completed']]
        pending_tasks = [t for t in all_tasks if not t['completed']]
        
        all_entries = list_journal_entries(mock_storage)
        work_entries = list_journal_entries(mock_storage, tag="work")
        
        all_moods = list_mood_entries(mock_storage)
        
        # Weekly review journal entry
        review_text = f"""
        Weekly Review:
        - Completed {len(completed_tasks)} tasks
        - {len(pending_tasks)} tasks still pending
        - Wrote {len(all_entries)} journal entries
        - Tracked mood {len(all_moods)} times
        - Focus areas: work productivity, personal development
        """
        
        add_journal_entry(mock_storage, review_text, tags=["weekly-review", "reflection"])
        
        # Verify weekly data
        assert len(completed_tasks) == 7  # One work task per day
        assert len(pending_tasks) == 7   # One personal task per day
        assert len(all_entries) == 8     # 7 daily + 1 weekly review
        assert len(all_moods) == 7
    
    def test_goal_tracking_scenario(self, mock_storage):
        # Set up annual goals
        reading_goal = add_goal(mock_storage, "Read 24 books this year", target_value=24)
        exercise_goal = add_goal(mock_storage, "Exercise 150 times this year", target_value=150)
        journal_goal = add_goal(mock_storage, "Write 365 journal entries", target_value=365)
        
        # Simulate progress over time
        for week in range(12):  # 3 months
            # Reading progress (2 books per month)
            if week % 2 == 0:
                current_books = (week // 2) + 1
                update_goal_progress(mock_storage, reading_goal, current_books)
                
                add_journal_entry(
                    mock_storage,
                    f"Finished reading book #{current_books}. Great insights!",
                    tags=["reading", "learning"]
                )
            
            # Exercise progress (3-4 times per week)
            exercise_sessions = week * 3 + (week // 2)
            update_goal_progress(mock_storage, exercise_goal, exercise_sessions)
            
            # Journal progress (daily entries)
            journal_entries_count = week * 7
            update_goal_progress(mock_storage, journal_goal, journal_entries_count)
        
        # Check goal progress
        goals = list_goals(mock_storage, show_completed=True)
        
        reading_progress = next(g for g in goals if g['id'] == reading_goal)
        exercise_progress = next(g for g in goals if g['id'] == exercise_goal)
        journal_progress = next(g for g in goals if g['id'] == journal_goal)
        
        assert reading_progress['current_value'] == 6  # 6 books in 3 months
        assert exercise_progress['current_value'] == 42  # ~3.5 sessions per week
        assert journal_progress['current_value'] == 84  # 12 weeks * 7 days
        
        # None should be completed yet (annual goals)
        assert not reading_progress['completed']
        assert not exercise_progress['completed']
        assert not journal_progress['completed']
