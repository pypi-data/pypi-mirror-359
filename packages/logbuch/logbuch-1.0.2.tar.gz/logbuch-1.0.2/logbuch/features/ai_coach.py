#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/ai_coach.py

import datetime
import json
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random

from logbuch.core.logger import get_logger


class CoachingType(Enum):
    PRODUCTIVITY_OPTIMIZATION = "productivity_optimization"
    HABIT_FORMATION = "habit_formation"
    STRESS_MANAGEMENT = "stress_management"
    GOAL_ACHIEVEMENT = "goal_achievement"
    TIME_MANAGEMENT = "time_management"
    ENERGY_OPTIMIZATION = "energy_optimization"
    FOCUS_ENHANCEMENT = "focus_enhancement"


@dataclass
class CoachingInsight:
    id: str
    type: CoachingType
    title: str
    insight: str
    action_items: List[str]
    confidence: float
    impact_score: float
    urgency: str  # low, medium, high, critical
    data_points: List[str]
    created_at: datetime.datetime
    implemented: bool = False
    effectiveness_rating: Optional[int] = None


@dataclass
class ProductivityPattern:
    pattern_type: str
    description: str
    frequency: float
    impact: str
    recommendation: str
    confidence: float


@dataclass
class PredictiveAlert:
    alert_type: str
    prediction: str
    probability: float
    suggested_actions: List[str]
    timeline: str


class AIProductivityCoach:
    def __init__(self, storage):
        self.storage = storage
        self.logger = get_logger("ai_coach")
        
        # Load coaching history
        self.insights_history = self._load_insights_history()
        self.patterns = []
        self.predictions = []
        
        self.logger.debug("AI Productivity Coach initialized")
    
    def _load_insights_history(self) -> List[CoachingInsight]:
        try:
            from pathlib import Path
            insights_file = Path.home() / ".logbuch" / "coaching_insights.json"
            
            if insights_file.exists():
                with open(insights_file, 'r') as f:
                    data = json.load(f)
                    insights = []
                    for item in data:
                        item['created_at'] = datetime.datetime.fromisoformat(item['created_at'])
                        item['type'] = CoachingType(item['type'])
                        insights.append(CoachingInsight(**item))
                    return insights
        except Exception as e:
            self.logger.debug(f"Could not load insights history: {e}")
        
        return []
    
    def _save_insights_history(self):
        try:
            from pathlib import Path
            insights_file = Path.home() / ".logbuch" / "coaching_insights.json"
            insights_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = []
            for insight in self.insights_history:
                insight_dict = asdict(insight)
                insight_dict['created_at'] = insight.created_at.isoformat()
                insight_dict['type'] = insight.type.value
                data.append(insight_dict)
            
            with open(insights_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save insights: {e}")
    
    def analyze_productivity_patterns(self) -> List[ProductivityPattern]:
        patterns = []
        
        # Get recent data
        tasks = self.storage.get_tasks(show_completed=True)
        journal_entries = self.storage.get_journal_entries(limit=100)
        mood_entries = self.storage.get_mood_entries(limit=100)
        
        # Pattern 1: Peak productivity hours
        peak_hours = self._analyze_peak_hours(tasks)
        if peak_hours:
            patterns.append(ProductivityPattern(
                pattern_type="peak_hours",
                description=f"You're most productive between {peak_hours['start']}:00-{peak_hours['end']}:00",
                frequency=peak_hours['confidence'],
                impact="High",
                recommendation=f"Schedule your most important tasks during {peak_hours['start']}:00-{peak_hours['end']}:00",
                confidence=peak_hours['confidence']
            ))
        
        # Pattern 2: Task completion streaks
        streak_pattern = self._analyze_completion_streaks(tasks)
        if streak_pattern:
            patterns.append(streak_pattern)
        
        # Pattern 3: Mood-productivity correlation
        mood_correlation = self._analyze_mood_productivity(tasks, mood_entries)
        if mood_correlation:
            patterns.append(mood_correlation)
        
        # Pattern 4: Procrastination triggers
        procrastination = self._analyze_procrastination_patterns(tasks)
        if procrastination:
            patterns.append(procrastination)
        
        # Pattern 5: Energy cycles
        energy_pattern = self._analyze_energy_cycles(journal_entries, mood_entries)
        if energy_pattern:
            patterns.append(energy_pattern)
        
        self.patterns = patterns
        return patterns
    
    def _analyze_peak_hours(self, tasks: List[Dict]) -> Optional[Dict]:
        completed_tasks = [t for t in tasks if t.get('done') and t.get('completed_at')]
        
        if len(completed_tasks) < 10:
            return None
        
        # Extract completion hours
        hours = []
        for task in completed_tasks:
            try:
                completed_at = datetime.datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                hours.append(completed_at.hour)
            except:
                continue
        
        if not hours:
            return None
        
        # Find peak hours using histogram
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Find consecutive peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hour = sorted_hours[0][0]
        
        # Find range around peak
        start_hour = max(0, peak_hour - 1)
        end_hour = min(23, peak_hour + 2)
        
        # Calculate confidence based on data concentration
        peak_tasks = sum(hour_counts.get(h, 0) for h in range(start_hour, end_hour + 1))
        confidence = min(0.95, peak_tasks / len(completed_tasks))
        
        if confidence > 0.3:
            return {
                'start': start_hour,
                'end': end_hour,
                'confidence': confidence
            }
        
        return None
    
    def _analyze_completion_streaks(self, tasks: List[Dict]) -> Optional[ProductivityPattern]:
        completed_tasks = [t for t in tasks if t.get('done') and t.get('completed_at')]
        
        if len(completed_tasks) < 20:
            return None
        
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
        avg_daily = statistics.mean(completion_counts)
        
        # Find best days
        high_productivity_days = [count for count in completion_counts if count > avg_daily * 1.5]
        
        if len(high_productivity_days) > len(completion_counts) * 0.2:
            return ProductivityPattern(
                pattern_type="completion_streaks",
                description=f"You have {len(high_productivity_days)} high-productivity days with {statistics.mean(high_productivity_days):.1f} tasks/day",
                frequency=len(high_productivity_days) / len(completion_counts),
                impact="High",
                recommendation="Identify what makes your high-productivity days special and replicate those conditions",
                confidence=0.8
            )
        
        return None
    
    def _analyze_mood_productivity(self, tasks: List[Dict], moods: List[Dict]) -> Optional[ProductivityPattern]:
        if len(moods) < 10:
            return None
        
        # Map moods to productivity scores
        mood_productivity = {}
        
        for mood_entry in moods:
            try:
                mood_date = datetime.datetime.fromisoformat(mood_entry['date'].replace('Z', '+00:00')).date()
                mood_value = mood_entry['mood']
                
                # Count tasks completed on same day
                daily_tasks = len([t for t in tasks 
                                 if t.get('done') and t.get('completed_at') and
                                 datetime.datetime.fromisoformat(t['completed_at'].replace('Z', '+00:00')).date() == mood_date])
                
                if mood_value not in mood_productivity:
                    mood_productivity[mood_value] = []
                mood_productivity[mood_value].append(daily_tasks)
            except:
                continue
        
        if len(mood_productivity) < 3:
            return None
        
        # Calculate average productivity for each mood
        mood_averages = {}
        for mood, task_counts in mood_productivity.items():
            mood_averages[mood] = statistics.mean(task_counts)
        
        # Find correlation
        best_mood = max(mood_averages.items(), key=lambda x: x[1])
        worst_mood = min(mood_averages.items(), key=lambda x: x[1])
        
        if best_mood[1] > worst_mood[1] * 1.5:
            return ProductivityPattern(
                pattern_type="mood_correlation",
                description=f"You're {best_mood[1]/worst_mood[1]:.1f}x more productive when feeling '{best_mood[0]}'",
                frequency=0.7,
                impact="High",
                recommendation=f"Focus on activities that help you feel '{best_mood[0]}' to boost productivity",
                confidence=0.75
            )
        
        return None
    
    def _analyze_procrastination_patterns(self, tasks: List[Dict]) -> Optional[ProductivityPattern]:
        overdue_tasks = []
        
        for task in tasks:
            if task.get('due_date') and not task.get('done'):
                try:
                    due_date = datetime.datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                    if due_date < datetime.datetime.now():
                        overdue_tasks.append(task)
                except:
                    continue
        
        if len(overdue_tasks) > 5:
            # Analyze common patterns in overdue tasks
            priorities = [t.get('priority', 'medium') for t in overdue_tasks]
            boards = [t.get('board', 'default') for t in overdue_tasks]
            
            # Find most common procrastination trigger
            priority_counts = {p: priorities.count(p) for p in set(priorities)}
            board_counts = {b: boards.count(b) for b in set(boards)}
            
            main_trigger = max(priority_counts.items(), key=lambda x: x[1])
            
            return ProductivityPattern(
                pattern_type="procrastination",
                description=f"You tend to procrastinate on '{main_trigger[0]}' priority tasks ({main_trigger[1]} overdue)",
                frequency=main_trigger[1] / len(overdue_tasks),
                impact="Medium",
                recommendation=f"Break down {main_trigger[0]} priority tasks into smaller, manageable chunks",
                confidence=0.6
            )
        
        return None
    
    def _analyze_energy_cycles(self, journals: List[Dict], moods: List[Dict]) -> Optional[ProductivityPattern]:
        if len(journals) < 10 and len(moods) < 10:
            return None
        
        # Simple energy analysis based on mood trends
        recent_moods = moods[-14:] if len(moods) >= 14 else moods
        
        if len(recent_moods) < 7:
            return None
        
        # Map moods to energy levels (simplified)
        energy_map = {
            'excited': 5, 'happy': 4, 'content': 3, 'okay': 2,
            'sad': 1, 'angry': 2, 'anxious': 1, 'tired': 1,
            'energetic': 5, 'motivated': 4, 'calm': 3
        }
        
        energy_levels = []
        for mood in recent_moods:
            energy = energy_map.get(mood.get('mood', '').lower(), 3)
            energy_levels.append(energy)
        
        if len(energy_levels) < 5:
            return None
        
        avg_energy = statistics.mean(energy_levels)
        
        if avg_energy < 2.5:
            return ProductivityPattern(
                pattern_type="energy_cycles",
                description=f"Your recent energy levels are below average ({avg_energy:.1f}/5)",
                frequency=0.8,
                impact="High",
                recommendation="Consider adding energy-boosting activities: exercise, better sleep, or breaks",
                confidence=0.7
            )
        
        return None
    
    def generate_coaching_insights(self) -> List[CoachingInsight]:
        insights = []
        
        # Analyze patterns first
        patterns = self.analyze_productivity_patterns()
        
        # Generate insights based on patterns
        for pattern in patterns:
            insight = self._pattern_to_insight(pattern)
            if insight:
                insights.append(insight)
        
        # Generate strategic insights
        strategic_insights = self._generate_strategic_insights()
        insights.extend(strategic_insights)
        
        # Generate predictive insights
        predictive_insights = self._generate_predictive_insights()
        insights.extend(predictive_insights)
        
        # Sort by impact and urgency
        insights.sort(key=lambda x: (x.impact_score, x.confidence), reverse=True)
        
        # Save insights
        self.insights_history.extend(insights)
        self._save_insights_history()
        
        return insights[:5]  # Return top 5 insights
    
    def _pattern_to_insight(self, pattern: ProductivityPattern) -> Optional[CoachingInsight]:
        insight_id = f"pattern_{pattern.pattern_type}_{datetime.datetime.now().strftime('%Y%m%d')}"
        
        if pattern.pattern_type == "peak_hours":
            return CoachingInsight(
                id=insight_id,
                type=CoachingType.TIME_MANAGEMENT,
                title="🕐 Optimize Your Peak Hours",
                insight=pattern.description,
                action_items=[
                    pattern.recommendation,
                    "Block calendar during peak hours for important work",
                    "Avoid meetings during your most productive time",
                    "Use peak hours for your most challenging tasks"
                ],
                confidence=pattern.confidence,
                impact_score=8.5,
                urgency="high",
                data_points=[f"Analysis based on {pattern.frequency*100:.0f}% of your task completions"],
                created_at=datetime.datetime.now()
            )
        
        elif pattern.pattern_type == "mood_correlation":
            return CoachingInsight(
                id=insight_id,
                type=CoachingType.ENERGY_OPTIMIZATION,
                title="😊 Mood-Productivity Connection",
                insight=pattern.description,
                action_items=[
                    pattern.recommendation,
                    "Track what activities improve your mood",
                    "Schedule mood-boosting activities before important work",
                    "Create a 'good mood' routine for productive days"
                ],
                confidence=pattern.confidence,
                impact_score=7.5,
                urgency="medium",
                data_points=["Based on correlation analysis of mood and task completion data"],
                created_at=datetime.datetime.now()
            )
        
        elif pattern.pattern_type == "procrastination":
            return CoachingInsight(
                id=insight_id,
                type=CoachingType.PRODUCTIVITY_OPTIMIZATION,
                title="⚠️ Procrastination Pattern Detected",
                insight=pattern.description,
                action_items=[
                    pattern.recommendation,
                    "Use the 2-minute rule for quick wins",
                    "Set artificial deadlines before real ones",
                    "Find an accountability partner for difficult tasks"
                ],
                confidence=pattern.confidence,
                impact_score=8.0,
                urgency="high",
                data_points=[f"Analysis of {len([t for t in self.storage.get_tasks() if not t.get('done')])} pending tasks"],
                created_at=datetime.datetime.now()
            )
        
        return None
    
    def _generate_strategic_insights(self) -> List[CoachingInsight]:
        insights = []
        
        # Goal achievement analysis
        goals = self.storage.get_goals() if hasattr(self.storage, 'get_goals') else []
        if goals:
            overdue_goals = [g for g in goals if g.get('due_date') and 
                           datetime.datetime.fromisoformat(g['due_date'].replace('Z', '+00:00')) < datetime.datetime.now()]
            
            if len(overdue_goals) > 0:
                insights.append(CoachingInsight(
                    id=f"strategic_goals_{datetime.datetime.now().strftime('%Y%m%d')}",
                    type=CoachingType.GOAL_ACHIEVEMENT,
                    title="🎯 Goal Achievement Strategy",
                    insight=f"You have {len(overdue_goals)} overdue goals that need attention",
                    action_items=[
                        "Review and update goal deadlines realistically",
                        "Break large goals into weekly milestones",
                        "Set up weekly goal review sessions",
                        "Consider if some goals are still relevant"
                    ],
                    confidence=0.9,
                    impact_score=9.0,
                    urgency="critical",
                    data_points=[f"Analysis of {len(goals)} total goals"],
                    created_at=datetime.datetime.now()
                ))
        
        # Habit formation insight
        tasks = self.storage.get_tasks(show_completed=True)
        recent_tasks = [t for t in tasks if t.get('completed_at') and 
                       datetime.datetime.fromisoformat(t['completed_at'].replace('Z', '+00:00')) > 
                       datetime.datetime.now() - datetime.timedelta(days=30)]
        
        if len(recent_tasks) > 0:
            daily_avg = len(recent_tasks) / 30
            if daily_avg < 2:
                insights.append(CoachingInsight(
                    id=f"strategic_habits_{datetime.datetime.now().strftime('%Y%m%d')}",
                    type=CoachingType.HABIT_FORMATION,
                    title="🔄 Build Consistent Habits",
                    insight=f"Your current task completion rate is {daily_avg:.1f} tasks/day",
                    action_items=[
                        "Start with just 1 small task daily to build momentum",
                        "Use habit stacking: attach new tasks to existing routines",
                        "Set up environmental cues for task completion",
                        "Celebrate small wins to reinforce the habit"
                    ],
                    confidence=0.8,
                    impact_score=8.5,
                    urgency="medium",
                    data_points=[f"Based on {len(recent_tasks)} tasks in last 30 days"],
                    created_at=datetime.datetime.now()
                ))
        
        return insights
    
    def _generate_predictive_insights(self) -> List[CoachingInsight]:
        insights = []
        
        # Predict upcoming busy periods
        tasks = self.storage.get_tasks()
        upcoming_tasks = [t for t in tasks if t.get('due_date') and not t.get('done')]
        
        if len(upcoming_tasks) > 10:
            # Group by week
            weekly_load = {}
            for task in upcoming_tasks:
                try:
                    due_date = datetime.datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                    week = due_date.isocalendar()[1]
                    weekly_load[week] = weekly_load.get(week, 0) + 1
                except:
                    continue
            
            if weekly_load:
                busiest_week = max(weekly_load.items(), key=lambda x: x[1])
                if busiest_week[1] > 5:
                    insights.append(CoachingInsight(
                        id=f"predictive_workload_{datetime.datetime.now().strftime('%Y%m%d')}",
                        type=CoachingType.STRESS_MANAGEMENT,
                        title="📈 Upcoming High Workload Detected",
                        insight=f"Week {busiest_week[0]} has {busiest_week[1]} tasks due - potential stress period",
                        action_items=[
                            "Start working on week's tasks early",
                            "Delegate or postpone non-essential tasks",
                            "Block extra time for high-priority items",
                            "Plan stress management activities for that week"
                        ],
                        confidence=0.85,
                        impact_score=7.5,
                        urgency="medium",
                        data_points=[f"Analysis of {len(upcoming_tasks)} upcoming tasks"],
                        created_at=datetime.datetime.now()
                    ))
        
        return insights
    
    def get_daily_coaching_brief(self) -> Dict:
        # Get recent insights
        recent_insights = [i for i in self.insights_history 
                          if i.created_at > datetime.datetime.now() - datetime.timedelta(days=7)]
        
        # Generate new insights if needed
        if len(recent_insights) < 3:
            new_insights = self.generate_coaching_insights()
            recent_insights.extend(new_insights)
        
        # Get today's focus
        today_focus = self._get_today_focus()
        
        # Get productivity score
        productivity_score = self._calculate_productivity_score()
        
        return {
            'date': datetime.date.today().isoformat(),
            'productivity_score': productivity_score,
            'today_focus': today_focus,
            'key_insights': recent_insights[:3],
            'quick_wins': self._get_quick_wins(),
            'energy_forecast': self._get_energy_forecast()
        }
    
    def _get_today_focus(self) -> str:
        tasks = self.storage.get_tasks()
        high_priority = [t for t in tasks if t.get('priority') == 'high' and not t.get('done')]
        
        if high_priority:
            return f"Focus on {len(high_priority)} high-priority tasks today"
        
        due_today = [t for t in tasks if t.get('due_date') and not t.get('done') and
                    datetime.datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')).date() == datetime.date.today()]
        
        if due_today:
            return f"Complete {len(due_today)} tasks due today"
        
        return "Build momentum with 3 quick task completions"
    
    def _calculate_productivity_score(self) -> float:
        # Simple scoring based on recent activity
        tasks = self.storage.get_tasks(show_completed=True)
        recent_tasks = [t for t in tasks if t.get('completed_at') and 
                       datetime.datetime.fromisoformat(t['completed_at'].replace('Z', '+00:00')) > 
                       datetime.datetime.now() - datetime.timedelta(days=7)]
        
        # Base score on task completion
        base_score = min(10, len(recent_tasks))
        
        # Bonus for consistency
        if len(recent_tasks) >= 7:
            base_score += 2
        
        # Penalty for overdue tasks
        overdue = len([t for t in self.storage.get_tasks() if t.get('due_date') and not t.get('done') and
                      datetime.datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < datetime.datetime.now()])
        
        final_score = max(0, base_score - overdue * 0.5)
        return min(10, final_score)
    
    def _get_quick_wins(self) -> List[str]:
        return [
            "Complete 1 task that takes less than 5 minutes",
            "Clear 3 items from your inbox or notifications",
            "Write down 3 things you're grateful for",
            "Take a 5-minute walk to boost energy",
            "Organize your workspace for better focus"
        ]
    
    def _get_energy_forecast(self) -> str:
        # Simple prediction based on patterns
        hour = datetime.datetime.now().hour
        
        if 6 <= hour <= 10:
            return "Morning energy building - good time for planning"
        elif 10 <= hour <= 14:
            return "Peak energy window - tackle your hardest tasks"
        elif 14 <= hour <= 17:
            return "Afternoon focus - good for steady work"
        elif 17 <= hour <= 20:
            return "Evening wind-down - perfect for reflection and planning"
        else:
            return "Rest period - focus on recovery and preparation"


# Export for CLI integration
__all__ = ['AIProductivityCoach', 'CoachingInsight', 'ProductivityPattern']
