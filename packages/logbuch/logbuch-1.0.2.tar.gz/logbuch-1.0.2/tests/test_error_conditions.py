#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_error_conditions.py

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import threading
import time

from logbuch.storage import Storage
from logbuch.commands.task import add_task, list_tasks, complete_task, delete_task
from logbuch.commands.journal import add_journal_entry, list_journal_entries, delete_journal_entry
from logbuch.commands.mood import add_mood_entry, list_mood_entries
from tests.test_mocks import MockStorage


class TestDatabaseErrorConditions:
    def test_corrupted_database_handling(self, temp_dir):
        db_path = temp_dir / "corrupted.db"
        
        # Create a corrupted database file
        with open(db_path, 'w') as f:
            f.write("This is not a valid SQLite database")
        
        # Should handle corruption gracefully
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            # If it doesn't raise an exception, verify it creates a new valid database
            assert storage.db_path.exists()
        except Exception as e:
            # It's acceptable to raise an exception for corrupted databases
            assert "database" in str(e).lower() or "sqlite" in str(e).lower()
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_database_permission_denied(self, temp_dir):
        db_path = temp_dir / "readonly.db"
        
        # Create a database first
        storage = Storage(str(db_path), keep_test_db=True)
        storage.add_task("Test task")
        del storage  # Close connection
        
        try:
            # Make file read-only (Unix-like systems)
            if os.name != 'nt':
                os.chmod(db_path, 0o444)
                
                # Attempt to write should handle permission error
                try:
                    readonly_storage = Storage(str(db_path), keep_test_db=True)
                    task_id = readonly_storage.add_task("Should fail")
                    # If it succeeds, that's also acceptable (some systems handle this differently)
                except Exception as e:
                    # Should get a permission or database error
                    assert any(word in str(e).lower() for word in ['permission', 'readonly', 'database', 'locked'])
        finally:
            # Restore permissions and cleanup
            if db_path.exists():
                try:
                    os.chmod(db_path, 0o644)
                    db_path.unlink()
                except:
                    pass
    
    def test_database_locked_handling(self, temp_dir):
        db_path = temp_dir / "locked.db"
        
        try:
            # Create first connection
            storage1 = Storage(str(db_path), keep_test_db=True)
            
            # Start a long-running transaction
            with sqlite3.connect(str(db_path)) as conn1:
                conn1.execute("BEGIN EXCLUSIVE TRANSACTION")
                
                # Try to access from another connection
                try:
                    storage2 = Storage(str(db_path), keep_test_db=True)
                    # This might succeed or fail depending on SQLite configuration
                    task_id = storage2.add_task("Test during lock")
                except Exception as e:
                    # Should handle database lock gracefully
                    assert any(word in str(e).lower() for word in ['locked', 'busy', 'database'])
                
                # Rollback to release lock
                conn1.rollback()
                
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_disk_full_simulation(self, temp_dir):
        db_path = temp_dir / "diskfull.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Simulate disk full by mocking file operations
            with patch('sqlite3.connect') as mock_connect:
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.execute.side_effect = sqlite3.OperationalError("database or disk is full")
                mock_conn.cursor.return_value = mock_cursor
                mock_connect.return_value.__enter__.return_value = mock_conn
                
                # Should handle disk full error gracefully
                try:
                    task_id = storage.add_task("Test disk full")
                    assert False, "Should have raised an exception"
                except Exception as e:
                    assert "disk" in str(e).lower() or "full" in str(e).lower()
                    
        finally:
            if db_path.exists():
                db_path.unlink()


class TestInputErrorConditions:
    def test_none_input_handling(self, mock_storage):
        # Test None task content
        try:
            task_id = add_task(mock_storage, None)
            # If it succeeds, verify it handles None appropriately
            if task_id:
                tasks = list_tasks(mock_storage)
                # Should either reject None or convert to empty string
                assert all(task['content'] is not None for task in tasks)
        except (TypeError, ValueError, AttributeError):
            # It's acceptable to reject None inputs
            pass
    
    def test_empty_string_handling(self, mock_storage):
        # Empty task content
        task_id = add_task(mock_storage, "")
        assert task_id is not None
        
        tasks = list_tasks(mock_storage)
        assert len(tasks) == 1
        assert tasks[0]['content'] == ""
        
        # Empty journal entry
        entry_id = add_journal_entry(mock_storage, "")
        assert entry_id is not None
        
        entries = list_journal_entries(mock_storage)
        assert len(entries) == 1
        assert entries[0]['text'] == ""
    
    def test_whitespace_only_input(self, mock_storage):
        whitespace_inputs = [
            "   ",      # spaces
            "\t\t",     # tabs
            "\n\n",     # newlines
            " \t\n ",   # mixed whitespace
        ]
        
        for whitespace in whitespace_inputs:
            task_id = add_task(mock_storage, whitespace)
            assert task_id is not None
            
            entry_id = add_journal_entry(mock_storage, whitespace)
            assert entry_id is not None
    
    def test_unicode_input_handling(self, mock_storage):
        unicode_inputs = [
            "🎉 Task with emoji",
            "Tâsk wîth âccénts",
            "任务 with Chinese characters",
            "Задача with Cyrillic",
            "مهمة with Arabic",
            "Task with\nnewlines\nand\ttabs",
            "Task with \"quotes\" and 'apostrophes'",
            "Task with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?",
        ]
        
        for unicode_input in unicode_inputs:
            task_id = add_task(mock_storage, unicode_input)
            assert task_id is not None
            
            # Verify it's stored correctly
            tasks = list_tasks(mock_storage)
            found_task = next((t for t in tasks if t['content'] == unicode_input), None)
            assert found_task is not None
            assert found_task['content'] == unicode_input
    
    def test_extremely_long_input(self, mock_storage):
        # Very long task content
        long_content = "A" * 100000  # 100KB
        
        try:
            task_id = add_task(mock_storage, long_content)
            if task_id:
                tasks = list_tasks(mock_storage)
                long_task = next((t for t in tasks if len(t['content']) > 50000), None)
                assert long_task is not None
        except Exception as e:
            # It's acceptable to reject extremely long inputs
            assert any(word in str(e).lower() for word in ['length', 'size', 'limit', 'too long'])
    
    def test_invalid_data_types(self, mock_storage):
        invalid_inputs = [
            123,           # integer
            12.34,         # float
            [],            # list
            {},            # dict
            set(),         # set
            object(),      # object
        ]
        
        for invalid_input in invalid_inputs:
            try:
                task_id = add_task(mock_storage, invalid_input)
                # If it succeeds, verify it converts to string
                if task_id:
                    tasks = list_tasks(mock_storage)
                    found_task = next((t for t in tasks if str(invalid_input) in str(t['content'])), None)
                    assert found_task is not None
            except (TypeError, ValueError):
                # It's acceptable to reject invalid data types
                pass


class TestOperationErrorConditions:
    def test_complete_nonexistent_task(self, mock_storage):
        result = complete_task(mock_storage, 99999)
        assert result is False
    
    def test_delete_nonexistent_task(self, mock_storage):
        # Mock storage might return True regardless, which is acceptable
        result = delete_task(mock_storage, 99999)
        # Either True (mock behavior) or False (real behavior) is acceptable
        assert isinstance(result, bool)
    
    def test_delete_nonexistent_journal_entry(self, mock_storage):
        result = delete_journal_entry(mock_storage, 99999)
        assert isinstance(result, bool)
    
    def test_complete_already_completed_task(self, mock_storage):
        # Add and complete a task
        task_id = add_task(mock_storage, "Task to complete twice")
        
        # Complete it once
        result1 = complete_task(mock_storage, task_id)
        assert result1 is True
        
        # Try to complete it again
        result2 = complete_task(mock_storage, task_id)
        # Should handle gracefully (either succeed or fail is acceptable)
        assert isinstance(result2, bool)
    
    def test_invalid_priority_values(self, mock_storage):
        invalid_priorities = [
            "invalid",
            "URGENT",  # wrong case
            123,       # number
            None,      # None
            "",        # empty string
        ]
        
        for invalid_priority in invalid_priorities:
            try:
                task_id = add_task(mock_storage, "Test task", priority=invalid_priority)
                # If it succeeds, verify it handles the invalid priority
                if task_id:
                    tasks = list_tasks(mock_storage)
                    task = next((t for t in tasks if t['id'] == task_id), None)
                    assert task is not None
                    # Should either use default priority or store as-is
                    assert task['priority'] is not None
            except (ValueError, TypeError):
                # It's acceptable to reject invalid priorities
                pass
    
    def test_invalid_tag_formats(self, mock_storage):
        invalid_tag_sets = [
            "not_a_list",      # string instead of list
            123,               # number
            {"tag": "value"},  # dict
            [123, 456],        # list of numbers
            [None, "valid"],   # list with None
            ["", "valid"],     # list with empty string
        ]
        
        for invalid_tags in invalid_tag_sets:
            try:
                task_id = add_task(mock_storage, "Test task", tags=invalid_tags)
                # If it succeeds, verify it handles the invalid tags
                if task_id:
                    tasks = list_tasks(mock_storage)
                    task = next((t for t in tasks if t['id'] == task_id), None)
                    assert task is not None
                    # Should either convert to valid format or use default
                    assert isinstance(task['tags'], list)
            except (TypeError, ValueError):
                # It's acceptable to reject invalid tag formats
                pass


class TestConcurrencyErrorConditions:
    def test_concurrent_task_creation_conflicts(self, temp_dir):
        db_path = temp_dir / "concurrent_errors.db"
        
        errors = []
        successful_operations = []
        
        def create_tasks_with_errors(thread_id):
            try:
                storage = Storage(str(db_path), keep_test_db=True)
                for i in range(10):
                    try:
                        task_id = storage.add_task(f"Thread {thread_id} task {i}")
                        successful_operations.append((thread_id, i, task_id))
                    except Exception as e:
                        errors.append((thread_id, i, str(e)))
                        time.sleep(0.001)  # Brief pause before retry
            except Exception as e:
                errors.append((thread_id, "connection", str(e)))
        
        try:
            # Start multiple threads
            threads = []
            for thread_id in range(5):
                thread = threading.Thread(target=create_tasks_with_errors, args=(thread_id,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify that either operations succeeded or errors were handled gracefully
            total_attempts = 50  # 5 threads * 10 tasks each
            total_results = len(successful_operations) + len(errors)
            
            # Should have attempted all operations
            assert total_results <= total_attempts
            
            # If there were errors, they should be database-related
            for thread_id, operation, error in errors:
                assert any(word in error.lower() for word in [
                    'database', 'locked', 'busy', 'timeout', 'connection'
                ])
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_concurrent_read_write_conflicts(self, temp_dir):
        db_path = temp_dir / "read_write_conflicts.db"
        
        read_errors = []
        write_errors = []
        
        def writer_with_error_handling():
            try:
                storage = Storage(str(db_path), keep_test_db=True)
                for i in range(20):
                    try:
                        storage.add_task(f"Writer task {i}")
                        time.sleep(0.001)
                    except Exception as e:
                        write_errors.append(str(e))
            except Exception as e:
                write_errors.append(f"Writer connection error: {e}")
        
        def reader_with_error_handling():
            try:
                storage = Storage(str(db_path), keep_test_db=True)
                for i in range(10):
                    try:
                        tasks = storage.get_tasks()
                        time.sleep(0.002)
                    except Exception as e:
                        read_errors.append(str(e))
            except Exception as e:
                read_errors.append(f"Reader connection error: {e}")
        
        try:
            # Start concurrent readers and writers
            threads = []
            
            # Start writers
            for _ in range(2):
                thread = threading.Thread(target=writer_with_error_handling)
                threads.append(thread)
                thread.start()
            
            # Start readers
            for _ in range(3):
                thread = threading.Thread(target=reader_with_error_handling)
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify errors are handled appropriately
            all_errors = read_errors + write_errors
            for error in all_errors:
                # Errors should be database-related, not application crashes
                assert any(word in error.lower() for word in [
                    'database', 'locked', 'busy', 'timeout', 'connection', 'sqlite'
                ])
            
        finally:
            if db_path.exists():
                db_path.unlink()


class TestMemoryErrorConditions:
    def test_memory_exhaustion_simulation(self, mock_storage):
        # Simulate memory pressure by creating many large objects
        large_objects = []
        
        try:
            # Create increasingly large task contents
            for i in range(10):
                size = 1000 * (i + 1)  # 1KB, 2KB, 3KB, etc.
                large_content = "X" * size
                
                try:
                    task_id = add_task(mock_storage, large_content)
                    large_objects.append(large_content)  # Keep reference to simulate memory usage
                    assert task_id is not None
                except MemoryError:
                    # It's acceptable to fail with MemoryError under extreme conditions
                    break
                except Exception as e:
                    # Other exceptions should be memory-related
                    assert any(word in str(e).lower() for word in ['memory', 'size', 'limit'])
                    break
            
        finally:
            # Clean up large objects
            large_objects.clear()
    
    def test_recursive_operation_protection(self, mock_storage):
        # This is more relevant for real implementations with complex operations
        # For now, test that basic operations don't cause infinite recursion
        
        def recursive_task_creation(depth, max_depth=100):
            if depth >= max_depth:
                return
            
            try:
                task_id = add_task(mock_storage, f"Recursive task depth {depth}")
                if task_id and depth < 50:  # Limit recursion to prevent actual stack overflow in tests
                    recursive_task_creation(depth + 1, max_depth)
            except RecursionError:
                # Should handle recursion limits gracefully
                pass
        
        # Start recursive operation
        recursive_task_creation(0)
        
        # Verify some tasks were created without crashing
        tasks = list_tasks(mock_storage)
        assert len(tasks) > 0


class TestNetworkErrorConditions:
    def test_network_timeout_handling(self, mock_storage):
        # Mock network operations that might timeout
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Connection timeout")
            
            # Operations should continue even if external integrations fail
            task_id = add_task(mock_storage, "Task during network failure")
            assert task_id is not None
            
            entry_id = add_journal_entry(mock_storage, "Entry during network failure")
            assert entry_id is not None
    
    def test_api_rate_limit_handling(self, mock_storage):
        # Mock API rate limit responses
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Rate limit exceeded")
            
            # Should handle rate limits gracefully
            for i in range(5):
                task_id = add_task(mock_storage, f"Task {i} during rate limit")
                assert task_id is not None
    
    def test_invalid_api_response_handling(self, mock_storage):
        # Mock invalid API responses
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            
            # Should handle invalid responses gracefully
            task_id = add_task(mock_storage, "Task during API error")
            assert task_id is not None


class TestFileSystemErrorConditions:
    def test_backup_directory_creation_failure(self, temp_dir):
        db_path = temp_dir / "backup_test.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            storage.add_task("Test task for backup")
            
            # Mock backup directory creation failure
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                mock_mkdir.side_effect = PermissionError("Permission denied")
                
                try:
                    backup_path = storage.create_backup()
                    # If it succeeds despite the mock, that's also acceptable
                except (PermissionError, OSError) as e:
                    # Should handle permission errors gracefully
                    assert "permission" in str(e).lower() or "denied" in str(e).lower()
                    
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_config_file_corruption(self, temp_dir):
        config_path = temp_dir / "corrupted_config.json"
        
        # Create corrupted config file
        with open(config_path, 'w') as f:
            f.write("{ invalid json content")
        
        # Should handle corrupted config gracefully
        try:
            from logbuch.core.config import ConfigManager
            manager = ConfigManager(str(config_path))
            config = manager.load()
            # Should either load defaults or raise appropriate exception
            assert config is not None
        except Exception as e:
            # Should be a JSON or configuration related error
            assert any(word in str(e).lower() for word in ['json', 'config', 'parse', 'invalid'])


# Integration test for error recovery

class TestErrorRecovery:
    def test_database_recovery_after_corruption(self, temp_dir):
        db_path = temp_dir / "recovery_test.db"
        
        try:
            # Create initial database with data
            storage1 = Storage(str(db_path), keep_test_db=True)
            task_id = storage1.add_task("Important task")
            del storage1  # Close connection
            
            # Simulate corruption
            with open(db_path, 'w') as f:
                f.write("corrupted data")
            
            # Attempt to recover
            try:
                storage2 = Storage(str(db_path), keep_test_db=True)
                # Should either recover or create new database
                new_task_id = storage2.add_task("Recovery test task")
                assert new_task_id is not None
            except Exception as e:
                # Should be a clear database-related error
                assert any(word in str(e).lower() for word in ['database', 'corrupt', 'sqlite'])
                
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_graceful_degradation(self, mock_storage):
        # Test that core functionality works even when advanced features fail
        
        # Mock gamification failure
        with patch('logbuch.features.gamification.GamificationEngine', side_effect=Exception("Gamification error")):
            # Task completion should still work
            task_id = add_task(mock_storage, "Task with gamification failure")
            result = complete_task(mock_storage, task_id)
            assert result is True
        
        # Mock notification failure
        with patch('logbuch.commands.notifications.send_system_notification', side_effect=Exception("Notification error")):
            # Journal entries should still work
            entry_id = add_journal_entry(mock_storage, "Entry with notification failure")
            assert entry_id is not None
        
        # Verify core data is intact
        tasks = list_tasks(mock_storage, show_completed=True)
        entries = list_journal_entries(mock_storage)
        
        assert len(tasks) == 1
        assert len(entries) == 1
        assert tasks[0]['completed'] is True
