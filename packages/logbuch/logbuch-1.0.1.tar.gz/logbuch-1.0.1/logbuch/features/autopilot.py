#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/autopilot.py

import datetime
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import random

from logbuch.core.logger import get_logger


class AutopilotMode(Enum):
    FULL_AUTO = "full_auto"          # Complete automation
    ASSISTED = "assisted"            # Suggestions with confirmation
    MANUAL = "manual"                # User-controlled
    LEARNING = "learning"            # Learning user patterns


@dataclass
class AutoTask:
    title: str
    description: str
    priority: str
    estimated_duration: int  # minutes
    optimal_time: str       # time of day
    context: str           # why it was created
    confidence: float      # AI confidence in suggestion


@dataclass
class WorkSession:
    start_time: datetime.datetime
    duration: int  # minutes
    task_ids: List[int]
    session_type: str  # focus, creative, admin, etc.
    break_intervals: List[int]  # break times in minutes


class ProductivityAutopilot:
    def __init__(self, storage):
        self.storage = storage
        self.logger = get_logger("autopilot")
        self.mode = AutopilotMode.ASSISTED
        self.learning_data = self._load_learning_data()
        
        # Autopilot settings
        self.auto_create_tasks_enabled = True
        self.auto_schedule_sessions_enabled = True
        self.auto_adjust_priorities_enabled = True
        self.auto_suggest_breaks_enabled = True
        self.auto_track_time_enabled = True
        
        self.logger.debug("Productivity Autopilot initialized")
    
    def _load_learning_data(self) -> Dict:
        try:
            from pathlib import Path
            learning_file = Path.home() / ".logbuch" / "autopilot_learning.json"
            
            if learning_file.exists():
                with open(learning_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.debug(f"Could not load learning data: {e}")
        
        return {
            "task_patterns": {},
            "time_preferences": {},
            "productivity_cycles": {},
            "break_patterns": {},
            "priority_adjustments": {}
        }
    
    def _save_learning_data(self):
        try:
            from pathlib import Path
            learning_file = Path.home() / ".logbuch" / "autopilot_learning.json"
            learning_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save learning data: {e}")
    
    def analyze_patterns(self) -> Dict[str, Any]:
        tasks = self.storage.get_tasks(show_completed=True)
        
        patterns = {
            "peak_hours": self._analyze_peak_productivity_hours(tasks),
            "task_types": self._analyze_task_type_patterns(tasks),
            "completion_cycles": self._analyze_completion_cycles(tasks),
            "priority_accuracy": self._analyze_priority_accuracy(tasks),
            "duration_estimates": self._analyze_duration_patterns(tasks)
        }
        
        # Update learning data
        self.learning_data.update(patterns)
        self._save_learning_data()
        
        return patterns
    
    def _analyze_peak_productivity_hours(self, tasks: List[Dict]) -> Dict:
        completed_tasks = [t for t in tasks if t.get('done') and t.get('completed_at')]
        
        if len(completed_tasks) < 5:
            return {"hours": [9, 10, 11, 14, 15], "confidence": 0.3}
        
        # Extract completion hours
        hours = []
        for task in completed_tasks:
            try:
                completed_at = datetime.datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                hours.append(completed_at.hour)
            except:
                continue
        
        # Find peak hours
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Get top 5 hours
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        peak_hour_list = [hour for hour, count in peak_hours]
        
        confidence = len(completed_tasks) / 50.0  # More data = higher confidence
        
        return {
            "hours": peak_hour_list,
            "confidence": min(confidence, 1.0),
            "distribution": hour_counts
        }
    
    def _analyze_task_type_patterns(self, tasks: List[Dict]) -> Dict:
        task_keywords = {}
        
        for task in tasks:
            title = task.get('title', '').lower()
            words = title.split()
            
            for word in words:
                if len(word) > 3:  # Skip short words
                    task_keywords[word] = task_keywords.get(word, 0) + 1
        
        # Get most common task types
        common_keywords = sorted(task_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "common_keywords": common_keywords,
            "total_tasks": len(tasks),
            "patterns": self._identify_task_patterns(tasks)
        }
    
    def _identify_task_patterns(self, tasks: List[Dict]) -> List[str]:
        patterns = []
        
        # Look for recurring patterns
        titles = [task.get('title', '').lower() for task in tasks]
        
        # Common productivity patterns
        if any('meeting' in title for title in titles):
            patterns.append("meeting_preparation")
        if any('email' in title for title in titles):
            patterns.append("email_management")
        if any('review' in title for title in titles):
            patterns.append("regular_reviews")
        if any('plan' in title for title in titles):
            patterns.append("planning_sessions")
        
        return patterns
    
    def _analyze_completion_cycles(self, tasks: List[Dict]) -> Dict:
        completed_tasks = [t for t in tasks if t.get('done') and t.get('completed_at')]
        
        if len(completed_tasks) < 10:
            return {"average_cycle": 1, "patterns": []}
        
        # Group by date
        daily_completions = {}
        for task in completed_tasks:
            try:
                date = datetime.datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00')).date()
                daily_completions[date] = daily_completions.get(date, 0) + 1
            except:
                continue
        
        # Analyze patterns
        completion_counts = list(daily_completions.values())
        avg_daily = sum(completion_counts) / len(completion_counts)
        
        return {
            "average_daily": avg_daily,
            "peak_days": [date for date, count in daily_completions.items() if count > avg_daily * 1.5],
            "low_days": [date for date, count in daily_completions.items() if count < avg_daily * 0.5]
        }
    
    def _analyze_priority_accuracy(self, tasks: List[Dict]) -> Dict:
        # This would analyze if high-priority tasks are actually completed first
        high_priority = [t for t in tasks if t.get('priority') == 'high']
        completed_high = [t for t in high_priority if t.get('done')]
        
        accuracy = len(completed_high) / len(high_priority) if high_priority else 0.5
        
        return {
            "priority_accuracy": accuracy,
            "high_priority_completion_rate": accuracy,
            "suggestions": ["Consider reviewing priority criteria"] if accuracy < 0.7 else []
        }
    
    def _analyze_duration_patterns(self, tasks: List[Dict]) -> Dict:
        # Mock analysis - would track actual time spent
        return {
            "average_task_duration": 45,  # minutes
            "short_tasks": 15,           # < 30 min
            "medium_tasks": 60,          # 30-90 min
            "long_tasks": 120,           # > 90 min
            "estimation_accuracy": 0.7
        }
    
    def auto_create_tasks(self) -> List[AutoTask]:
        if not self.auto_create_tasks_enabled:
            return []
        
        patterns = self.analyze_patterns()
        auto_tasks = []
        
        # Create tasks based on identified patterns
        if "meeting_preparation" in patterns.get("task_types", {}).get("patterns", []):
            auto_tasks.append(AutoTask(
                title="Prepare for upcoming meetings",
                description="Review agenda and prepare materials for scheduled meetings",
                priority="medium",
                estimated_duration=30,
                optimal_time="morning",
                context="Detected meeting pattern",
                confidence=0.8
            ))
        
        if "email_management" in patterns.get("task_types", {}).get("patterns", []):
            auto_tasks.append(AutoTask(
                title="Process inbox",
                description="Review and respond to emails",
                priority="medium",
                estimated_duration=20,
                optimal_time="morning",
                context="Detected email management pattern",
                confidence=0.7
            ))
        
        # Weekly review task
        last_review = self._get_last_review_date()
        if not last_review or (datetime.date.today() - last_review).days >= 7:
            auto_tasks.append(AutoTask(
                title="Weekly productivity review",
                description="Review completed tasks, analyze progress, and plan next week",
                priority="high",
                estimated_duration=45,
                optimal_time="friday_afternoon",
                context="Weekly review cycle",
                confidence=0.9
            ))
        
        # Daily planning task
        if not self._has_daily_planning_task():
            auto_tasks.append(AutoTask(
                title="Daily planning session",
                description="Review priorities and plan today's tasks",
                priority="high",
                estimated_duration=15,
                optimal_time="early_morning",
                context="Daily planning routine",
                confidence=0.85
            ))
        
        return auto_tasks
    
    def auto_schedule_work_sessions(self) -> List[WorkSession]:
        if not self.auto_schedule_sessions_enabled:
            return []
        
        patterns = self.analyze_patterns()
        peak_hours = patterns.get("peak_hours", {}).get("hours", [9, 10, 11, 14, 15])
        
        sessions = []
        
        # Morning focus session
        if 9 in peak_hours or 10 in peak_hours:
            sessions.append(WorkSession(
                start_time=datetime.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0),
                duration=90,  # 1.5 hours
                task_ids=[],  # Would be populated with high-priority tasks
                session_type="deep_focus",
                break_intervals=[45]  # 45-minute break
            ))
        
        # Afternoon productive session
        if 14 in peak_hours or 15 in peak_hours:
            sessions.append(WorkSession(
                start_time=datetime.datetime.now().replace(hour=14, minute=0, second=0, microsecond=0),
                duration=60,
                task_ids=[],
                session_type="productive_work",
                break_intervals=[30]
            ))
        
        return sessions
    
    def auto_adjust_priorities(self) -> List[Dict]:
        if not self.auto_adjust_priorities_enabled:
            return []
        
        tasks = self.storage.get_tasks()
        adjustments = []
        
        for task in tasks:
            if task.get('done'):
                continue
            
            current_priority = task.get('priority', 'medium')
            suggested_priority = self._calculate_optimal_priority(task)
            
            if current_priority != suggested_priority:
                adjustments.append({
                    'task_id': task.get('id'),
                    'title': task.get('title'),
                    'current_priority': current_priority,
                    'suggested_priority': suggested_priority,
                    'reason': self._get_priority_adjustment_reason(task, suggested_priority)
                })
        
        return adjustments
    
    def _calculate_optimal_priority(self, task: Dict) -> str:
        # Check due date urgency
        if task.get('due_date'):
            try:
                due_date = datetime.datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                days_until_due = (due_date - datetime.datetime.now()).days
                
                if days_until_due <= 1:
                    return "high"
                elif days_until_due <= 3:
                    return "medium"
                else:
                    return "low"
            except:
                pass
        
        # Default based on current priority
        return task.get('priority', 'medium')
    
    def _get_priority_adjustment_reason(self, task: Dict, new_priority: str) -> str:
        if task.get('due_date'):
            try:
                due_date = datetime.datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                days_until_due = (due_date - datetime.datetime.now()).days
                
                if days_until_due <= 1:
                    return "Due within 24 hours"
                elif days_until_due <= 3:
                    return "Due within 3 days"
            except:
                pass
        
        return "Pattern-based adjustment"
    
    def auto_suggest_breaks(self) -> List[Dict]:
        if not self.auto_suggest_breaks_enabled:
            return []
        
        # Mock break suggestions - would be based on actual work tracking
        suggestions = []
        
        current_hour = datetime.datetime.now().hour
        
        # Suggest lunch break
        if 12 <= current_hour <= 13:
            suggestions.append({
                "type": "lunch_break",
                "title": "🍽️ Lunch Break Time",
                "description": "Take a proper lunch break to recharge",
                "duration": 45,
                "optimal": True
            })
        
        # Suggest afternoon break
        if 15 <= current_hour <= 16:
            suggestions.append({
                "type": "energy_break",
                "title": "⚡ Energy Boost Break",
                "description": "Take a short break to combat afternoon energy dip",
                "duration": 15,
                "optimal": True
            })
        
        return suggestions
    
    def get_autopilot_dashboard(self) -> Dict[str, Any]:
        patterns = self.analyze_patterns()
        auto_tasks = self.auto_create_tasks()
        sessions = self.auto_schedule_work_sessions()
        priority_adjustments = self.auto_adjust_priorities()
        break_suggestions = self.auto_suggest_breaks()
        
        return {
            "mode": self.mode.value,
            "patterns": patterns,
            "auto_tasks": auto_tasks,
            "scheduled_sessions": sessions,
            "priority_adjustments": priority_adjustments,
            "break_suggestions": break_suggestions,
            "settings": {
                "auto_create_tasks": self.auto_create_tasks_enabled,
                "auto_schedule_sessions": self.auto_schedule_sessions_enabled,
                "auto_adjust_priorities": self.auto_adjust_priorities_enabled,
                "auto_suggest_breaks": self.auto_suggest_breaks_enabled,
                "auto_track_time": self.auto_track_time_enabled
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _get_last_review_date(self) -> Optional[datetime.date]:
        # Would check for review tasks in storage
        return None
    
    def _has_daily_planning_task(self) -> bool:
        # Would check for planning tasks in storage
        return False


# Export for CLI integration
__all__ = ['ProductivityAutopilot', 'AutoTask', 'WorkSession', 'AutopilotMode']
