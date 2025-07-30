#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/gamification.py

import datetime
import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from logbuch.core.logger import get_logger
from logbuch.core.config import get_config


class AchievementType(Enum):
    TASK_COMPLETION = "task_completion"
    STREAK = "streak"
    PRODUCTIVITY = "productivity"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"
    SPECIAL = "special"


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    type: AchievementType
    xp_reward: int
    rarity: str  # common, rare, epic, legendary
    unlocked: bool = False
    unlocked_at: Optional[datetime.datetime] = None
    progress: int = 0
    target: int = 1


@dataclass
class PlayerStats:
    level: int = 1
    xp: int = 0
    total_xp: int = 0
    tasks_completed: int = 0
    journal_entries: int = 0
    mood_entries: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    achievements_unlocked: int = 0
    productivity_score: float = 0.0
    rank: str = "Novice"
    title: str = "Productivity Apprentice"


@dataclass
class DailyChallenge:
    id: str
    name: str
    description: str
    xp_reward: int
    target: int
    progress: int = 0
    completed: bool = False
    expires_at: datetime.datetime = None


class GamificationEngine:
    def __init__(self, storage):
        self.storage = storage
        self.logger = get_logger("gamification")
        self.config = get_config()
        
        # XP and level system
        self.xp_per_level = 100
        self.level_multiplier = 1.2
        
        # Load player data
        self.player_stats = self._load_player_stats()
        self.achievements = self._initialize_achievements()
        self.daily_challenges = self._generate_daily_challenges()
        
        self.logger.debug("Gamification Engine initialized")
    
    def _load_player_stats(self) -> PlayerStats:
        try:
            # Try to load from file
            from pathlib import Path
            stats_file = Path.home() / ".logbuch" / "player_stats.json"
            
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    return PlayerStats(**data)
        except Exception as e:
            self.logger.debug(f"Could not load player stats: {e}")
        
        # Return default stats
        return PlayerStats()
    
    def _save_player_stats(self):
        try:
            from pathlib import Path
            stats_file = Path.home() / ".logbuch" / "player_stats.json"
            stats_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(stats_file, 'w') as f:
                json.dump(asdict(self.player_stats), f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Could not save player stats: {e}")
    
    def _initialize_achievements(self) -> List[Achievement]:
        achievements = [
            # Task Completion Achievements
            Achievement("first_task", "First Steps", "Complete your first task", "🎯", 
                       AchievementType.TASK_COMPLETION, 10, "common", target=1),
            Achievement("task_warrior", "Task Warrior", "Complete 10 tasks", "⚔️", 
                       AchievementType.TASK_COMPLETION, 50, "common", target=10),
            Achievement("task_master", "Task Master", "Complete 50 tasks", "👑", 
                       AchievementType.TASK_COMPLETION, 200, "rare", target=50),
            Achievement("task_legend", "Task Legend", "Complete 100 tasks", "🏆", 
                       AchievementType.TASK_COMPLETION, 500, "epic", target=100),
            Achievement("task_god", "Task God", "Complete 500 tasks", "⚡", 
                       AchievementType.TASK_COMPLETION, 1000, "legendary", target=500),
            
            # Streak Achievements
            Achievement("streak_starter", "Streak Starter", "Maintain a 3-day streak", "🔥", 
                       AchievementType.STREAK, 25, "common", target=3),
            Achievement("streak_keeper", "Streak Keeper", "Maintain a 7-day streak", "🌟", 
                       AchievementType.STREAK, 75, "rare", target=7),
            Achievement("streak_master", "Streak Master", "Maintain a 30-day streak", "💎", 
                       AchievementType.STREAK, 300, "epic", target=30),
            Achievement("streak_legend", "Streak Legend", "Maintain a 100-day streak", "🚀", 
                       AchievementType.STREAK, 1000, "legendary", target=100),
            
            # Productivity Achievements
            Achievement("productive_day", "Productive Day", "Complete 5 tasks in one day", "☀️", 
                       AchievementType.PRODUCTIVITY, 30, "common", target=5),
            Achievement("productivity_beast", "Productivity Beast", "Complete 10 tasks in one day", "🦁", 
                       AchievementType.PRODUCTIVITY, 100, "rare", target=10),
            Achievement("unstoppable", "Unstoppable", "Complete 20 tasks in one day", "🌪️", 
                       AchievementType.PRODUCTIVITY, 250, "epic", target=20),
            
            # Consistency Achievements
            Achievement("journal_keeper", "Journal Keeper", "Write 10 journal entries", "📝", 
                       AchievementType.CONSISTENCY, 50, "common", target=10),
            Achievement("mood_tracker", "Mood Tracker", "Track mood for 7 days", "😊", 
                       AchievementType.CONSISTENCY, 40, "common", target=7),
            Achievement("self_aware", "Self Aware", "Track mood for 30 days", "🧠", 
                       AchievementType.CONSISTENCY, 150, "rare", target=30),
            
            # Milestone Achievements
            Achievement("level_up", "Level Up!", "Reach level 5", "⬆️", 
                       AchievementType.MILESTONE, 100, "rare", target=5),
            Achievement("high_achiever", "High Achiever", "Reach level 10", "🎖️", 
                       AchievementType.MILESTONE, 300, "epic", target=10),
            Achievement("productivity_master", "Productivity Master", "Reach level 25", "👑", 
                       AchievementType.MILESTONE, 1000, "legendary", target=25),
            
            # Special Achievements
            Achievement("early_bird", "Early Bird", "Complete a task before 8 AM", "🐦", 
                       AchievementType.SPECIAL, 25, "common", target=1),
            Achievement("night_owl", "Night Owl", "Complete a task after 10 PM", "🦉", 
                       AchievementType.SPECIAL, 25, "common", target=1),
            Achievement("weekend_warrior", "Weekend Warrior", "Complete 5 tasks on weekend", "🏋️", 
                       AchievementType.SPECIAL, 50, "rare", target=5),
            Achievement("perfectionist", "Perfectionist", "Complete all tasks for 3 days straight", "💯", 
                       AchievementType.SPECIAL, 200, "epic", target=3),
            Achievement("comeback_kid", "Comeback Kid", "Complete 10 overdue tasks", "🔄", 
                       AchievementType.SPECIAL, 100, "rare", target=10),
        ]
        
        # Load achievement progress
        try:
            from pathlib import Path
            achievements_file = Path.home() / ".logbuch" / "achievements.json"
            
            if achievements_file.exists():
                with open(achievements_file, 'r') as f:
                    saved_achievements = json.load(f)
                    
                    for achievement in achievements:
                        if achievement.id in saved_achievements:
                            saved_data = saved_achievements[achievement.id]
                            achievement.unlocked = saved_data.get('unlocked', False)
                            achievement.progress = saved_data.get('progress', 0)
                            if saved_data.get('unlocked_at'):
                                achievement.unlocked_at = datetime.datetime.fromisoformat(saved_data['unlocked_at'])
        except Exception as e:
            self.logger.debug(f"Could not load achievements: {e}")
        
        return achievements
    
    def _save_achievements(self):
        try:
            from pathlib import Path
            achievements_file = Path.home() / ".logbuch" / "achievements.json"
            achievements_file.parent.mkdir(parents=True, exist_ok=True)
            
            achievements_data = {}
            for achievement in self.achievements:
                achievements_data[achievement.id] = {
                    'unlocked': achievement.unlocked,
                    'progress': achievement.progress,
                    'unlocked_at': achievement.unlocked_at.isoformat() if achievement.unlocked_at else None
                }
            
            with open(achievements_file, 'w') as f:
                json.dump(achievements_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save achievements: {e}")
    
    def _generate_daily_challenges(self) -> List[DailyChallenge]:
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        expires_at = datetime.datetime.combine(tomorrow, datetime.time(0, 0))
        
        challenge_pool = [
            DailyChallenge("complete_3_tasks", "Task Tripler", "Complete 3 tasks today", 50, 3, expires_at=expires_at),
            DailyChallenge("write_journal", "Daily Reflection", "Write a journal entry", 30, 1, expires_at=expires_at),
            DailyChallenge("track_mood", "Mood Check", "Track your mood", 20, 1, expires_at=expires_at),
            DailyChallenge("complete_high_priority", "Priority Focus", "Complete 2 high priority tasks", 75, 2, expires_at=expires_at),
            DailyChallenge("no_overdue", "Clean Slate", "Have no overdue tasks", 100, 1, expires_at=expires_at),
            DailyChallenge("early_completion", "Early Bird Special", "Complete a task before 9 AM", 40, 1, expires_at=expires_at),
        ]
        
        # Select 3 random challenges for today
        return random.sample(challenge_pool, min(3, len(challenge_pool)))
    
    def award_xp(self, amount: int, reason: str = "") -> Dict[str, any]:
        old_level = self.player_stats.level
        
        self.player_stats.xp += amount
        self.player_stats.total_xp += amount
        
        # Check for level up
        level_up_info = self._check_level_up()
        
        # Update rank and title
        self._update_rank_and_title()
        
        # Save progress
        self._save_player_stats()
        
        result = {
            'xp_gained': amount,
            'total_xp': self.player_stats.total_xp,
            'current_level': self.player_stats.level,
            'level_up': level_up_info,
            'reason': reason
        }
        
        if level_up_info:
            self.logger.info(f"Player leveled up to {self.player_stats.level}!")
        
        return result
    
    def _check_level_up(self) -> Optional[Dict[str, any]]:
        old_level = self.player_stats.level
        
        # Calculate required XP for current level
        while True:
            required_xp = self._calculate_xp_for_level(self.player_stats.level + 1)
            if self.player_stats.total_xp >= required_xp:
                self.player_stats.level += 1
                self.player_stats.xp = self.player_stats.total_xp - required_xp
            else:
                break
        
        if self.player_stats.level > old_level:
            return {
                'old_level': old_level,
                'new_level': self.player_stats.level,
                'levels_gained': self.player_stats.level - old_level,
                'bonus_xp': (self.player_stats.level - old_level) * 25  # Bonus XP for leveling up
            }
        
        return None
    
    def _calculate_xp_for_level(self, level: int) -> int:
        if level <= 1:
            return 0
        
        total_xp = 0
        for i in range(2, level + 1):
            total_xp += int(self.xp_per_level * (self.level_multiplier ** (i - 2)))
        
        return total_xp
    
    def _update_rank_and_title(self):
        level = self.player_stats.level
        achievements_count = len([a for a in self.achievements if a.unlocked])
        
        # Determine rank
        if level >= 50:
            self.player_stats.rank = "Grandmaster"
        elif level >= 25:
            self.player_stats.rank = "Master"
        elif level >= 15:
            self.player_stats.rank = "Expert"
        elif level >= 10:
            self.player_stats.rank = "Advanced"
        elif level >= 5:
            self.player_stats.rank = "Intermediate"
        else:
            self.player_stats.rank = "Novice"
        
        # Determine title based on achievements
        if achievements_count >= 20:
            self.player_stats.title = "Productivity Legend"
        elif achievements_count >= 15:
            self.player_stats.title = "Achievement Hunter"
        elif achievements_count >= 10:
            self.player_stats.title = "Task Conqueror"
        elif achievements_count >= 5:
            self.player_stats.title = "Productivity Enthusiast"
        else:
            self.player_stats.title = "Productivity Apprentice"
    
    def process_task_completion(self, task: Dict) -> List[Dict]:
        rewards = []
        
        # Base XP for task completion
        base_xp = 10
        priority_multiplier = {'low': 1.0, 'medium': 1.2, 'high': 1.5}
        xp_amount = int(base_xp * priority_multiplier.get(task.get('priority', 'medium'), 1.0))
        
        # Award XP
        xp_result = self.award_xp(xp_amount, f"Completed task: {task['content'][:30]}")
        rewards.append({
            'type': 'xp',
            'data': xp_result
        })
        
        # Update stats
        self.player_stats.tasks_completed += 1
        
        # Check achievements
        achievement_rewards = self._check_task_achievements(task)
        rewards.extend(achievement_rewards)
        
        # Check daily challenges
        challenge_rewards = self._check_daily_challenges('task_completion', task)
        rewards.extend(challenge_rewards)
        
        self._save_player_stats()
        return rewards
    
    def process_journal_entry(self, entry: Dict) -> List[Dict]:
        rewards = []
        
        # XP based on entry length
        base_xp = 15
        length_bonus = min(len(entry.get('text', '')) // 100, 10)  # Bonus for longer entries
        xp_amount = base_xp + length_bonus
        
        xp_result = self.award_xp(xp_amount, "Journal entry added")
        rewards.append({
            'type': 'xp',
            'data': xp_result
        })
        
        # Update stats
        self.player_stats.journal_entries += 1
        
        # Check achievements
        achievement_rewards = self._check_journal_achievements()
        rewards.extend(achievement_rewards)
        
        # Check daily challenges
        challenge_rewards = self._check_daily_challenges('journal_entry')
        rewards.extend(challenge_rewards)
        
        self._save_player_stats()
        return rewards
    
    def process_mood_entry(self, mood: Dict) -> List[Dict]:
        rewards = []
        
        # XP for mood tracking
        xp_amount = 8
        xp_result = self.award_xp(xp_amount, f"Mood tracked: {mood['mood']}")
        rewards.append({
            'type': 'xp',
            'data': xp_result
        })
        
        # Update stats
        self.player_stats.mood_entries += 1
        
        # Check achievements
        achievement_rewards = self._check_mood_achievements()
        rewards.extend(achievement_rewards)
        
        # Check daily challenges
        challenge_rewards = self._check_daily_challenges('mood_entry')
        rewards.extend(challenge_rewards)
        
        self._save_player_stats()
        return rewards
    
    def _check_task_achievements(self, task: Dict) -> List[Dict]:
        rewards = []
        
        # Task completion count achievements
        task_achievements = [
            ("first_task", 1), ("task_warrior", 10), ("task_master", 50), 
            ("task_legend", 100), ("task_god", 500)
        ]
        
        for achievement_id, target in task_achievements:
            achievement = next((a for a in self.achievements if a.id == achievement_id), None)
            if achievement and not achievement.unlocked:
                achievement.progress = self.player_stats.tasks_completed
                if achievement.progress >= target:
                    rewards.append(self._unlock_achievement(achievement))
        
        # Special task achievements
        current_hour = datetime.datetime.now().hour
        
        # Early bird achievement
        if current_hour < 8:
            early_bird = next((a for a in self.achievements if a.id == "early_bird"), None)
            if early_bird and not early_bird.unlocked:
                rewards.append(self._unlock_achievement(early_bird))
        
        # Night owl achievement
        if current_hour >= 22:
            night_owl = next((a for a in self.achievements if a.id == "night_owl"), None)
            if night_owl and not night_owl.unlocked:
                rewards.append(self._unlock_achievement(night_owl))
        
        return rewards
    
    def _check_journal_achievements(self) -> List[Dict]:
        rewards = []
        
        journal_keeper = next((a for a in self.achievements if a.id == "journal_keeper"), None)
        if journal_keeper and not journal_keeper.unlocked:
            journal_keeper.progress = self.player_stats.journal_entries
            if journal_keeper.progress >= journal_keeper.target:
                rewards.append(self._unlock_achievement(journal_keeper))
        
        return rewards
    
    def _check_mood_achievements(self) -> List[Dict]:
        rewards = []
        
        # Count consecutive days of mood tracking
        mood_entries = self.storage.get_mood_entries(limit=30)
        consecutive_days = self._count_consecutive_mood_days(mood_entries)
        
        mood_achievements = [("mood_tracker", 7), ("self_aware", 30)]
        
        for achievement_id, target in mood_achievements:
            achievement = next((a for a in self.achievements if a.id == achievement_id), None)
            if achievement and not achievement.unlocked:
                achievement.progress = consecutive_days
                if achievement.progress >= target:
                    rewards.append(self._unlock_achievement(achievement))
        
        return rewards
    
    def _check_daily_challenges(self, action_type: str, data: Dict = None) -> List[Dict]:
        rewards = []
        
        for challenge in self.daily_challenges:
            if challenge.completed:
                continue
            
            # Update challenge progress based on action
            if challenge.id == "complete_3_tasks" and action_type == "task_completion":
                challenge.progress += 1
            elif challenge.id == "write_journal" and action_type == "journal_entry":
                challenge.progress += 1
            elif challenge.id == "track_mood" and action_type == "mood_entry":
                challenge.progress += 1
            elif challenge.id == "complete_high_priority" and action_type == "task_completion":
                if data and data.get('priority') == 'high':
                    challenge.progress += 1
            
            # Check if challenge is completed
            if challenge.progress >= challenge.target and not challenge.completed:
                challenge.completed = True
                xp_result = self.award_xp(challenge.xp_reward, f"Daily Challenge: {challenge.name}")
                rewards.append({
                    'type': 'daily_challenge',
                    'data': {
                        'challenge': challenge,
                        'xp_reward': xp_result
                    }
                })
        
        return rewards
    
    def _unlock_achievement(self, achievement: Achievement) -> Dict:
        achievement.unlocked = True
        achievement.unlocked_at = datetime.datetime.now()
        self.player_stats.achievements_unlocked += 1
        
        # Award achievement XP
        xp_result = self.award_xp(achievement.xp_reward, f"Achievement: {achievement.name}")
        
        self._save_achievements()
        
        return {
            'type': 'achievement',
            'data': {
                'achievement': achievement,
                'xp_reward': xp_result
            }
        }
    
    def _count_consecutive_mood_days(self, mood_entries: List[Dict]) -> int:
        if not mood_entries:
            return 0
        
        # Get unique dates
        dates = set()
        for entry in mood_entries:
            try:
                date = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00')).date()
                dates.add(date)
            except:
                continue
        
        if not dates:
            return 0
        
        # Count consecutive days from today backwards
        today = datetime.date.today()
        consecutive = 0
        current_date = today
        
        while current_date in dates:
            consecutive += 1
            current_date -= datetime.timedelta(days=1)
        
        return consecutive
    
    def get_player_profile(self) -> Dict:
        next_level_xp = self._calculate_xp_for_level(self.player_stats.level + 1)
        current_level_xp = self._calculate_xp_for_level(self.player_stats.level)
        xp_to_next_level = next_level_xp - self.player_stats.total_xp
        
        return {
            'stats': self.player_stats,
            'xp_to_next_level': xp_to_next_level,
            'level_progress': (self.player_stats.total_xp - current_level_xp) / (next_level_xp - current_level_xp) * 100,
            'achievements': {
                'unlocked': [a for a in self.achievements if a.unlocked],
                'locked': [a for a in self.achievements if not a.unlocked],
                'total': len(self.achievements)
            },
            'daily_challenges': self.daily_challenges
        }
    
    def get_leaderboard_data(self) -> Dict:
        return {
            'player_rank': 1,  # Placeholder
            'total_players': 1,  # Placeholder
            'percentile': 100,  # Placeholder
            'stats': self.player_stats
        }


# Gamification display utilities
def display_rewards(rewards: List[Dict]):
    if not rewards:
        return
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    for reward in rewards:
        if reward['type'] == 'xp':
            xp_data = reward['data']
            text = Text()
            text.append("✨ XP GAINED ✨\n", style="bold yellow")
            text.append(f"+{xp_data['xp_gained']} XP", style="bright_green")
            if xp_data.get('level_up'):
                text.append(f"\n🎉 LEVEL UP! 🎉\n", style="bold magenta")
                text.append(f"Level {xp_data['level_up']['new_level']}", style="bright_cyan")
            
            console.print(Panel(text, border_style="yellow"))
        
        elif reward['type'] == 'achievement':
            achievement_data = reward['data']
            achievement = achievement_data['achievement']
            
            rarity_colors = {
                'common': 'white',
                'rare': 'blue', 
                'epic': 'magenta',
                'legendary': 'gold1'
            }
            
            text = Text()
            text.append("🏆 ACHIEVEMENT UNLOCKED! 🏆\n", style="bold gold1")
            text.append(f"{achievement.icon} {achievement.name}\n", style=f"bold {rarity_colors.get(achievement.rarity, 'white')}")
            text.append(f"{achievement.description}\n", style="dim white")
            text.append(f"+{achievement.xp_reward} XP", style="bright_green")
            
            console.print(Panel(text, border_style=rarity_colors.get(achievement.rarity, 'white')))
        
        elif reward['type'] == 'daily_challenge':
            challenge_data = reward['data']
            challenge = challenge_data['challenge']
            
            text = Text()
            text.append("⭐ DAILY CHALLENGE COMPLETE! ⭐\n", style="bold cyan")
            text.append(f"{challenge.name}\n", style="bold white")
            text.append(f"{challenge.description}\n", style="dim white")
            text.append(f"+{challenge.xp_reward} XP", style="bright_green")
            
            console.print(Panel(text, border_style="cyan"))


# Export for CLI integration
__all__ = ['GamificationEngine', 'display_rewards', 'PlayerStats', 'Achievement']
