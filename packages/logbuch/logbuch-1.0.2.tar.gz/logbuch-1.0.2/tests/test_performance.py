#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# tests/test_performance.py

import pytest
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from unittest.mock import Mock, patch
import random
import string
from datetime import datetime, timedelta

from tests.test_mocks import (
    MockStorage, PerformanceTimer, generate_large_test_dataset,
    create_sample_task_data, create_sample_journal_data
)

from logbuch.commands.task import add_task, list_tasks, complete_task
from logbuch.commands.journal import add_journal_entry, list_journal_entries
from logbuch.commands.mood import add_mood_entry, list_mood_entries
from logbuch.storage import Storage


class TestBasicPerformance:
    @pytest.mark.performance
    def test_task_creation_performance(self, mock_storage):
        task_count = 1000
        
        with PerformanceTimer() as timer:
            for i in range(task_count):
                add_task(
                    mock_storage,
                    f"Performance test task {i}",
                    priority=random.choice(['low', 'medium', 'high']),
                    tags=[f"tag{i%10}", "performance"],
                    board=random.choice(['default', 'work', 'personal'])
                )
        
        # Should create 1000 tasks in under 2 seconds
        assert timer.elapsed < 2.0
        
        # Verify all tasks were created
        tasks = list_tasks(mock_storage)
        assert len(tasks) == task_count
    
    @pytest.mark.performance
    def test_task_retrieval_performance(self, mock_storage):
        # Create a large number of tasks
        task_count = 5000
        for i in range(task_count):
            add_task(mock_storage, f"Task {i}", tags=[f"tag{i%100}"])
        
        # Test basic retrieval
        with PerformanceTimer() as timer:
            all_tasks = list_tasks(mock_storage)
        
        assert timer.elapsed < 1.0
        assert len(all_tasks) == task_count
        
        # Test filtered retrieval
        with PerformanceTimer() as timer:
            filtered_tasks = list_tasks(mock_storage, tag="tag50")
        
        assert timer.elapsed < 0.5
        assert len(filtered_tasks) == 50  # Every 100th task
    
    @pytest.mark.performance
    def test_journal_entry_performance(self, mock_storage):
        entry_count = 2000
        
        # Test creation performance
        with PerformanceTimer() as timer:
            for i in range(entry_count):
                text = f"Performance test journal entry {i}. " + \
                       "This is a longer text to simulate realistic journal entries. " * 3
                add_journal_entry(
                    mock_storage,
                    text,
                    tags=[f"tag{i%20}", "performance"],
                    category=random.choice(['daily', 'work', 'personal', 'reflection'])
                )
        
        # Should create 2000 entries in under 3 seconds
        assert timer.elapsed < 3.0
        
        # Test retrieval performance
        with PerformanceTimer() as timer:
            all_entries = list_journal_entries(mock_storage)
        
        assert timer.elapsed < 1.0
        assert len(all_entries) == entry_count
    
    @pytest.mark.performance
    def test_mixed_operations_performance(self, mock_storage):
        operations_count = 1000
        
        with PerformanceTimer() as timer:
            for i in range(operations_count):
                operation = i % 4
                
                if operation == 0:
                    # Add task
                    add_task(mock_storage, f"Mixed op task {i}")
                elif operation == 1:
                    # Add journal entry
                    add_journal_entry(mock_storage, f"Mixed op journal {i}")
                elif operation == 2:
                    # Add mood entry
                    add_mood_entry(mock_storage, random.choice(['happy', 'sad', 'excited', 'calm']))
                else:
                    # List tasks
                    list_tasks(mock_storage)
        
        # Mixed operations should complete quickly
        assert timer.elapsed < 5.0


class TestScalabilityPerformance:
    @pytest.mark.performance
    @pytest.mark.slow
    def test_task_scalability(self, mock_storage):
        sizes = [100, 500, 1000, 2000, 5000]
        creation_times = []
        retrieval_times = []
        
        for size in sizes:
            # Clear storage
            mock_storage.tasks.clear()
            
            # Test creation time
            with PerformanceTimer() as timer:
                for i in range(size):
                    add_task(mock_storage, f"Scalability task {i}")
            creation_times.append(timer.elapsed)
            
            # Test retrieval time
            with PerformanceTimer() as timer:
                tasks = list_tasks(mock_storage)
            retrieval_times.append(timer.elapsed)
            
            assert len(tasks) == size
        
        # Creation time should scale roughly linearly
        # (allowing for some variance in mock operations)
        assert creation_times[-1] < creation_times[0] * 100  # Not more than 100x slower
        
        # Retrieval time should remain relatively constant for mock storage
        assert all(t < 1.0 for t in retrieval_times)
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_search_scalability(self, mock_storage):
        # Create datasets of increasing size
        sizes = [1000, 2000, 5000, 10000]
        search_times = []
        
        for size in sizes:
            # Clear and populate storage
            mock_storage.tasks.clear()
            
            for i in range(size):
                tags = [f"tag{i%100}", "common"] if i % 10 == 0 else [f"tag{i%100}"]
                add_task(mock_storage, f"Search test task {i}", tags=tags)
            
            # Test search performance
            with PerformanceTimer() as timer:
                # Search for common tag (should find size/10 results)
                common_tasks = list_tasks(mock_storage, tag="common")
            search_times.append(timer.elapsed)
            
            expected_results = size // 10
            assert len(common_tasks) == expected_results
        
        # Search time should remain reasonable even with large datasets
        assert all(t < 2.0 for t in search_times)


class TestConcurrencyPerformance:
    @pytest.mark.performance
    def test_concurrent_task_creation(self, mock_storage):
        def create_tasks(thread_id, task_count):
            for i in range(task_count):
                add_task(mock_storage, f"Thread {thread_id} task {i}")
        
        thread_count = 5
        tasks_per_thread = 200
        
        with PerformanceTimer() as timer:
            threads = []
            for thread_id in range(thread_count):
                thread = threading.Thread(
                    target=create_tasks,
                    args=(thread_id, tasks_per_thread)
                )
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
        
        # Concurrent creation should complete in reasonable time
        assert timer.elapsed < 10.0
        
        # Verify all tasks were created
        tasks = list_tasks(mock_storage)
        assert len(tasks) == thread_count * tasks_per_thread
    
    @pytest.mark.performance
    def test_concurrent_read_write(self, mock_storage):
        def writer_task(writer_id):
            for i in range(100):
                add_task(mock_storage, f"Writer {writer_id} task {i}")
                time.sleep(0.001)  # Small delay to simulate real work
        
        def reader_task(reader_id):
            for i in range(50):
                tasks = list_tasks(mock_storage)
                time.sleep(0.002)  # Small delay to simulate real work
        
        with PerformanceTimer() as timer:
            threads = []
            
            # Start writer threads
            for writer_id in range(3):
                thread = threading.Thread(target=writer_task, args=(writer_id,))
                threads.append(thread)
                thread.start()
            
            # Start reader threads
            for reader_id in range(2):
                thread = threading.Thread(target=reader_task, args=(reader_id,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
        
        # Concurrent operations should complete in reasonable time
        assert timer.elapsed < 15.0
        
        # Verify data integrity
        tasks = list_tasks(mock_storage)
        assert len(tasks) == 300  # 3 writers * 100 tasks each


class TestMemoryPerformance:
    @pytest.mark.performance
    def test_memory_usage_with_large_dataset(self, mock_storage):
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large dataset
        large_task_count = 10000
        for i in range(large_task_count):
            content = f"Large dataset task {i}: " + "x" * 100  # Longer content
            add_task(
                mock_storage,
                content,
                tags=[f"tag{i%50}", "large", "dataset"],
                priority=random.choice(['low', 'medium', 'high'])
            )
        
        # Add journal entries
        for i in range(5000):
            text = f"Large dataset journal entry {i}: " + \
                   "This is a longer journal entry to test memory usage. " * 10
            add_journal_entry(mock_storage, text, tags=[f"tag{i%30}"])
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for mock storage)
        assert memory_increase < 100 * 1024 * 1024  # 100MB
        
        # Verify data is accessible
        tasks = list_tasks(mock_storage)
        entries = list_journal_entries(mock_storage)
        
        assert len(tasks) == large_task_count
        assert len(entries) == 5000
    
    @pytest.mark.performance
    def test_memory_cleanup_after_operations(self, mock_storage):
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        def create_and_delete_data():
            # Create data
            task_ids = []
            for i in range(1000):
                task_id = add_task(mock_storage, f"Temp task {i}")
                task_ids.append(task_id)
            
            # Delete data
            for task_id in task_ids:
                mock_storage.delete_task(task_id)
        
        initial_memory = process.memory_info().rss
        
        # Perform operations multiple times
        for _ in range(10):
            create_and_delete_data()
            gc.collect()  # Force garbage collection
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory should not increase significantly after cleanup
        assert memory_increase < 50 * 1024 * 1024  # 50MB


class TestRealWorldPerformance:
    @pytest.mark.performance
    def test_daily_usage_performance(self, mock_storage):
        def simulate_daily_usage():
            # Morning: Add tasks for the day
            for i in range(10):
                add_task(
                    mock_storage,
                    f"Daily task {i}",
                    priority=random.choice(['low', 'medium', 'high']),
                    tags=random.sample(['work', 'personal', 'health', 'learning'], 2)
                )
            
            # Throughout day: Add journal entries
            for i in range(3):
                add_journal_entry(
                    mock_storage,
                    f"Daily journal entry {i}: " + "Thoughts and reflections. " * 20,
                    tags=random.sample(['work', 'personal', 'reflection'], 1)
                )
            
            # Complete some tasks
            tasks = list_tasks(mock_storage)
            for task in tasks[:5]:  # Complete half the tasks
                with patch('logbuch.commands.task.GamificationEngine'):
                    complete_task(mock_storage, task['id'])
            
            # Add mood entries
            for i in range(2):
                add_mood_entry(
                    mock_storage,
                    random.choice(['happy', 'productive', 'focused', 'tired']),
                    f"Daily mood note {i}"
                )
            
            # Check various lists
            list_tasks(mock_storage)
            list_tasks(mock_storage, show_completed=True)
            list_journal_entries(mock_storage, limit=10)
            list_mood_entries(mock_storage, limit=5)
        
        # Simulate 30 days of usage
        with PerformanceTimer() as timer:
            for day in range(30):
                simulate_daily_usage()
        
        # 30 days of usage should complete in reasonable time
        assert timer.elapsed < 30.0  # Less than 1 second per day
        
        # Verify accumulated data
        all_tasks = list_tasks(mock_storage, show_completed=True)
        all_entries = list_journal_entries(mock_storage)
        all_moods = list_mood_entries(mock_storage)
        
        assert len(all_tasks) == 300  # 10 tasks per day * 30 days
        assert len(all_entries) == 90  # 3 entries per day * 30 days
        assert len(all_moods) == 60   # 2 moods per day * 30 days
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_weekly_review_performance(self, mock_storage):
        # Simulate a week of data
        for day in range(7):
            for hour in range(24):
                if random.random() < 0.1:  # 10% chance each hour
                    add_task(mock_storage, f"Day {day} hour {hour} task")
                
                if random.random() < 0.05:  # 5% chance each hour
                    add_journal_entry(
                        mock_storage,
                        f"Day {day} hour {hour} journal entry with longer text. " * 10
                    )
        
        # Weekly review operations
        with PerformanceTimer() as timer:
            # Get all data for review
            all_tasks = list_tasks(mock_storage, show_completed=True)
            all_entries = list_journal_entries(mock_storage)
            all_moods = list_mood_entries(mock_storage)
            
            # Filter by different criteria
            work_tasks = list_tasks(mock_storage, tag="work")
            personal_entries = list_journal_entries(mock_storage, tag="personal")
            
            # Generate statistics (simulated)
            completed_tasks = [t for t in all_tasks if t['completed']]
            pending_tasks = [t for t in all_tasks if not t['completed']]
            
            # Create weekly review entry
            review_text = f"""
            Weekly Review:
            - Total tasks: {len(all_tasks)}
            - Completed: {len(completed_tasks)}
            - Pending: {len(pending_tasks)}
            - Journal entries: {len(all_entries)}
            - Mood entries: {len(all_moods)}
            """
            
            add_journal_entry(mock_storage, review_text, tags=["weekly-review"])
        
        # Weekly review should complete quickly
        assert timer.elapsed < 5.0


class TestDatabasePerformance:
    @pytest.mark.performance
    def test_real_database_performance(self, temp_dir):
        db_path = temp_dir / "performance_test.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Test bulk insert performance
            task_count = 1000
            
            with PerformanceTimer() as timer:
                for i in range(task_count):
                    storage.add_task(
                        f"DB performance task {i}",
                        priority=random.choice(['low', 'medium', 'high']),
                        tags=[f"tag{i%20}", "performance"]
                    )
            
            # Should insert 1000 tasks in under 5 seconds
            assert timer.elapsed < 5.0
            
            # Test query performance
            with PerformanceTimer() as timer:
                tasks = storage.get_tasks()
            
            assert timer.elapsed < 1.0
            assert len(tasks) == task_count
            
            # Test filtered query performance
            with PerformanceTimer() as timer:
                filtered_tasks = storage.get_tasks(tag="tag5")
            
            assert timer.elapsed < 1.0
            assert len(filtered_tasks) == 50  # Every 20th task
            
        finally:
            if db_path.exists():
                db_path.unlink()
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_database_backup_performance(self, temp_dir):
        db_path = temp_dir / "backup_performance_test.db"
        storage = Storage(str(db_path), keep_test_db=True)
        
        try:
            # Add substantial amount of data
            for i in range(2000):
                storage.add_task(f"Backup test task {i}")
                if i % 10 == 0:
                    storage.add_journal_entry(f"Backup test entry {i//10}")
            
            # Test backup performance
            with PerformanceTimer() as timer:
                backup_path = storage.create_backup()
            
            # Backup should complete in reasonable time
            assert timer.elapsed < 10.0
            assert backup_path is not None
            
            # Verify backup integrity
            backup_storage = Storage(backup_path, keep_test_db=True)
            backup_tasks = backup_storage.get_tasks()
            backup_entries = backup_storage.get_journal_entries()
            
            assert len(backup_tasks) == 2000
            assert len(backup_entries) == 200
            
        finally:
            if db_path.exists():
                db_path.unlink()


# Benchmark utilities

def run_performance_benchmark():
    print("Running Logbuch Performance Benchmark...")
    print("=" * 50)
    
    mock_storage = MockStorage()
    
    # Task operations benchmark
    print("Task Operations:")
    with PerformanceTimer() as timer:
        for i in range(1000):
            add_task(mock_storage, f"Benchmark task {i}")
    print(f"  Create 1000 tasks: {timer.elapsed:.3f}s")
    
    with PerformanceTimer() as timer:
        tasks = list_tasks(mock_storage)
    print(f"  List 1000 tasks: {timer.elapsed:.3f}s")
    
    # Journal operations benchmark
    print("\nJournal Operations:")
    with PerformanceTimer() as timer:
        for i in range(500):
            add_journal_entry(mock_storage, f"Benchmark entry {i}" + " text" * 50)
    print(f"  Create 500 entries: {timer.elapsed:.3f}s")
    
    with PerformanceTimer() as timer:
        entries = list_journal_entries(mock_storage)
    print(f"  List 500 entries: {timer.elapsed:.3f}s")
    
    # Search benchmark
    print("\nSearch Operations:")
    with PerformanceTimer() as timer:
        work_tasks = list_tasks(mock_storage, tag="work")
    print(f"  Search tasks by tag: {timer.elapsed:.3f}s")
    
    print("\nBenchmark completed!")


if __name__ == "__main__":
    run_performance_benchmark()
