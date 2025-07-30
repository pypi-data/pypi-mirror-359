#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/integrations/smart_suggestions.py

import datetime
import statistics
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass

from logbuch.core.logger import get_logger
from logbuch.core.config import get_config


@dataclass
class Suggestion:
    type: str
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    priority: str = "medium"  # low, medium, high


class SmartSuggestionEngine:
    def __init__(self):
        self.logger = get_logger("smart_suggestions")
        self.config = get_config()
    
    def analyze_and_suggest(self, storage) -> List[Suggestion]:
        suggestions = []
        
        # Get all data for analysis
        tasks = storage.get_tasks()
        journal_entries = storage.get_journal_entries(limit=1000)
        mood_entries = storage.get_mood_entries(limit=1000)
        sleep_entries = storage.get_sleep_entries(limit=1000)
        goals = storage.get_goals()
        
        # Generate different types of suggestions
        suggestions.extend(self._suggest_task_optimization(tasks))
        suggestions.extend(self._suggest_productivity_patterns(tasks, journal_entries))
        suggestions.extend(self._suggest_mood_improvements(mood_entries, tasks))
        suggestions.extend(self._suggest_goal_adjustments(goals, tasks))
        suggestions.extend(self._suggest_time_management(tasks))
        suggestions.extend(self._suggest_habit_formation(tasks, mood_entries))
        suggestions.extend(self._suggest_workload_balance(tasks))
        suggestions.extend(self._suggest_content_ideas(journal_entries))
        
        # Sort by confidence and priority
        suggestions.sort(key=lambda s: (s.priority == 'high', s.confidence), reverse=True)
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def _suggest_task_optimization(self, tasks: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        if not tasks:
            return suggestions
        
        # Analyze task patterns
        incomplete_tasks = [t for t in tasks if not t.get('done')]
        completed_tasks = [t for t in tasks if t.get('done')]
        overdue_tasks = self._get_overdue_tasks(incomplete_tasks)
        
        # Too many incomplete tasks
        if len(incomplete_tasks) > 20:
            suggestions.append(Suggestion(
                type="task_management",
                title="Reduce Task Overload",
                description=f"You have {len(incomplete_tasks)} incomplete tasks. Consider breaking large tasks into smaller ones or archiving old tasks.",
                confidence=0.9,
                priority="high",
                action="bulk_cleanup"
            ))
        
        # Many overdue tasks
        if len(overdue_tasks) > 5:
            suggestions.append(Suggestion(
                type="deadline_management",
                title="Address Overdue Tasks",
                description=f"You have {len(overdue_tasks)} overdue tasks. Consider rescheduling or breaking them down.",
                confidence=0.95,
                priority="high",
                action="reschedule_overdue"
            ))
        
        # No priorities set
        no_priority_tasks = [t for t in incomplete_tasks if not t.get('priority') or t.get('priority') == 'medium']
        if len(no_priority_tasks) > 10:
            suggestions.append(Suggestion(
                type="prioritization",
                title="Set Task Priorities",
                description=f"{len(no_priority_tasks)} tasks lack clear priorities. Setting priorities helps focus on what matters most.",
                confidence=0.8,
                priority="medium",
                action="set_priorities"
            ))
        
        # Low completion rate
        if completed_tasks and len(completed_tasks) / len(tasks) < 0.3:
            suggestions.append(Suggestion(
                type="completion_rate",
                title="Improve Task Completion",
                description="Your task completion rate is low. Consider setting smaller, more achievable goals.",
                confidence=0.7,
                priority="medium",
                action="break_down_tasks"
            ))
        
        return suggestions
    
    def _suggest_productivity_patterns(self, tasks: List[Dict], journal_entries: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        # Analyze completion patterns
        completion_patterns = self._analyze_completion_patterns(tasks)
        
        if completion_patterns['best_day']:
            suggestions.append(Suggestion(
                type="productivity_pattern",
                title=f"Optimize {completion_patterns['best_day']} Productivity",
                description=f"You're most productive on {completion_patterns['best_day']}s. Consider scheduling important tasks on this day.",
                confidence=0.8,
                priority="medium",
                data=completion_patterns
            ))
        
        # Analyze journal sentiment for productivity correlation
        if journal_entries:
            productivity_correlation = self._analyze_productivity_sentiment(journal_entries, tasks)
            if productivity_correlation['correlation'] > 0.6:
                suggestions.append(Suggestion(
                    type="mood_productivity",
                    title="Mood-Productivity Connection",
                    description="Your journal entries show a strong correlation between positive mood and productivity. Consider mood tracking for better planning.",
                    confidence=productivity_correlation['correlation'],
                    priority="medium"
                ))
        
        return suggestions
    
    def _suggest_mood_improvements(self, mood_entries: List[Dict], tasks: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        if not mood_entries:
            suggestions.append(Suggestion(
                type="mood_tracking",
                title="Start Mood Tracking",
                description="Tracking your mood can help identify patterns and improve overall wellbeing.",
                confidence=0.7,
                priority="low",
                action="start_mood_tracking"
            ))
            return suggestions
        
        # Analyze mood trends
        recent_moods = mood_entries[:30]  # Last 30 entries
        mood_analysis = self._analyze_mood_patterns(recent_moods)
        
        if mood_analysis['negative_trend']:
            suggestions.append(Suggestion(
                type="wellbeing",
                title="Address Mood Decline",
                description="Your recent mood entries show a declining trend. Consider self-care activities or speaking with someone.",
                confidence=0.8,
                priority="high",
                action="wellbeing_check"
            ))
        
        if mood_analysis['low_variety']:
            suggestions.append(Suggestion(
                type="mood_variety",
                title="Expand Mood Vocabulary",
                description="You tend to use similar mood words. Exploring a wider range of emotions can improve self-awareness.",
                confidence=0.6,
                priority="low",
                action="mood_suggestions"
            ))
        
        return suggestions
    
    def _suggest_goal_adjustments(self, goals: List[Dict], tasks: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        if not goals:
            suggestions.append(Suggestion(
                type="goal_setting",
                title="Set Personal Goals",
                description="Setting clear goals can improve focus and motivation. Consider adding 2-3 meaningful goals.",
                confidence=0.8,
                priority="medium",
                action="create_goals"
            ))
            return suggestions
        
        # Analyze goal progress
        stagnant_goals = [g for g in goals if not g.get('completed') and g.get('progress', 0) < 10]
        if len(stagnant_goals) > 2:
            suggestions.append(Suggestion(
                type="goal_progress",
                title="Revive Stagnant Goals",
                description=f"{len(stagnant_goals)} goals have made little progress. Consider breaking them into smaller milestones.",
                confidence=0.9,
                priority="high",
                action="break_down_goals"
            ))
        
        # Goals without related tasks
        goal_task_alignment = self._analyze_goal_task_alignment(goals, tasks)
        if goal_task_alignment['unaligned_goals']:
            suggestions.append(Suggestion(
                type="goal_alignment",
                title="Align Tasks with Goals",
                description="Some goals lack supporting tasks. Create specific action items for better progress.",
                confidence=0.8,
                priority="medium",
                action="create_goal_tasks",
                data=goal_task_alignment
            ))
        
        return suggestions
    
    def _suggest_time_management(self, tasks: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        # Analyze due date patterns
        tasks_with_dates = [t for t in tasks if t.get('due_date')]
        if len(tasks_with_dates) / len(tasks) < 0.3 if tasks else 0:
            suggestions.append(Suggestion(
                type="time_management",
                title="Add Due Dates to Tasks",
                description="Most of your tasks lack due dates. Adding deadlines can improve time management and urgency.",
                confidence=0.7,
                priority="medium",
                action="add_due_dates"
            ))
        
        # Analyze task creation patterns
        creation_patterns = self._analyze_task_creation_patterns(tasks)
        if creation_patterns['batch_creation']:
            suggestions.append(Suggestion(
                type="task_planning",
                title="Spread Out Task Creation",
                description="You tend to create many tasks at once. Consider daily or weekly planning sessions instead.",
                confidence=0.6,
                priority="low",
                data=creation_patterns
            ))
        
        return suggestions
    
    def _suggest_habit_formation(self, tasks: List[Dict], mood_entries: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        # Analyze recurring task patterns
        recurring_patterns = self._analyze_recurring_tasks(tasks)
        
        if recurring_patterns['potential_habits']:
            suggestions.append(Suggestion(
                type="habit_formation",
                title="Convert Tasks to Habits",
                description=f"You have {len(recurring_patterns['potential_habits'])} recurring tasks that could become habits.",
                confidence=0.7,
                priority="medium",
                action="create_habits",
                data=recurring_patterns
            ))
        
        # Suggest consistency improvements
        if mood_entries:
            consistency_analysis = self._analyze_consistency(mood_entries)
            if consistency_analysis['inconsistent']:
                suggestions.append(Suggestion(
                    type="consistency",
                    title="Improve Tracking Consistency",
                    description="Your mood tracking is inconsistent. Regular tracking provides better insights.",
                    confidence=0.6,
                    priority="low",
                    action="set_reminders"
                ))
        
        return suggestions
    
    def _suggest_workload_balance(self, tasks: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        # Analyze task distribution by priority
        priority_distribution = Counter(t.get('priority', 'medium') for t in tasks if not t.get('done'))
        
        if priority_distribution.get('high', 0) > priority_distribution.get('medium', 0) + priority_distribution.get('low', 0):
            suggestions.append(Suggestion(
                type="workload_balance",
                title="Balance Task Priorities",
                description="You have many high-priority tasks. Consider if all are truly urgent or if some can be rescheduled.",
                confidence=0.8,
                priority="medium",
                action="rebalance_priorities"
            ))
        
        # Analyze task complexity (based on content length as proxy)
        complex_tasks = [t for t in tasks if len(t.get('content', '')) > 100]
        if len(complex_tasks) > 5:
            suggestions.append(Suggestion(
                type="task_complexity",
                title="Break Down Complex Tasks",
                description=f"You have {len(complex_tasks)} complex tasks. Breaking them down can make them more manageable.",
                confidence=0.7,
                priority="medium",
                action="simplify_tasks"
            ))
        
        return suggestions
    
    def _suggest_content_ideas(self, journal_entries: List[Dict]) -> List[Suggestion]:
        suggestions = []
        
        if not journal_entries:
            return suggestions
        
        # Analyze journal themes
        themes = self._analyze_journal_themes(journal_entries)
        
        if themes['repetitive_content']:
            suggestions.append(Suggestion(
                type="journal_variety",
                title="Diversify Journal Topics",
                description="Your journal entries cover similar themes. Try exploring different aspects of your life.",
                confidence=0.6,
                priority="low",
                action="journal_prompts",
                data={"suggested_topics": ["gratitude", "challenges", "learning", "relationships", "goals"]}
            ))
        
        if len(journal_entries) < 10:
            suggestions.append(Suggestion(
                type="journal_frequency",
                title="Increase Journal Frequency",
                description="Regular journaling can improve self-reflection and mental clarity. Consider daily or weekly entries.",
                confidence=0.7,
                priority="low",
                action="set_journal_reminders"
            ))
        
        return suggestions
    
    # Helper methods for analysis
    
    def _get_overdue_tasks(self, tasks: List[Dict]) -> List[Dict]:
        today = datetime.date.today()
        overdue = []
        
        for task in tasks:
            if task.get('due_date'):
                try:
                    due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                    if due_date < today:
                        overdue.append(task)
                except:
                    continue
        
        return overdue
    
    def _analyze_completion_patterns(self, tasks: List[Dict]) -> Dict[str, Any]:
        completed_tasks = [t for t in tasks if t.get('done') and t.get('completed_at')]
        
        if not completed_tasks:
            return {'best_day': None, 'completion_rate': 0}
        
        # Analyze by day of week
        day_counts = defaultdict(int)
        for task in completed_tasks:
            try:
                completed_date = datetime.datetime.fromisoformat(task['completed_at'].split('T')[0])
                day_name = completed_date.strftime('%A')
                day_counts[day_name] += 1
            except:
                continue
        
        best_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else None
        
        return {
            'best_day': best_day,
            'completion_rate': len(completed_tasks) / len(tasks) if tasks else 0,
            'day_distribution': dict(day_counts)
        }
    
    def _analyze_productivity_sentiment(self, journal_entries: List[Dict], tasks: List[Dict]) -> Dict[str, Any]:
        # Simple sentiment analysis based on positive/negative words
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'productive', 'accomplished'}
        negative_words = {'bad', 'terrible', 'awful', 'frustrated', 'stressed', 'overwhelmed', 'tired'}
        
        sentiment_scores = []
        for entry in journal_entries[:30]:  # Last 30 entries
            text = entry.get('text', '').lower()
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count + negative_count > 0:
                sentiment = (positive_count - negative_count) / (positive_count + negative_count)
                sentiment_scores.append(sentiment)
        
        # Simple correlation calculation (would use proper correlation in production)
        correlation = statistics.mean(sentiment_scores) if sentiment_scores else 0
        
        return {
            'correlation': abs(correlation),
            'average_sentiment': correlation
        }
    
    def _analyze_mood_patterns(self, mood_entries: List[Dict]) -> Dict[str, Any]:
        if not mood_entries:
            return {'negative_trend': False, 'low_variety': False}
        
        # Simple trend analysis
        moods = [entry.get('mood', '').lower() for entry in mood_entries]
        negative_moods = {'sad', 'angry', 'frustrated', 'depressed', 'anxious', 'stressed', 'overwhelmed'}
        
        recent_negative = sum(1 for mood in moods[:10] if mood in negative_moods)
        negative_trend = recent_negative > 5
        
        # Variety analysis
        unique_moods = len(set(moods))
        low_variety = unique_moods < len(moods) * 0.3
        
        return {
            'negative_trend': negative_trend,
            'low_variety': low_variety,
            'unique_moods': unique_moods,
            'total_entries': len(mood_entries)
        }
    
    def _analyze_goal_task_alignment(self, goals: List[Dict], tasks: List[Dict]) -> Dict[str, Any]:
        unaligned_goals = []
        
        for goal in goals:
            goal_keywords = goal.get('description', '').lower().split()
            
            # Check if any tasks relate to this goal
            related_tasks = []
            for task in tasks:
                task_content = task.get('content', '').lower()
                if any(keyword in task_content for keyword in goal_keywords if len(keyword) > 3):
                    related_tasks.append(task)
            
            if not related_tasks:
                unaligned_goals.append(goal)
        
        return {
            'unaligned_goals': unaligned_goals,
            'alignment_rate': (len(goals) - len(unaligned_goals)) / len(goals) if goals else 0
        }
    
    def _analyze_task_creation_patterns(self, tasks: List[Dict]) -> Dict[str, Any]:
        if not tasks:
            return {'batch_creation': False}
        
        # Group tasks by creation date
        creation_dates = defaultdict(int)
        for task in tasks:
            if task.get('created_at'):
                try:
                    date = datetime.datetime.fromisoformat(task['created_at'].split('T')[0]).date()
                    creation_dates[date] += 1
                except:
                    continue
        
        # Check for batch creation (more than 5 tasks in one day)
        batch_creation = any(count > 5 for count in creation_dates.values())
        
        return {
            'batch_creation': batch_creation,
            'creation_distribution': dict(creation_dates)
        }
    
    def _analyze_recurring_tasks(self, tasks: List[Dict]) -> Dict[str, Any]:
        # Simple analysis based on similar task content
        task_contents = [t.get('content', '').lower() for t in tasks]
        content_counts = Counter(task_contents)
        
        potential_habits = [content for content, count in content_counts.items() if count > 2]
        
        return {
            'potential_habits': potential_habits,
            'recurring_count': len(potential_habits)
        }
    
    def _analyze_consistency(self, entries: List[Dict]) -> Dict[str, Any]:
        if not entries:
            return {'inconsistent': True}
        
        # Analyze date gaps
        dates = []
        for entry in entries:
            try:
                date = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00')).date()
                dates.append(date)
            except:
                continue
        
        if len(dates) < 2:
            return {'inconsistent': True}
        
        dates.sort()
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = statistics.mean(gaps) if gaps else 0
        
        # Consider inconsistent if average gap is more than 3 days
        inconsistent = avg_gap > 3
        
        return {
            'inconsistent': inconsistent,
            'average_gap_days': avg_gap,
            'max_gap_days': max(gaps) if gaps else 0
        }
    
    def _analyze_journal_themes(self, journal_entries: List[Dict]) -> Dict[str, Any]:
        if not journal_entries:
            return {'repetitive_content': False}
        
        # Simple theme analysis based on common words
        all_text = ' '.join(entry.get('text', '') for entry in journal_entries).lower()
        words = all_text.split()
        
        # Filter out common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'are', 'were', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        meaningful_words = [word for word in words if len(word) > 3 and word not in common_words]
        
        word_counts = Counter(meaningful_words)
        top_words = word_counts.most_common(10)
        
        # Check for repetitive content (if top words appear very frequently)
        repetitive_content = any(count > len(journal_entries) * 0.5 for word, count in top_words)
        
        return {
            'repetitive_content': repetitive_content,
            'top_themes': [word for word, count in top_words],
            'theme_diversity': len(set(meaningful_words)) / len(meaningful_words) if meaningful_words else 0
        }
