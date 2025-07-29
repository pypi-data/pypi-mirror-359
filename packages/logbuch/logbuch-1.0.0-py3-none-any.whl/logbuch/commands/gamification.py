#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/gamification.py

import datetime
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from logbuch.features.gamification import GamificationEngine, AchievementType


class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
    
    def execute(self, args: Dict) -> bool:
        return True


class ProfileCommand(BaseCommand):
    def __init__(self, storage, gamification_engine: GamificationEngine):
        super().__init__(storage)
        self.gamification = gamification_engine
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            profile = self.gamification.get_player_profile()
            stats = profile['stats']
            
            # Create main profile panel
            self._display_player_header(stats, profile)
            
            # Display level progress
            self._display_level_progress(profile)
            
            # Display achievements summary
            self._display_achievements_summary(profile['achievements'])
            
            # Display daily challenges
            self._display_daily_challenges(profile['daily_challenges'])
            
            # Display recent activity stats
            self._display_activity_stats(stats)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error displaying profile: {e}", style="red")
            return False
    
    def _display_player_header(self, stats, profile):
        header_text = Text()
        header_text.append(f"🎮 {stats.title}\n", style="bold cyan")
        header_text.append(f"Rank: {stats.rank} | Level {stats.level}\n", style="bright_white")
        header_text.append(f"Total XP: {stats.total_xp:,}", style="yellow")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="Player Profile",
            border_style="cyan"
        ))
    
    def _display_level_progress(self, profile):
        with Progress(
            TextColumn("[bold blue]Level Progress"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("Level", total=100)
            progress.update(task, completed=profile['level_progress'])
        
        self.console.print(f"XP to next level: {profile['xp_to_next_level']:,}", style="dim white")
        self.console.print()
    
    def _display_achievements_summary(self, achievements):
        unlocked_count = len(achievements['unlocked'])
        total_count = achievements['total']
        
        achievement_text = Text()
        achievement_text.append("🏆 Achievements\n", style="bold gold1")
        achievement_text.append(f"{unlocked_count}/{total_count} unlocked ", style="white")
        achievement_text.append(f"({unlocked_count/total_count*100:.1f}%)", style="dim white")
        
        # Show recent achievements
        recent_achievements = sorted(
            achievements['unlocked'], 
            key=lambda a: a.unlocked_at or datetime.datetime.min,
            reverse=True
        )[:3]
        
        if recent_achievements:
            achievement_text.append("\n\nRecent unlocks:\n", style="dim white")
            for achievement in recent_achievements:
                rarity_colors = {
                    'common': 'white',
                    'rare': 'blue', 
                    'epic': 'magenta',
                    'legendary': 'gold1'
                }
                color = rarity_colors.get(achievement.rarity, 'white')
                achievement_text.append(f"{achievement.icon} {achievement.name}\n", style=color)
        
        self.console.print(Panel(achievement_text, border_style="gold1"))
    
    def _display_daily_challenges(self, challenges):
        if not challenges:
            return
        
        challenge_panels = []
        
        for challenge in challenges:
            status = "✅ Complete" if challenge.completed else f"{challenge.progress}/{challenge.target}"
            
            challenge_text = Text()
            challenge_text.append(f"{challenge.name}\n", style="bold white")
            challenge_text.append(f"{challenge.description}\n", style="dim white")
            challenge_text.append(f"Progress: {status}\n", style="cyan")
            challenge_text.append(f"Reward: {challenge.xp_reward} XP", style="yellow")
            
            panel_style = "green" if challenge.completed else "blue"
            challenge_panels.append(Panel(challenge_text, border_style=panel_style, width=25))
        
        self.console.print("⭐ Daily Challenges", style="bold cyan")
        self.console.print(Columns(challenge_panels, equal=True))
        self.console.print()
    
    def _display_activity_stats(self, stats):
        stats_table = Table(title="Activity Statistics", show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        stats_table.add_column("Achievement", style="yellow")
        
        stats_table.add_row("Tasks Completed", f"{stats.tasks_completed:,}", "🎯")
        stats_table.add_row("Journal Entries", f"{stats.journal_entries:,}", "📝")
        stats_table.add_row("Mood Entries", f"{stats.mood_entries:,}", "😊")
        stats_table.add_row("Current Streak", f"{stats.current_streak} days", "🔥")
        stats_table.add_row("Longest Streak", f"{stats.longest_streak} days", "⚡")
        stats_table.add_row("Productivity Score", f"{stats.productivity_score:.1f}", "📊")
        
        self.console.print(stats_table)


class AchievementsCommand(BaseCommand):
    def __init__(self, storage, gamification_engine: GamificationEngine):
        super().__init__(storage)
        self.gamification = gamification_engine
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            filter_type = args.get('type')
            show_locked = args.get('show_locked', True)
            
            achievements = self.gamification.achievements
            
            # Filter by type if specified
            if filter_type:
                try:
                    achievement_type = AchievementType(filter_type)
                    achievements = [a for a in achievements if a.type == achievement_type]
                except ValueError:
                    self.console.print(f"❌ Invalid achievement type: {filter_type}", style="red")
                    return False
            
            # Group achievements by type
            grouped_achievements = {}
            for achievement in achievements:
                if not show_locked and not achievement.unlocked:
                    continue
                
                type_name = achievement.type.value.replace('_', ' ').title()
                if type_name not in grouped_achievements:
                    grouped_achievements[type_name] = []
                grouped_achievements[type_name].append(achievement)
            
            # Display each group
            for type_name, type_achievements in grouped_achievements.items():
                self._display_achievement_group(type_name, type_achievements)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error displaying achievements: {e}", style="red")
            return False
    
    def _display_achievement_group(self, type_name: str, achievements: List):
        self.console.print(f"\n🏆 {type_name} Achievements", style="bold cyan")
        
        achievement_table = Table(show_header=True, header_style="bold magenta")
        achievement_table.add_column("Achievement", style="white", width=25)
        achievement_table.add_column("Description", style="dim white", width=35)
        achievement_table.add_column("Progress", style="cyan", width=15)
        achievement_table.add_column("Reward", style="yellow", width=10)
        achievement_table.add_column("Rarity", style="white", width=10)
        
        # Sort by unlocked status and rarity
        rarity_order = {'common': 1, 'rare': 2, 'epic': 3, 'legendary': 4}
        achievements.sort(key=lambda a: (not a.unlocked, rarity_order.get(a.rarity, 0)))
        
        for achievement in achievements:
            # Status and progress
            if achievement.unlocked:
                status = "✅ Unlocked"
                progress_text = f"{achievement.progress}/{achievement.target}"
            else:
                status = "🔒 Locked"
                progress_text = f"{achievement.progress}/{achievement.target}"
            
            # Rarity styling
            rarity_colors = {
                'common': 'white',
                'rare': 'blue', 
                'epic': 'magenta',
                'legendary': 'gold1'
            }
            rarity_style = rarity_colors.get(achievement.rarity, 'white')
            
            achievement_table.add_row(
                f"{achievement.icon} {achievement.name}",
                achievement.description,
                progress_text,
                f"{achievement.xp_reward} XP",
                f"[{rarity_style}]{achievement.rarity.title()}[/{rarity_style}]"
            )
        
        self.console.print(achievement_table)


class ChallengesCommand(BaseCommand):
    def __init__(self, storage, gamification_engine: GamificationEngine):
        super().__init__(storage)
        self.gamification = gamification_engine
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            challenges = self.gamification.daily_challenges
            
            if not challenges:
                self.console.print("No daily challenges available today.", style="yellow")
                return True
            
            self.console.print("⭐ Today's Challenges", style="bold cyan")
            
            for i, challenge in enumerate(challenges, 1):
                # Progress bar
                progress_percent = (challenge.progress / challenge.target) * 100
                
                challenge_text = Text()
                challenge_text.append(f"{i}. {challenge.name}\n", style="bold white")
                challenge_text.append(f"{challenge.description}\n", style="dim white")
                
                # Status
                if challenge.completed:
                    challenge_text.append("✅ Completed!", style="green")
                else:
                    challenge_text.append(f"Progress: {challenge.progress}/{challenge.target} ", style="cyan")
                    challenge_text.append(f"({progress_percent:.0f}%)", style="dim cyan")
                
                challenge_text.append(f"\nReward: {challenge.xp_reward} XP", style="yellow")
                
                # Time remaining
                now = datetime.datetime.now()
                time_remaining = challenge.expires_at - now
                hours_remaining = int(time_remaining.total_seconds() // 3600)
                challenge_text.append(f"\nExpires in: {hours_remaining}h", style="dim white")
                
                panel_style = "green" if challenge.completed else "blue"
                self.console.print(Panel(challenge_text, border_style=panel_style))
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error displaying challenges: {e}", style="red")
            return False


class LeaderboardCommand(BaseCommand):
    def __init__(self, storage, gamification_engine: GamificationEngine):
        super().__init__(storage)
        self.gamification = gamification_engine
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            leaderboard_data = self.gamification.get_leaderboard_data()
            
            self.console.print("🏆 Leaderboard", style="bold gold1")
            self.console.print("(Multiplayer features coming soon!)", style="dim white")
            
            # Show player's current standing
            stats = leaderboard_data['stats']
            
            standing_text = Text()
            standing_text.append("Your Current Standing:\n", style="bold cyan")
            standing_text.append(f"Rank: #{leaderboard_data['player_rank']}\n", style="white")
            standing_text.append(f"Level: {stats.level}\n", style="yellow")
            standing_text.append(f"Total XP: {stats.total_xp:,}\n", style="green")
            standing_text.append(f"Tasks Completed: {stats.tasks_completed:,}\n", style="blue")
            standing_text.append(f"Achievements: {stats.achievements_unlocked}", style="magenta")
            
            self.console.print(Panel(standing_text, border_style="gold1"))
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error displaying leaderboard: {e}", style="red")
            return False


# Export commands
__all__ = ['ProfileCommand', 'AchievementsCommand', 'ChallengesCommand', 'LeaderboardCommand']
