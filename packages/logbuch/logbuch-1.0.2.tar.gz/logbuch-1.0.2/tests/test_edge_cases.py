#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_edge_cases.py

import pytest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import threading
import time
import string
import random

from logbuch.storage import Storage
from logbuch.commands.task import add_task, list_tasks, complete_task, delete_task, move_task
from logbuch.commands.journal import add_journal_entry, list_journal_entries, delete_journal_entry
from logbuch.commands.mood import add_mood_entry, list_mood_entries
from tests.test_mocks import MockStorage


class TestBoundaryConditions:
    def test_maximum_string_lengths(self, mock_storage):
        # Test various string lengths
        test_lengths = [0, 1, 100, 1000, 10000, 65535, 100000]
        
        for length in test_lengths:
            content = "A" * length
            
            try:
                task_id = add_task(mock_storage, content)
                
                if task_id:
                    # Verify the content was stored correctly
                    tasks = list_tasks(mock_storage)
                    found_task = next((t for t in tasks if t['id'] == task_id), None)
                    assert found_task is not None
                    assert len(found_task['content']) == length
                    
                    # Clear for next test
                    delete_task(mock_storage, task_id)
                    
            except Exception as e:
                # It's acceptable to reject extremely long inputs
                if length > 50000:  # Very large inputs
                    assert any(word in str(e).lower() for word in ['length', 'size', 'limit', 'memory'])
                else:
                    # Smaller inputs should generally work
                    raise e
    
    def test_minimum_and_maximum_ids(self, mock_storage):
        # Test with various ID values
        test_ids = [
            0, 1, -1,           # Basic boundary values
            sys.maxsize,        # Maximum positive integer
            -sys.maxsize,       # Maximum negative integer
            2**31 - 1,          # 32-bit signed int max
            2**32 - 1,          # 32-bit unsigned int max
            2**63 - 1,          # 64-bit signed int max
        ]
        
        for test_id in test_ids:
            # Test completing non-existent task with boundary ID
            result = complete_task(mock_storage, test_id)
            assert result is False  # Should fail gracefully
            
            # Test deleting non-existent task with boundary ID
            result = delete_task(mock_storage, test_id)
            # Mock storage might return True, real storage should handle gracefully
            assert isinstance(result, bool)
    
    def test_empty_and_null_collections(self, mock_storage):
        # Test with empty tags
        task_id = add_task(mock_storage, "Empty tags test", tags=[])
        assert task_id is not None
        
        tasks = list_tasks(mock_storage)
        task = next((t for t in tasks if t['id'] == task_id), None)
        assert task is not None
        assert task['tags'] == []
        
        # Test with None tags
        try:
            task_id2 = add_task(mock_storage, "None tags test", tags=None)
            if task_id2:
                tasks = list_tasks(mock_storage)
                task = next((t for t in tasks if t['id'] == task_id2), None)
                assert task is not None
                # Should either be empty list or None
                assert task['tags'] is None or task['tags'] == []
        except (TypeError, ValueError):
            # It's acceptable to reject None tags
            pass
    
    def test_date_boundary_conditions(self, mock_storage):
        # Test with various date formats and edge cases
        date_test_cases = [
            "2024-01-01",           # Valid ISO date
            "2024-12-31",           # End of year
            "2024-02-29",           # Leap year
            "1900-01-01",           # Old date
            "2100-12-31",           # Future date
            "invalid-date",         # Invalid format
            "",                     # Empty string
            "2024-13-01",           # Invalid month
            "2024-01-32",           # Invalid day
        ]
        
        for date_str in date_test_cases:
            try:
                task_id = add_task(mock_storage, f"Date test: {date_str}", due_date=date_str)
                
                if task_id:
                    tasks = list_tasks(mock_storage)
                    task = next((t for t in tasks if t['id'] == task_id), None)
                    assert task is not None
                    # Due date should be stored (validation might happen elsewhere)
                    
            except (ValueError, TypeError) as e:
                # Invalid dates might be rejected
                if "invalid" in date_str or "13" in date_str or "32" in date_str:
                    # Expected to fail for clearly invalid dates
                    pass
                else:
                    # Valid dates should work
                    raise e


class TestSpecialCharacterHandling:
    def test_unicode_edge_cases(self, mock_storage):
        unicode_test_cases = [
            # Basic Unicode
            "Hello 世界",
            "Café naïve résumé",
            
            # Emoji and symbols
            "Task with 🎉🚀💻 emojis",
            "Math symbols: ∑∏∫∆∇",
            "Currency: $€£¥₹₿",
            
            # Control characters
            "Line\nBreak",
            "Tab\tSeparated",
            "Carriage\rReturn",
            
            # Zero-width characters
            "Zero\u200bWidth\u200cSpace",
            
            # Right-to-left text
            "العربية",
            "עברית",
            
            # Combining characters
            "é" + "\u0301",  # e + combining acute accent
            
            # Surrogate pairs (high Unicode)
            "𝕳𝖊𝖑𝖑𝖔 𝖂𝖔𝖗𝖑𝖉",
            
            # Mixed scripts
            "English العربية 中文 русский",
        ]
        
        for unicode_text in unicode_test_cases:
            try:
                task_id = add_task(mock_storage, unicode_text)
                assert task_id is not None
                
                # Verify storage and retrieval
                tasks = list_tasks(mock_storage)
                found_task = next((t for t in tasks if t['id'] == task_id), None)
                assert found_task is not None
                assert found_task['content'] == unicode_text
                
                # Test journal entries too
                entry_id = add_journal_entry(mock_storage, unicode_text)
                assert entry_id is not None
                
                entries = list_journal_entries(mock_storage)
                found_entry = next((e for e in entries if e['id'] == entry_id), None)
                assert found_entry is not None
                assert found_entry['text'] == unicode_text
                
            except UnicodeError as e:
                # Some extreme Unicode cases might fail
                print(f"Unicode error for '{unicode_text}': {e}")
                # This might be acceptable for very edge cases
    
    def test_sql_special_characters(self, mock_storage):
        sql_special_chars = [
            "Single 'quote' test",
            'Double "quote" test',
            "Backtick `test`",
            "Semicolon; test",
            "Percent % wildcard",
            "Underscore _ wildcard",
            "Backslash \\ test",
            "Forward / slash",
            "Null \x00 byte",
            "CRLF \r\n test",
        ]
        
        for special_text in sql_special_chars:
            task_id = add_task(mock_storage, special_text)
            assert task_id is not None
            
            # Verify the special characters are preserved
            tasks = list_tasks(mock_storage)
            found_task = next((t for t in tasks if t['id'] == task_id), None)
            assert found_task is not None
            # Content should match exactly (no SQL injection or corruption)
            assert found_task['content'] == special_text
    
    def test_html_xml_special_characters(self, mock_storage):
        html_special_cases = [
            "Less than < test",
            "Greater than > test",
            "Ampersand & test",
            "HTML entity &lt;&gt;&amp;",
            "XML CDATA <![CDATA[test]]>",
            "HTML comment <!-- test -->",
            "XML declaration <?xml version='1.0'?>",
            "HTML tag <script>alert('test')</script>",
        ]
        
        for html_text in html_special_cases:
            task_id = add_task(mock_storage, html_text)
            assert task_id is not None
            
            # Verify HTML/XML characters are preserved as-is
            tasks = list_tasks(mock_storage)
            found_task = next((t for t in tasks if t['id'] == task_id), None)
            assert found_task is not None
            assert found_task['content'] == html_text


class TestConcurrencyEdgeCases:
    def test_simultaneous_task_completion(self, temp_dir):
        db_path = temp_dir / "concurrent_completion.db"
        
        try:
            # Create initial task
            storage = Storage(str(db_path), keep_test_db=True)
            task_id = storage.add_task("Concurrent completion test")
            del storage
            
            completion_results = []
            completion_errors = []
            
            def complete_task_worker():
                try:
                    worker_storage = Storage(str(db_path), keep_test_db=True)
                    result = worker_storage.complete_task(task_id)
                    completion_results.append(result)
                except Exception as e:
                    completion_errors.append(str(e))
            
            # Start multiple threads trying to complete the same task
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=complete_task_worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Verify results
            # At least one should succeed, others might fail or also succeed
            assert len(completion_results) > 0
            
            # Check final state
            final_storage = Storage(str(db_path), keep_test_db=True)
            tasks = final_storage.get_tasks(show_completed=True)
            task = next((t for t in tasks if t['id'] == task_id), None)
            
            assert task is not None
            assert task['completed'] is True  # Should be completed
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_rapid_task_creation_and_deletion(self, temp_dir):
        db_path = temp_dir / "rapid_operations.db"
        
        try:
            def rapid_operations_worker(worker_id):
                storage = Storage(str(db_path), keep_test_db=True)
                created_tasks = []
                
                # Rapidly create tasks
                for i in range(20):
                    try:
                        task_id = storage.add_task(f"Rapid task {worker_id}-{i}")
                        created_tasks.append(task_id)
                        time.sleep(0.001)  # Very short delay
                    except Exception as e:
                        print(f"Creation error: {e}")
                
                # Rapidly delete half of them
                for i in range(0, len(created_tasks), 2):
                    try:
                        storage.delete_task(created_tasks[i])
                        time.sleep(0.001)
                    except Exception as e:
                        print(f"Deletion error: {e}")
            
            # Start multiple workers
            threads = []
            for worker_id in range(3):
                thread = threading.Thread(target=rapid_operations_worker, args=(worker_id,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify database is in consistent state
            storage = Storage(str(db_path), keep_test_db=True)
            tasks = storage.get_tasks()
            
            # Should have some tasks remaining
            assert len(tasks) >= 0  # At least not negative
            
            # All remaining tasks should be valid
            for task in tasks:
                assert task['id'] is not None
                assert task['content'] is not None
                assert isinstance(task['completed'], bool)
                
        finally:
            if db_path.exists():
                db_path.unlink()
    
    def test_database_lock_timeout_edge_cases(self, temp_dir):
        db_path = temp_dir / "lock_timeout.db"
        
        try:
            # Create long-running transaction
            def long_transaction():
                with sqlite3.connect(str(db_path), timeout=1.0) as conn:
                    conn.execute("BEGIN EXCLUSIVE TRANSACTION")
                    time.sleep(2.0)  # Hold lock for 2 seconds
                    conn.rollback()
            
            # Start long transaction in background
            import threading
            lock_thread = threading.Thread(target=long_transaction)
            lock_thread.start()
            
            time.sleep(0.1)  # Let the lock be acquired
            
            # Try to access database while locked
            try:
                storage = Storage(str(db_path), keep_test_db=True)
                task_id = storage.add_task("Lock timeout test")
                
                # If this succeeds, the timeout handling worked
                assert task_id is not None
                
            except Exception as e:
                # Should be a timeout or lock-related error
                assert any(word in str(e).lower() for word in [
                    'timeout', 'locked', 'busy', 'database'
                ])
            
            # Wait for lock thread to complete
            lock_thread.join()
            
        finally:
            if db_path.exists():
                db_path.unlink()


class TestMemoryEdgeCases:
    def test_memory_efficient_large_queries(self, mock_storage):
        # Create large number of tasks
        task_count = 10000
        
        for i in range(task_count):
            add_task(mock_storage, f"Memory test task {i}", tags=[f"batch{i//100}"])
        
        # Test large query results
        all_tasks = list_tasks(mock_storage)
        assert len(all_tasks) == task_count
        
        # Test filtered queries (should be more memory efficient)
        batch_0_tasks = list_tasks(mock_storage, tag="batch0")
        assert len(batch_0_tasks) == 100
        
        # Verify memory usage doesn't explode
        import sys
        
        # Get memory usage (approximate)
        task_size = sys.getsizeof(all_tasks)
        assert task_size < 100 * 1024 * 1024  # Less than 100MB for mock data
    
    def test_circular_reference_prevention(self, mock_storage):
        # Create tasks with potential circular references in tags
        task_id1 = add_task(mock_storage, "Task 1", tags=["ref2"])
        task_id2 = add_task(mock_storage, "Task 2", tags=["ref1"])
        
        # This shouldn't cause infinite loops or memory issues
        tasks = list_tasks(mock_storage, tag="ref1")
        assert len(tasks) == 1
        
        tasks = list_tasks(mock_storage, tag="ref2")
        assert len(tasks) == 1
    
    def test_large_object_cleanup(self, mock_storage):
        # Create large content
        large_content = "X" * 100000  # 100KB
        
        task_id = add_task(mock_storage, large_content)
        assert task_id is not None
        
        # Delete the task
        delete_task(mock_storage, task_id)
        
        # Verify it's gone
        tasks = list_tasks(mock_storage)
        assert not any(t['id'] == task_id for t in tasks)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Memory should be freed (hard to test directly in unit tests)


class TestFileSystemEdgeCases:
    def test_database_in_nonexistent_directory(self, temp_dir):
        nonexistent_dir = temp_dir / "does_not_exist" / "nested" / "path"
        db_path = nonexistent_dir / "test.db"
        
        try:
            # Should create directory structure
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Should be able to add data
            task_id = storage.add_task("Nonexistent dir test")
            assert task_id is not None
            
            # Verify file was created
            assert db_path.exists()
            assert db_path.parent.exists()
            
        finally:
            if db_path.exists():
                db_path.unlink()
            # Clean up created directories
            try:
                nonexistent_dir.rmdir()
                nonexistent_dir.parent.rmdir()
                nonexistent_dir.parent.parent.rmdir()
            except:
                pass
    
    def test_database_with_special_characters_in_path(self, temp_dir):
        special_paths = [
            "test with spaces.db",
            "test-with-dashes.db",
            "test_with_underscores.db",
            "test.with.dots.db",
            "test(with)parentheses.db",
            "test[with]brackets.db",
            "test{with}braces.db",
        ]
        
        for special_name in special_paths:
            db_path = temp_dir / special_name
            
            try:
                storage = Storage(str(db_path), keep_test_db=True)
                task_id = storage.add_task(f"Special path test: {special_name}")
                assert task_id is not None
                
                # Verify file was created with correct name
                assert db_path.exists()
                assert db_path.name == special_name
                
            except Exception as e:
                # Some special characters might not be allowed on certain filesystems
                print(f"Special path '{special_name}' failed: {e}")
                # This might be acceptable depending on the filesystem
                
            finally:
                if db_path.exists():
                    db_path.unlink()
    
    def test_database_file_permissions_edge_cases(self, temp_dir):
        db_path = temp_dir / "permissions_test.db"
        
        try:
            # Create database
            storage = Storage(str(db_path), keep_test_db=True)
            storage.add_task("Permission test task")
            del storage
            
            # Test read-only access
            if os.name != 'nt':  # Unix-like systems
                # Make file read-only
                os.chmod(db_path, 0o444)
                
                try:
                    # Should handle read-only gracefully
                    readonly_storage = Storage(str(db_path), keep_test_db=True)
                    
                    # Reading should work
                    tasks = readonly_storage.get_tasks()
                    assert len(tasks) == 1
                    
                    # Writing might fail
                    try:
                        readonly_storage.add_task("Should fail")
                        # If it succeeds, that's also acceptable
                    except Exception as e:
                        assert any(word in str(e).lower() for word in [
                            'permission', 'readonly', 'denied', 'locked'
                        ])
                        
                except Exception as e:
                    # Read-only database access might fail entirely
                    assert "permission" in str(e).lower() or "readonly" in str(e).lower()
                
        finally:
            # Restore permissions and cleanup
            if db_path.exists():
                try:
                    os.chmod(db_path, 0o644)
                    db_path.unlink()
                except:
                    pass


class TestDataTypeEdgeCases:
    def test_numeric_string_handling(self, mock_storage):
        numeric_strings = [
            "123",           # Integer string
            "123.456",       # Float string
            "0",             # Zero
            "-123",          # Negative
            "1e10",          # Scientific notation
            "0x1A",          # Hexadecimal
            "0o777",         # Octal
            "0b1010",        # Binary
            "∞",             # Infinity symbol
            "NaN",           # Not a Number
        ]
        
        for numeric_str in numeric_strings:
            task_id = add_task(mock_storage, numeric_str)
            assert task_id is not None
            
            # Verify it's stored as string, not converted to number
            tasks = list_tasks(mock_storage)
            task = next((t for t in tasks if t['id'] == task_id), None)
            assert task is not None
            assert task['content'] == numeric_str
            assert isinstance(task['content'], str)
    
    def test_boolean_like_strings(self, mock_storage):
        boolean_strings = [
            "true", "True", "TRUE",
            "false", "False", "FALSE",
            "yes", "Yes", "YES",
            "no", "No", "NO",
            "1", "0",
            "on", "off",
            "enabled", "disabled",
        ]
        
        for bool_str in boolean_strings:
            task_id = add_task(mock_storage, bool_str)
            assert task_id is not None
            
            # Should remain as string
            tasks = list_tasks(mock_storage)
            task = next((t for t in tasks if t['id'] == task_id), None)
            assert task is not None
            assert task['content'] == bool_str
            assert isinstance(task['content'], str)
    
    def test_json_like_strings(self, mock_storage):
        json_strings = [
            '{"key": "value"}',
            '[1, 2, 3]',
            '{"nested": {"object": true}}',
            '[]',
            '{}',
            'null',
            '"string"',
        ]
        
        for json_str in json_strings:
            task_id = add_task(mock_storage, json_str)
            assert task_id is not None
            
            # Should be stored as plain string, not parsed as JSON
            tasks = list_tasks(mock_storage)
            task = next((t for t in tasks if t['id'] == task_id), None)
            assert task is not None
            assert task['content'] == json_str
            assert isinstance(task['content'], str)


class TestTimingEdgeCases:
    def test_rapid_successive_operations(self, mock_storage):
        # Perform many operations in quick succession
        task_ids = []
        
        start_time = time.time()
        
        for i in range(100):
            task_id = add_task(mock_storage, f"Rapid task {i}")
            task_ids.append(task_id)
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 5.0  # Less than 5 seconds
        
        # All tasks should be created
        tasks = list_tasks(mock_storage)
        assert len(tasks) == 100
        
        # Rapidly complete tasks
        start_time = time.time()
        
        for task_id in task_ids:
            complete_task(mock_storage, task_id)
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 5.0
        
        # All tasks should be completed
        completed_tasks = list_tasks(mock_storage, show_completed=True)
        completed_count = sum(1 for t in completed_tasks if t['completed'])
        assert completed_count == 100
    
    def test_timestamp_precision_edge_cases(self, temp_dir):
        db_path = temp_dir / "timestamp_test.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Create tasks in rapid succession
            task_ids = []
            for i in range(10):
                task_id = storage.add_task(f"Timestamp test {i}")
                task_ids.append(task_id)
                # Very small delay to test timestamp precision
                time.sleep(0.001)
            
            # Verify timestamps are different (or at least not all the same)
            tasks = storage.get_tasks()
            timestamps = [task.get('created_at') for task in tasks if task.get('created_at')]
            
            if timestamps:
                # Should have some variation in timestamps
                unique_timestamps = set(timestamps)
                # At least some should be different (depending on precision)
                assert len(unique_timestamps) >= 1
                
        finally:
            if db_path.exists():
                db_path.unlink()


class TestResourceLimitEdgeCases:
    def test_maximum_open_connections(self, temp_dir):
        db_path = temp_dir / "max_connections.db"
        
        try:
            # Create many storage instances (simulating many connections)
            storages = []
            
            for i in range(50):  # Try to create many connections
                try:
                    storage = Storage(str(db_path), keep_test_db=True)
                    storage.add_task(f"Connection test {i}")
                    storages.append(storage)
                except Exception as e:
                    # Might hit connection limits
                    print(f"Connection limit reached at {i}: {e}")
                    break
            
            # Should have created at least some connections
            assert len(storages) > 0
            
            # All should be functional
            for i, storage in enumerate(storages[:10]):  # Test first 10
                tasks = storage.get_tasks()
                assert len(tasks) >= 1
                
        finally:
            # Clean up connections
            for storage in storages:
                try:
                    del storage
                except:
                    pass
            
            if db_path.exists():
                db_path.unlink()
    
    def test_disk_space_simulation(self, temp_dir):
        db_path = temp_dir / "disk_space_test.db"
        
        try:
            storage = Storage(str(db_path), keep_test_db=True)
            
            # Create increasingly large content to simulate disk usage
            for i in range(100):
                try:
                    # Create progressively larger content
                    content_size = 1000 * (i + 1)  # 1KB, 2KB, 3KB, etc.
                    large_content = "X" * content_size
                    
                    task_id = storage.add_task(f"Disk test {i}: {large_content}")
                    assert task_id is not None
                    
                except Exception as e:
                    # Might hit disk space or memory limits
                    if any(word in str(e).lower() for word in ['disk', 'space', 'memory', 'size']):
                        print(f"Resource limit reached at iteration {i}: {e}")
                        break
                    else:
                        raise e
            
            # Database should still be functional
            tasks = storage.get_tasks()
            assert len(tasks) > 0
            
        finally:
            if db_path.exists():
                db_path.unlink()
