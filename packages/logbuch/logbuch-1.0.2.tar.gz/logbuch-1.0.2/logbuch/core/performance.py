#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import time
import functools
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timedelta
import sqlite3
from contextlib import contextmanager

from logbuch.core.logger import get_logger

logger = get_logger(__name__)


class PerformanceMonitor:
    def __init__(self):
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.slow_query_threshold = 0.1  # 100ms
        self.performance_stats = {
            'queries': [],
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def time_function(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > self.slow_query_threshold:
                    logger.warning(f"Slow operation: {func.__name__} took {execution_time:.3f}s")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Error in {func.__name__} after {execution_time:.3f}s: {e}")
                raise
        
        return wrapper
    
    def cache_query(self, query: str, params: tuple = None) -> Optional[Any]:
        cache_key = f"{query}:{str(params)}"
        
        if cache_key in self.query_cache:
            cached_data, timestamp = self.query_cache[cache_key]
            
            if time.time() - timestamp < self.cache_ttl:
                self.performance_stats['cache_hits'] += 1
                return cached_data
            else:
                # Remove expired cache entry
                del self.query_cache[cache_key]
        
        self.performance_stats['cache_misses'] += 1
        return None
    
    def store_query_cache(self, query: str, params: tuple, result: Any):
        cache_key = f"{query}:{str(params)}"
        self.query_cache[cache_key] = (result, time.time())
        
        # Limit cache size
        if len(self.query_cache) > 100:
            # Remove oldest entries
            oldest_keys = sorted(
                self.query_cache.keys(),
                key=lambda k: self.query_cache[k][1]
            )[:20]
            
            for key in oldest_keys:
                del self.query_cache[key]
    
    def clear_cache(self):
        self.query_cache.clear()
        logger.info("Performance cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.performance_stats['cache_hits'] + self.performance_stats['cache_misses']
        hit_rate = (self.performance_stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.query_cache),
            'cache_hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total_requests,
            'cache_hits': self.performance_stats['cache_hits'],
            'cache_misses': self.performance_stats['cache_misses']
        }


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


class OptimizedStorage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_pool = []
        self.max_connections = 5
    
    @contextmanager
    def get_connection(self):
        if self.connection_pool:
            conn = self.connection_pool.pop()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Performance optimizations
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
        
        try:
            yield conn
        finally:
            if len(self.connection_pool) < self.max_connections:
                self.connection_pool.append(conn)
            else:
                conn.close()
    
    @perf_monitor.time_function
    def execute_query(self, query: str, params: tuple = None, use_cache: bool = True) -> List[sqlite3.Row]:
        # Check cache first for SELECT queries
        if use_cache and query.strip().upper().startswith('SELECT'):
            cached_result = perf_monitor.cache_query(query, params)
            if cached_result is not None:
                return cached_result
        
        start_time = time.time()
        
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchall()
                
                # Cache SELECT results
                if use_cache and query.strip().upper().startswith('SELECT'):
                    perf_monitor.store_query_cache(query, params, result)
                
                # Commit for non-SELECT queries
                if not query.strip().upper().startswith('SELECT'):
                    conn.commit()
                
                execution_time = time.time() - start_time
                
                # Log slow queries
                if execution_time > perf_monitor.slow_query_threshold:
                    logger.warning(f"Slow query ({execution_time:.3f}s): {query[:100]}...")
                
                return result
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise


def optimize_task_queries():
    optimizations = [
        # Index for task status queries
        "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
        
        # Index for task priority queries
        "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
        
        # Index for task creation date queries
        "CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)",
        
        # Index for task completion date queries
        "CREATE INDEX IF NOT EXISTS idx_tasks_completed_at ON tasks(completed_at)",
        
        # Composite index for common filters
        "CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks(status, priority)",
        
        # Index for time entries
        "CREATE INDEX IF NOT EXISTS idx_time_entries_task_id ON time_entries(task_id)",
        
        # Index for achievements
        "CREATE INDEX IF NOT EXISTS idx_achievements_earned_at ON achievements(earned_at)",
    ]
    
    return optimizations


class PaginatedQuery:
    def __init__(self, base_query: str, params: tuple = None, page_size: int = 20):
        self.base_query = base_query
        self.params = params or ()
        self.page_size = page_size
        self.current_page = 0
    
    def get_page(self, page: int = None) -> Dict[str, Any]:
        if page is not None:
            self.current_page = page
        
        offset = self.current_page * self.page_size
        
        # Add LIMIT and OFFSET to query
        paginated_query = f"{self.base_query} LIMIT {self.page_size} OFFSET {offset}"
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM ({self.base_query})"
        
        from logbuch.storage import Storage
        storage = Storage()
        
        results = storage.execute_query(paginated_query, self.params)
        total_count = storage.execute_query(count_query, self.params)[0][0]
        
        total_pages = (total_count + self.page_size - 1) // self.page_size
        
        return {
            'results': results,
            'current_page': self.current_page,
            'total_pages': total_pages,
            'total_count': total_count,
            'page_size': self.page_size,
            'has_next': self.current_page < total_pages - 1,
            'has_prev': self.current_page > 0
        }
    
    def next_page(self) -> Dict[str, Any]:
        return self.get_page(self.current_page + 1)
    
    def prev_page(self) -> Dict[str, Any]:
        return self.get_page(max(0, self.current_page - 1))


def optimize_database_startup():
    startup_optimizations = [
        # Analyze tables for better query planning
        "ANALYZE",
        
        # Vacuum to defragment database
        "VACUUM",
        
        # Update statistics
        "PRAGMA optimize",
    ]
    
    return startup_optimizations


class LazyLoader:
    def __init__(self, loader_func: Callable, *args, **kwargs):
        self.loader_func = loader_func
        self.args = args
        self.kwargs = kwargs
        self._loaded = False
        self._data = None
    
    def load(self):
        if not self._loaded:
            self._data = self.loader_func(*self.args, **self.kwargs)
            self._loaded = True
        return self._data
    
    @property
    def data(self):
        return self.load()


def batch_operations(operations: List[Callable], batch_size: int = 100):
    results = []
    
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        
        batch_results = []
        for operation in batch:
            try:
                result = operation()
                batch_results.append(result)
            except Exception as e:
                logger.error(f"Error in batch operation: {e}")
                batch_results.append(None)
        
        results.extend(batch_results)
    
    return results


# Performance decorators
def cached(ttl: int = 300):
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return result
                else:
                    del cache[cache_key]
            
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator


def async_background(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # For now, just run normally
        # In a full implementation, this would use threading or asyncio
        return func(*args, **kwargs)
    
    return wrapper


# Export performance utilities
__all__ = [
    'PerformanceMonitor',
    'OptimizedStorage', 
    'PaginatedQuery',
    'LazyLoader',
    'perf_monitor',
    'cached',
    'async_background',
    'optimize_task_queries',
    'optimize_database_startup',
    'batch_operations'
]
