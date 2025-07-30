#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 30.06.25, 08:14.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime, date, timedelta
import json
import sqlite3
from pathlib import Path
import tempfile
import shutil


class MockStorage:
    def __init__(self):
        self.tasks = []
        self.journal_entries = []
        self.mood_entries = []
        self.sleep_entries = []
        self.goals = []
        self.projects = []
        self.achievements = []
        self.stats = {}
        self.next_id = 1
        
    def add_task(self, content, priority=None, tags=None, due_date=None, board="default"):
        task = {
            'id': self.next_id,
            'content': content,
            'priority': priority or 'medium',
            'tags': tags or [],
            'due_date': due_date,
            'board': board,
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        self.tasks.append(task)
        self.next_id += 1
        return task['id']
    
    def get_tasks(self, show_completed=False, board=None, priority=None, tag=None):
        filtered_tasks = self.tasks.copy()
        
        if not show_completed:
            filtered_tasks = [t for t in filtered_tasks if not t['completed']]
        
        if board:
            filtered_tasks = [t for t in filtered_tasks if t['board'] == board]
            
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority]
            
        if tag:
            filtered_tasks = [t for t in filtered_tasks if tag in t['tags']]
            
        return filtered_tasks
    
    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                return True
        return False
    
    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        return True
    
    def move_task(self, task_id, board):
        for task in self.tasks:
            if task['id'] == task_id:
                task['board'] = board
                return True
        return False
    
    def add_journal_entry(self, text, tags=None, category=None):
        entry = {
            'id': self.next_id,
            'text': text,
            'tags': tags or [],
            'category': category,
            'created_at': datetime.now().isoformat()
        }
        self.journal_entries.append(entry)
        self.next_id += 1
        return entry['id']
    
    def get_journal_entries(self, limit=None, tag=None, category=None, date=None):
        filtered_entries = self.journal_entries.copy()
        
        if tag:
            filtered_entries = [e for e in filtered_entries if tag in e['tags']]
            
        if category:
            filtered_entries = [e for e in filtered_entries if e['category'] == category]
            
        if date:
            # Simple date filtering - in real app this would be more sophisticated
            filtered_entries = [e for e in filtered_entries if date in e['created_at']]
            
        if limit:
            filtered_entries = filtered_entries[:limit]
            
        return filtered_entries
    
    def delete_journal_entry(self, entry_id):
        self.journal_entries = [e for e in self.journal_entries if e['id'] != entry_id]
        return True
    
    def add_mood_entry(self, mood, notes=None):
        entry = {
            'id': self.next_id,
            'mood': mood,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        self.mood_entries.append(entry)
        self.next_id += 1
        return entry['id']
    
    def get_mood_entries(self, limit=None, date_range=None):
        filtered_entries = self.mood_entries.copy()
        
        if limit:
            filtered_entries = filtered_entries[:limit]
            
        return filtered_entries
    
    def add_sleep_entry(self, bedtime, wake_time, quality=None, notes=None):
        entry = {
            'id': self.next_id,
            'bedtime': bedtime,
            'wake_time': wake_time,
            'quality': quality,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        self.sleep_entries.append(entry)
        self.next_id += 1
        return entry['id']
    
    def get_sleep_entries(self, limit=None):
        return self.sleep_entries[:limit] if limit else self.sleep_entries
    
    def add_goal(self, title, description=None, target_value=None, current_value=0):
        goal = {
            'id': self.next_id,
            'title': title,
            'description': description,
            'target_value': target_value,
            'current_value': current_value,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        self.goals.append(goal)
        self.next_id += 1
        return goal['id']
    
    def update_goal_progress(self, goal_id, progress):
        for goal in self.goals:
            if goal['id'] == goal_id:
                goal['current_value'] = progress
                if goal['target_value'] and progress >= goal['target_value']:
                    goal['completed'] = True
                return True
        return False
    
    def get_goals(self, show_completed=False):
        if show_completed:
            return self.goals
        return [g for g in self.goals if not g['completed']]
    
    def get_stats(self):
        return {
            'total_tasks': len(self.tasks),
            'completed_tasks': len([t for t in self.tasks if t['completed']]),
            'total_journal_entries': len(self.journal_entries),
            'total_mood_entries': len(self.mood_entries),
            'total_sleep_entries': len(self.sleep_entries),
            'total_goals': len(self.goals),
            'completed_goals': len([g for g in self.goals if g['completed']])
        }


class MockConsole:
    def __init__(self):
        self.output = []
        self.errors = []
    
    def print(self, *args, **kwargs):
        self.output.append(str(args))
    
    def error(self, *args, **kwargs):
        self.errors.append(str(args))
    
    def clear(self):
        self.output.clear()
        self.errors.clear()


class MockConfig:
    def __init__(self):
        self.database = MockDatabaseConfig()
        self.notifications = MockNotificationConfig()
        self.ui = MockUIConfig()
        self.security = MockSecurityConfig()
        self.debug = True
        self.log_level = "DEBUG"
        self.data_dir = "/tmp/test_logbuch"


class MockDatabaseConfig:
    def __init__(self):
        self.path = ":memory:"
        self.backup_interval_hours = 1
        self.max_backups = 3


class MockNotificationConfig:
    def __init__(self):
        self.enabled = False
        self.sound_enabled = False
        self.desktop_enabled = False


class MockUIConfig:
    def __init__(self):
        self.theme = "default"
        self.show_help = True
        self.compact_mode = False


class MockSecurityConfig:
    def __init__(self):
        self.input_validation = True
        self.rate_limit_enabled = False
        self.max_input_length = 10000


class MockGamificationEngine:
    def __init__(self, storage):
        self.storage = storage
        self.rewards = []
    
    def process_task_completion(self, task):
        reward = {
            'type': 'task_completion',
            'points': 10,
            'achievement': None,
            'message': f"Great job completing '{task['content']}'!"
        }
        
        # Add bonus for high priority tasks
        if task.get('priority') == 'high':
            reward['points'] = 20
            reward['message'] += " High priority bonus!"
        
        self.rewards.append(reward)
        return [reward]
    
    def process_journal_entry(self, entry):
        reward = {
            'type': 'journal_entry',
            'points': 5,
            'achievement': None,
            'message': "Thanks for journaling!"
        }
        
        # Add bonus for long entries
        if len(entry['text']) > 100:
            reward['points'] = 10
            reward['message'] += " Detailed entry bonus!"
        
        self.rewards.append(reward)
        return [reward]


class MockFileSystem:
    def __init__(self):
        self.files = {}
        self.directories = set()
    
    def exists(self, path):
        return str(path) in self.files or str(path) in self.directories
    
    def read_text(self, path):
        return self.files.get(str(path), "")
    
    def write_text(self, path, content):
        self.files[str(path)] = content
    
    def mkdir(self, path, parents=False, exist_ok=False):
        self.directories.add(str(path))
    
    def unlink(self, path):
        if str(path) in self.files:
            del self.files[str(path)]


class MockDateTime:
    def __init__(self, fixed_time=None):
        self.fixed_time = fixed_time or datetime(2024, 1, 15, 10, 30, 0)
    
    def now(self):
        return self.fixed_time
    
    def today(self):
        return self.fixed_time.date()


# Pytest fixtures using the mock classes

@pytest.fixture
def mock_storage():
    return MockStorage()


@pytest.fixture
def mock_console():
    return MockConsole()


@pytest.fixture
def mock_config():
    return MockConfig()


@pytest.fixture
def mock_gamification():
    def _create_mock_gamification(storage):
        return MockGamificationEngine(storage)
    return _create_mock_gamification


@pytest.fixture
def mock_filesystem():
    return MockFileSystem()


@pytest.fixture
def mock_datetime():
    return MockDateTime()


@pytest.fixture
def populated_mock_storage():
    storage = MockStorage()
    
    # Add sample tasks
    storage.add_task("Complete project documentation", "high", ["work", "urgent"])
    storage.add_task("Buy groceries", "medium", ["personal"])
    storage.add_task("Call dentist", "low", ["health"])
    
    # Add sample journal entries
    storage.add_journal_entry("Had a productive day working on the project", ["work", "positive"])
    storage.add_journal_entry("Feeling grateful for good health", ["personal", "gratitude"])
    
    # Add sample mood entries
    storage.add_mood_entry("happy", "Great progress on work today")
    storage.add_mood_entry("focused", "Deep work session")
    
    # Add sample goals
    storage.add_goal("Read 12 books this year", "Personal development goal", 12, 3)
    storage.add_goal("Exercise 3 times per week", "Health goal", 156, 45)  # 3 * 52 weeks
    
    return storage


# Context managers for mocking

class MockDatabaseConnection:
    def __init__(self, mock_storage):
        self.mock_storage = mock_storage
        self.cursor_mock = Mock()
    
    def __enter__(self):
        return self.cursor_mock
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def execute(self, query, params=None):
        return self.cursor_mock
    
    def fetchall(self):
        return []
    
    def fetchone(self):
        return None


# Utility functions for testing

def create_sample_task_data(count=5):
    tasks = []
    priorities = ['low', 'medium', 'high']
    boards = ['default', 'work', 'personal']
    
    for i in range(count):
        tasks.append({
            'content': f"Sample task {i+1}",
            'priority': priorities[i % len(priorities)],
            'tags': [f"tag{i}", "test"],
            'board': boards[i % len(boards)]
        })
    
    return tasks


def create_sample_journal_data(count=3):
    entries = []
    categories = ['daily', 'work', 'personal', 'reflection']
    
    for i in range(count):
        entries.append({
            'text': f"This is journal entry number {i+1}. It contains some thoughts and reflections.",
            'tags': [f"tag{i}", "test"],
            'category': categories[i % len(categories)]
        })
    
    return entries


def assert_task_created(storage, content, priority=None):
    tasks = storage.get_tasks()
    task = next((t for t in tasks if t['content'] == content), None)
    assert task is not None, f"Task with content '{content}' not found"
    
    if priority:
        assert task['priority'] == priority, f"Expected priority {priority}, got {task['priority']}"
    
    return task


def assert_journal_entry_created(storage, text, category=None):
    entries = storage.get_journal_entries()
    entry = next((e for e in entries if e['text'] == text), None)
    assert entry is not None, f"Journal entry with text '{text}' not found"
    
    if category:
        assert entry['category'] == category, f"Expected category {category}, got {entry['category']}"
    
    return entry


# Performance testing utilities

class PerformanceTimer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end_time = time.time()
    
    @property
    def elapsed(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0


def generate_large_test_dataset(task_count=1000, journal_count=500):
    import random
    import string
    
    tasks = []
    for i in range(task_count):
        tasks.append({
            'content': f"Task {i}: {''.join(random.choices(string.ascii_letters, k=20))}",
            'priority': random.choice(['low', 'medium', 'high']),
            'tags': [f"tag{j}" for j in range(random.randint(0, 3))],
            'board': random.choice(['default', 'work', 'personal'])
        })
    
    journal_entries = []
    for i in range(journal_count):
        journal_entries.append({
            'text': f"Journal entry {i}: {''.join(random.choices(string.ascii_letters + ' ', k=100))}",
            'tags': [f"tag{j}" for j in range(random.randint(0, 2))],
            'category': random.choice(['daily', 'work', 'personal', 'reflection'])
        })
    
    return tasks, journal_entries
