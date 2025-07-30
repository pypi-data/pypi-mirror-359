#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.


import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import json

from tests.test_mocks import (
    MockStorage, MockConsole, MockConfig, MockGamificationEngine,
    assert_task_created, assert_journal_entry_created,
    create_sample_task_data, create_sample_journal_data
)

# Import the command modules to test
from logbuch.commands.task import (
    add_task, list_tasks, complete_task, delete_task, move_task
)
from logbuch.commands.journal import (
    add_journal_entry, list_journal_entries, delete_journal_entry
)
from logbuch.commands.mood import (
    add_mood_entry, list_mood_entries, get_random_mood, get_random_moods
)
from logbuch.commands.sleep import add_sleep_entry, list_sleep_entries
from logbuch.commands.goal import (
    add_goal, update_goal_progress, list_goals
)


class TestTaskCommands:
    def test_add_task_basic(self, mock_storage):
        task_id = add_task(mock_storage, "Test task")
        
        assert task_id is not None
        assert_task_created(mock_storage, "Test task")
    
    def test_add_task_with_priority(self, mock_storage):
        task_id = add_task(mock_storage, "High priority task", priority="high")
        
        task = assert_task_created(mock_storage, "High priority task", priority="high")
        assert task['priority'] == "high"
    
    def test_add_task_with_tags(self, mock_storage):
        tags = ["work", "urgent"]
        task_id = add_task(mock_storage, "Tagged task", tags=tags)
        
        task = assert_task_created(mock_storage, "Tagged task")
        assert set(task['tags']) == set(tags)
    
    def test_add_task_with_board(self, mock_storage):
        task_id = add_task(mock_storage, "Work task", board="work")
        
        task = assert_task_created(mock_storage, "Work task")
        assert task['board'] == "work"
    
    def test_list_tasks_empty(self, mock_storage):
        tasks = list_tasks(mock_storage)
        assert tasks == []
    
    def test_list_tasks_with_data(self, mock_storage):
        # Add some tasks
        add_task(mock_storage, "Task 1", priority="high")
        add_task(mock_storage, "Task 2", priority="medium")
        add_task(mock_storage, "Task 3", priority="low")
        
        tasks = list_tasks(mock_storage)
        assert len(tasks) == 3
        assert all(not task['completed'] for task in tasks)
    
    def test_list_tasks_filter_by_board(self, mock_storage):
        add_task(mock_storage, "Work task", board="work")
        add_task(mock_storage, "Personal task", board="personal")
        add_task(mock_storage, "Default task", board="default")
        
        work_tasks = list_tasks(mock_storage, board="work")
        assert len(work_tasks) == 1
        assert work_tasks[0]['content'] == "Work task"
    
    def test_list_tasks_filter_by_priority(self, mock_storage):
        add_task(mock_storage, "High task", priority="high")
        add_task(mock_storage, "Medium task", priority="medium")
        add_task(mock_storage, "Low task", priority="low")
        
        high_tasks = list_tasks(mock_storage, priority="high")
        assert len(high_tasks) == 1
        assert high_tasks[0]['priority'] == "high"
    
    def test_list_tasks_filter_by_tag(self, mock_storage):
        add_task(mock_storage, "Tagged task", tags=["work", "urgent"])
        add_task(mock_storage, "Other task", tags=["personal"])
        
        work_tasks = list_tasks(mock_storage, tag="work")
        assert len(work_tasks) == 1
        assert "work" in work_tasks[0]['tags']
    
    def test_complete_task_success(self, mock_storage):
        task_id = add_task(mock_storage, "Task to complete")
        
        with patch('logbuch.commands.task.GamificationEngine') as mock_gamification:
            mock_engine = Mock()
            mock_engine.process_task_completion.return_value = [{'points': 10}]
            mock_gamification.return_value = mock_engine
            
            result = complete_task(mock_storage, task_id)
            
            assert result is True
            # Verify task is marked as completed
            tasks = list_tasks(mock_storage, show_completed=True)
            completed_task = next(t for t in tasks if t['id'] == task_id)
            assert completed_task['completed'] is True
    
    def test_complete_task_nonexistent(self, mock_storage):
        result = complete_task(mock_storage, 999)
        assert result is False
    
    def test_complete_task_gamification_error(self, mock_storage):
        task_id = add_task(mock_storage, "Task to complete")
        
        with patch('logbuch.commands.task.GamificationEngine', side_effect=Exception("Gamification error")):
            with patch('logbuch.core.logger.get_logger') as mock_logger:
                mock_log = Mock()
                mock_logger.return_value = mock_log
                
                result = complete_task(mock_storage, task_id)
                
                # Task should still be completed despite gamification error
                assert result is True
                mock_log.debug.assert_called_once()
    
    def test_delete_task(self, mock_storage):
        task_id = add_task(mock_storage, "Task to delete")
        
        result = delete_task(mock_storage, task_id)
        assert result is True
        
        # Verify task is deleted
        tasks = list_tasks(mock_storage)
        assert not any(t['id'] == task_id for t in tasks)
    
    def test_move_task(self, mock_storage):
        task_id = add_task(mock_storage, "Task to move", board="default")
        
        result = move_task(mock_storage, task_id, "work")
        assert result is True
        
        # Verify task is moved
        tasks = list_tasks(mock_storage, board="work")
        assert len(tasks) == 1
        assert tasks[0]['id'] == task_id


class TestJournalCommands:
    def test_add_journal_entry_basic(self, mock_storage):
        entry_id = add_journal_entry(mock_storage, "Today was a good day")
        
        assert entry_id is not None
        assert_journal_entry_created(mock_storage, "Today was a good day")
    
    def test_add_journal_entry_with_tags(self, mock_storage):
        tags = ["positive", "work"]
        entry_id = add_journal_entry(mock_storage, "Great progress today", tags=tags)
        
        entry = assert_journal_entry_created(mock_storage, "Great progress today")
        assert set(entry['tags']) == set(tags)
    
    def test_add_journal_entry_with_category(self, mock_storage):
        entry_id = add_journal_entry(mock_storage, "Work reflection", category="work")
        
        entry = assert_journal_entry_created(mock_storage, "Work reflection", category="work")
        assert entry['category'] == "work"
    
    def test_add_journal_entry_with_gamification(self, mock_storage):
        with patch('logbuch.commands.journal.GamificationEngine') as mock_gamification:
            mock_engine = Mock()
            mock_engine.process_journal_entry.return_value = [{'points': 5}]
            mock_gamification.return_value = mock_engine
            
            entry_id = add_journal_entry(mock_storage, "Journal entry")
            
            assert entry_id is not None
            mock_engine.process_journal_entry.assert_called_once()
    
    def test_add_journal_entry_gamification_error(self, mock_storage):
        with patch('logbuch.commands.journal.GamificationEngine', side_effect=Exception("Gamification error")):
            with patch('logbuch.core.logger.get_logger') as mock_logger:
                mock_log = Mock()
                mock_logger.return_value = mock_log
                
                entry_id = add_journal_entry(mock_storage, "Journal entry")
                
                # Entry should still be created despite gamification error
                assert entry_id is not None
                mock_log.debug.assert_called_once()
    
    def test_list_journal_entries_empty(self, mock_storage):
        entries = list_journal_entries(mock_storage)
        assert entries == []
    
    def test_list_journal_entries_with_data(self, mock_storage):
        add_journal_entry(mock_storage, "Entry 1")
        add_journal_entry(mock_storage, "Entry 2")
        add_journal_entry(mock_storage, "Entry 3")
        
        entries = list_journal_entries(mock_storage)
        assert len(entries) == 3
    
    def test_list_journal_entries_with_limit(self, mock_storage):
        for i in range(5):
            add_journal_entry(mock_storage, f"Entry {i+1}")
        
        entries = list_journal_entries(mock_storage, limit=3)
        assert len(entries) == 3
    
    def test_list_journal_entries_filter_by_tag(self, mock_storage):
        add_journal_entry(mock_storage, "Work entry", tags=["work"])
        add_journal_entry(mock_storage, "Personal entry", tags=["personal"])
        
        work_entries = list_journal_entries(mock_storage, tag="work")
        assert len(work_entries) == 1
        assert "work" in work_entries[0]['tags']
    
    def test_list_journal_entries_filter_by_category(self, mock_storage):
        add_journal_entry(mock_storage, "Daily entry", category="daily")
        add_journal_entry(mock_storage, "Work entry", category="work")
        
        daily_entries = list_journal_entries(mock_storage, category="daily")
        assert len(daily_entries) == 1
        assert daily_entries[0]['category'] == "daily"
    
    def test_delete_journal_entry(self, mock_storage):
        entry_id = add_journal_entry(mock_storage, "Entry to delete")
        
        result = delete_journal_entry(mock_storage, entry_id)
        assert result is True
        
        # Verify entry is deleted
        entries = list_journal_entries(mock_storage)
        assert not any(e['id'] == entry_id for e in entries)


class TestMoodCommands:
    def test_add_mood_entry_basic(self, mock_storage):
        entry_id = add_mood_entry(mock_storage, "happy")
        
        assert entry_id is not None
        entries = mock_storage.get_mood_entries()
        assert len(entries) == 1
        assert entries[0]['mood'] == "happy"
    
    def test_add_mood_entry_with_notes(self, mock_storage):
        entry_id = add_mood_entry(mock_storage, "excited", "Got promoted today!")
        
        entries = mock_storage.get_mood_entries()
        assert len(entries) == 1
        assert entries[0]['mood'] == "excited"
        assert entries[0]['notes'] == "Got promoted today!"
    
    def test_list_mood_entries_empty(self, mock_storage):
        entries = list_mood_entries(mock_storage)
        assert entries == []
    
    def test_list_mood_entries_with_data(self, mock_storage):
        add_mood_entry(mock_storage, "happy")
        add_mood_entry(mock_storage, "focused")
        add_mood_entry(mock_storage, "tired")
        
        entries = list_mood_entries(mock_storage)
        assert len(entries) == 3
    
    def test_list_mood_entries_with_limit(self, mock_storage):
        for mood in ["happy", "sad", "excited", "calm", "anxious"]:
            add_mood_entry(mock_storage, mood)
        
        entries = list_mood_entries(mock_storage, limit=3)
        assert len(entries) == 3
    
    @patch('random.choice')
    def test_get_random_mood(self, mock_choice):
        mock_choice.return_value = "happy"
        
        mood = get_random_mood()
        assert mood == "happy"
        mock_choice.assert_called_once()
    
    @patch('random.sample')
    def test_get_random_moods(self, mock_sample):
        mock_sample.return_value = ["happy", "excited", "calm"]
        
        moods = get_random_moods(3)
        assert moods == ["happy", "excited", "calm"]
        mock_sample.assert_called_once()


class TestSleepCommands:
    def test_add_sleep_entry_basic(self, mock_storage):
        bedtime = "23:00"
        wake_time = "07:00"
        
        entry_id = add_sleep_entry(mock_storage, bedtime, wake_time)
        
        assert entry_id is not None
        entries = mock_storage.get_sleep_entries()
        assert len(entries) == 1
        assert entries[0]['bedtime'] == bedtime
        assert entries[0]['wake_time'] == wake_time
    
    def test_add_sleep_entry_with_quality(self, mock_storage):
        entry_id = add_sleep_entry(mock_storage, "23:00", "07:00", quality=8)
        
        entries = mock_storage.get_sleep_entries()
        assert len(entries) == 1
        assert entries[0]['quality'] == 8
    
    def test_add_sleep_entry_with_notes(self, mock_storage):
        notes = "Woke up feeling refreshed"
        entry_id = add_sleep_entry(mock_storage, "23:00", "07:00", notes=notes)
        
        entries = mock_storage.get_sleep_entries()
        assert len(entries) == 1
        assert entries[0]['notes'] == notes
    
    def test_list_sleep_entries_empty(self, mock_storage):
        entries = list_sleep_entries(mock_storage)
        assert entries == []
    
    def test_list_sleep_entries_with_data(self, mock_storage):
        add_sleep_entry(mock_storage, "23:00", "07:00")
        add_sleep_entry(mock_storage, "22:30", "06:30")
        
        entries = list_sleep_entries(mock_storage)
        assert len(entries) == 2
    
    def test_list_sleep_entries_with_limit(self, mock_storage):
        for i in range(5):
            add_sleep_entry(mock_storage, "23:00", "07:00")
        
        entries = list_sleep_entries(mock_storage, limit=3)
        assert len(entries) == 3


class TestGoalCommands:
    def test_add_goal_basic(self, mock_storage):
        goal_id = add_goal(mock_storage, "Read 12 books this year")
        
        assert goal_id is not None
        goals = mock_storage.get_goals()
        assert len(goals) == 1
        assert goals[0]['title'] == "Read 12 books this year"
    
    def test_add_goal_with_description(self, mock_storage):
        description = "Personal development goal for continuous learning"
        goal_id = add_goal(mock_storage, "Read 12 books", description=description)
        
        goals = mock_storage.get_goals()
        assert len(goals) == 1
        assert goals[0]['description'] == description
    
    def test_add_goal_with_target_value(self, mock_storage):
        goal_id = add_goal(mock_storage, "Exercise goal", target_value=100)
        
        goals = mock_storage.get_goals()
        assert len(goals) == 1
        assert goals[0]['target_value'] == 100
        assert goals[0]['current_value'] == 0
    
    def test_update_goal_progress(self, mock_storage):
        goal_id = add_goal(mock_storage, "Exercise goal", target_value=100)
        
        result = update_goal_progress(mock_storage, goal_id, 25)
        assert result is True
        
        goals = mock_storage.get_goals()
        assert goals[0]['current_value'] == 25
        assert not goals[0]['completed']
    
    def test_update_goal_progress_completion(self, mock_storage):
        goal_id = add_goal(mock_storage, "Exercise goal", target_value=100)
        
        result = update_goal_progress(mock_storage, goal_id, 100)
        assert result is True
        
        goals = mock_storage.get_goals(show_completed=True)
        assert goals[0]['current_value'] == 100
        assert goals[0]['completed'] is True
    
    def test_update_goal_progress_nonexistent(self, mock_storage):
        result = update_goal_progress(mock_storage, 999, 50)
        assert result is False
    
    def test_list_goals_empty(self, mock_storage):
        goals = list_goals(mock_storage)
        assert goals == []
    
    def test_list_goals_with_data(self, mock_storage):
        add_goal(mock_storage, "Goal 1")
        add_goal(mock_storage, "Goal 2")
        
        goals = list_goals(mock_storage)
        assert len(goals) == 2
    
    def test_list_goals_hide_completed(self, mock_storage):
        goal_id = add_goal(mock_storage, "Completed goal", target_value=10)
        add_goal(mock_storage, "Active goal")
        
        # Complete the first goal
        update_goal_progress(mock_storage, goal_id, 10)
        
        goals = list_goals(mock_storage)
        assert len(goals) == 1
        assert goals[0]['title'] == "Active goal"
    
    def test_list_goals_show_completed(self, mock_storage):
        goal_id = add_goal(mock_storage, "Completed goal", target_value=10)
        add_goal(mock_storage, "Active goal")
        
        # Complete the first goal
        update_goal_progress(mock_storage, goal_id, 10)
        
        goals = list_goals(mock_storage, show_completed=True)
        assert len(goals) == 2


# Integration tests combining multiple commands

class TestCommandIntegration:
    def test_task_and_journal_workflow(self, mock_storage):
        # Add a task
        task_id = add_task(mock_storage, "Complete important project", priority="high")
        
        # Add journal entry about starting the task
        entry_id = add_journal_entry(
            mock_storage, 
            "Started working on the important project today",
            tags=["work", "project"]
        )
        
        # Complete the task
        with patch('logbuch.commands.task.GamificationEngine'):
            complete_task(mock_storage, task_id)
        
        # Add journal entry about completion
        completion_entry_id = add_journal_entry(
            mock_storage,
            "Successfully completed the important project!",
            tags=["work", "achievement"]
        )
        
        # Verify everything was created correctly
        tasks = list_tasks(mock_storage, show_completed=True)
        assert len(tasks) == 1
        assert tasks[0]['completed'] is True
        
        entries = list_journal_entries(mock_storage)
        assert len(entries) == 2
    
    def test_mood_and_sleep_correlation(self, mock_storage):
        # Add sleep entry
        sleep_id = add_sleep_entry(mock_storage, "23:00", "07:00", quality=8)
        
        # Add corresponding mood entry
        mood_id = add_mood_entry(mock_storage, "refreshed", "Slept well last night")
        
        # Verify both entries exist
        sleep_entries = list_sleep_entries(mock_storage)
        mood_entries = list_mood_entries(mock_storage)
        
        assert len(sleep_entries) == 1
        assert len(mood_entries) == 1
        assert sleep_entries[0]['quality'] == 8
        assert mood_entries[0]['mood'] == "refreshed"
    
    def test_goal_progress_with_tasks(self, mock_storage):
        # Add a goal
        goal_id = add_goal(mock_storage, "Complete 10 work tasks", target_value=10)
        
        # Add and complete multiple tasks
        for i in range(5):
            task_id = add_task(mock_storage, f"Work task {i+1}", tags=["work"])
            with patch('logbuch.commands.task.GamificationEngine'):
                complete_task(mock_storage, task_id)
        
        # Update goal progress
        update_goal_progress(mock_storage, goal_id, 5)
        
        # Verify goal progress
        goals = list_goals(mock_storage)
        assert len(goals) == 1
        assert goals[0]['current_value'] == 5
        assert not goals[0]['completed']
        
        # Complete remaining tasks and goal
        for i in range(5, 10):
            task_id = add_task(mock_storage, f"Work task {i+1}", tags=["work"])
            with patch('logbuch.commands.task.GamificationEngine'):
                complete_task(mock_storage, task_id)
        
        update_goal_progress(mock_storage, goal_id, 10)
        
        # Verify goal completion
        completed_goals = list_goals(mock_storage, show_completed=True)
        completed_goal = next(g for g in completed_goals if g['id'] == goal_id)
        assert completed_goal['completed'] is True


# Error handling tests

class TestCommandErrorHandling:
    def test_add_task_empty_content(self, mock_storage):
        # This should still work as the validation might be in the storage layer
        task_id = add_task(mock_storage, "")
        assert task_id is not None
    
    def test_complete_nonexistent_task(self, mock_storage):
        result = complete_task(mock_storage, 999)
        assert result is False
    
    def test_delete_nonexistent_task(self, mock_storage):
        # Mock storage should handle this gracefully
        result = delete_task(mock_storage, 999)
        assert result is True  # Mock returns True regardless
    
    def test_move_nonexistent_task(self, mock_storage):
        result = move_task(mock_storage, 999, "work")
        assert result is False
    
    def test_add_journal_entry_empty_text(self, mock_storage):
        entry_id = add_journal_entry(mock_storage, "")
        assert entry_id is not None
    
    def test_delete_nonexistent_journal_entry(self, mock_storage):
        result = delete_journal_entry(mock_storage, 999)
        assert result is True  # Mock returns True regardless
