#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/revolutionary_features.py

import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align

from logbuch.features.smart_environment import SmartEnvironmentManager
from logbuch.features.autopilot import ProductivityAutopilot
from logbuch.features.social_productivity import SocialProductivityNetwork


class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
        self.console = Console()
    
    def execute(self, **kwargs):
        return True


class SmartEnvironmentCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.env_manager = SmartEnvironmentManager()
    
    def execute(self, **kwargs):
        try:
            dashboard = self.env_manager.get_environment_dashboard()
            
            # Header
            header_text = Text()
            header_text.append("🌍 SMART ENVIRONMENT DASHBOARD\n", style="bold bright_cyan")
            header_text.append("Context-Aware Productivity Optimization", style="dim bright_white")
            
            self.console.print(Panel(
                Align.center(header_text),
                title="🤖 AI Environment Intelligence",
                border_style="bright_cyan"
            ))
            
            # Current context
            context = dashboard['context']
            context_text = Text()
            context_text.append("📊 CURRENT CONTEXT\n", style="bold bright_yellow")
            context_text.append(f"🌤️  Weather: {context.weather.title()} ({context.temperature:.1f}°C)\n", style="white")
            context_text.append(f"🕐 Time: {context.time_of_day.replace('_', ' ').title()}\n", style="white")
            context_text.append(f"🔋 Battery: {context.battery_level:.0f}%\n", style="green" if context.battery_level > 50 else "red")
            context_text.append(f"💻 CPU: {context.cpu_usage:.1f}%\n", style="white")
            context_text.append(f"🧠 Memory: {context.memory_usage:.1f}%\n", style="white")
            context_text.append(f"🌐 Network: {'Connected' if context.network_status else 'Offline'}\n", style="green" if context.network_status else "red")
            context_text.append(f"🎯 Focus Mode: {'Active' if context.focus_mode else 'Inactive'}", style="cyan" if context.focus_mode else "dim white")
            
            self.console.print(Panel(context_text, title="🌍 Environment Context", border_style="bright_yellow"))
            
            # Smart suggestions
            suggestions = dashboard['suggestions']
            if suggestions:
                self.console.print("💡 Smart Environment Suggestions", style="bold bright_magenta")
                
                for i, suggestion in enumerate(suggestions[:3], 1):
                    priority_color = {
                        9: "red", 8: "orange1", 7: "yellow", 
                        6: "cyan", 5: "blue"
                    }.get(suggestion.priority, "white")
                    
                    suggestion_text = Text()
                    suggestion_text.append(f"{i}. {suggestion.title}\n", style=f"bold {priority_color}")
                    suggestion_text.append(f"{suggestion.description}\n", style="white")
                    suggestion_text.append(f"Context: {suggestion.context} | Priority: {suggestion.priority}/10", style="dim white")
                    
                    self.console.print(Panel(suggestion_text, border_style=priority_color))
            
            # Auto-optimizations
            optimizations = dashboard['optimizations']
            if optimizations:
                opt_text = Text()
                opt_text.append("🔧 AUTO-OPTIMIZATIONS APPLIED\n", style="bold bright_green")
                for opt in optimizations:
                    opt_text.append(f"{opt}\n", style="green")
                
                self.console.print(Panel(opt_text, title="⚡ Automatic Optimizations", border_style="bright_green"))
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error displaying smart environment: {e}", style="red")
            return False


class AutopilotCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.autopilot = ProductivityAutopilot(storage)
    
    def execute(self, action: str = "dashboard", **kwargs):
        try:
            if action == "dashboard":
                return self._show_dashboard()
            elif action == "analyze":
                return self._show_analysis()
            elif action == "auto-tasks":
                return self._show_auto_tasks()
            elif action == "schedule":
                return self._show_schedule()
            else:
                return self._show_dashboard()
                
        except Exception as e:
            self.console.print(f"❌ Error in autopilot: {e}", style="red")
            return False
    
    def _show_dashboard(self):
        dashboard = self.autopilot.get_autopilot_dashboard()
        
        # Header
        header_text = Text()
        header_text.append("🚁 PRODUCTIVITY AUTOPILOT\n", style="bold bright_cyan")
        header_text.append("Hands-Free Productivity Management", style="dim bright_white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="🤖 AI Autopilot System",
            border_style="bright_cyan"
        ))
        
        # Mode and settings
        mode_text = Text()
        mode_text.append(f"🎛️  Mode: {dashboard['mode'].title()}\n", style="bold bright_yellow")
        settings = dashboard['settings']
        mode_text.append(f"✅ Auto-create tasks: {settings['auto_create_tasks']}\n", style="green" if settings['auto_create_tasks'] else "dim white")
        mode_text.append(f"✅ Auto-schedule: {settings['auto_schedule_sessions']}\n", style="green" if settings['auto_schedule_sessions'] else "dim white")
        mode_text.append(f"✅ Auto-priorities: {settings['auto_adjust_priorities']}\n", style="green" if settings['auto_adjust_priorities'] else "dim white")
        mode_text.append(f"✅ Auto-breaks: {settings['auto_suggest_breaks']}", style="green" if settings['auto_suggest_breaks'] else "dim white")
        
        self.console.print(Panel(mode_text, title="⚙️ Autopilot Settings", border_style="bright_yellow"))
        
        # Auto-generated tasks
        auto_tasks = dashboard['auto_tasks']
        if auto_tasks:
            tasks_table = Table(title="🤖 Auto-Generated Tasks", show_header=True, header_style="bold bright_magenta")
            tasks_table.add_column("Task", style="cyan", width=30)
            tasks_table.add_column("Priority", style="yellow", width=8)
            tasks_table.add_column("Duration", style="green", width=10)
            tasks_table.add_column("Confidence", style="blue", width=12)
            tasks_table.add_column("Context", style="white", width=25)
            
            for task in auto_tasks:
                confidence_pct = f"{task.confidence*100:.0f}%"
                tasks_table.add_row(
                    task.title,
                    task.priority.title(),
                    f"{task.estimated_duration}min",
                    confidence_pct,
                    task.context
                )
            
            self.console.print(tasks_table)
        
        # Priority adjustments
        adjustments = dashboard['priority_adjustments']
        if adjustments:
            adj_text = Text()
            adj_text.append("🎯 PRIORITY ADJUSTMENTS\n", style="bold bright_yellow")
            for adj in adjustments[:3]:
                adj_text.append(f"• {adj['title']}\n", style="white")
                adj_text.append(f"  {adj['current_priority']} → {adj['suggested_priority']} ({adj['reason']})\n", style="dim white")
            
            self.console.print(Panel(adj_text, title="⚡ Smart Priority Optimization", border_style="bright_yellow"))
        
        return True
    
    def _show_analysis(self):
        patterns = self.autopilot.analyze_patterns()
        
        self.console.print("📊 Productivity Pattern Analysis", style="bold bright_cyan")
        
        # Peak hours
        peak_hours = patterns.get('peak_hours', {})
        if peak_hours.get('hours'):
            hours_text = Text()
            hours_text.append("🕐 Peak Productivity Hours\n", style="bold bright_yellow")
            hours_text.append(f"Hours: {', '.join(map(str, peak_hours['hours']))}\n", style="cyan")
            hours_text.append(f"Confidence: {peak_hours['confidence']*100:.0f}%", style="green")
            
            self.console.print(Panel(hours_text, border_style="bright_yellow"))
        
        # Task patterns
        task_types = patterns.get('task_types', {})
        if task_types.get('common_keywords'):
            keywords_text = Text()
            keywords_text.append("📝 Common Task Patterns\n", style="bold bright_magenta")
            for keyword, count in task_types['common_keywords'][:5]:
                keywords_text.append(f"• {keyword}: {count} times\n", style="white")
            
            self.console.print(Panel(keywords_text, border_style="bright_magenta"))
        
        return True
    
    def _show_auto_tasks(self):
        auto_tasks = self.autopilot.auto_create_tasks()
        
        if not auto_tasks:
            self.console.print("No auto-generated tasks available. Keep using Logbuch to build patterns!", style="yellow")
            return True
        
        self.console.print("🤖 Auto-Generated Tasks", style="bold bright_cyan")
        
        for i, task in enumerate(auto_tasks, 1):
            task_text = Text()
            task_text.append(f"{i}. {task.title}\n", style="bold cyan")
            task_text.append(f"{task.description}\n", style="white")
            task_text.append(f"Priority: {task.priority} | Duration: {task.estimated_duration}min\n", style="yellow")
            task_text.append(f"Optimal time: {task.optimal_time} | Confidence: {task.confidence*100:.0f}%\n", style="green")
            task_text.append(f"Context: {task.context}", style="dim white")
            
            self.console.print(Panel(task_text, border_style="cyan"))
        
        return True
    
    def _show_schedule(self):
        sessions = self.autopilot.auto_schedule_work_sessions()
        
        if not sessions:
            self.console.print("No auto-scheduled sessions available.", style="yellow")
            return True
        
        self.console.print("📅 Auto-Scheduled Work Sessions", style="bold bright_cyan")
        
        for session in sessions:
            session_text = Text()
            session_text.append(f"🎯 {session.session_type.replace('_', ' ').title()}\n", style="bold cyan")
            session_text.append(f"Time: {session.start_time.strftime('%H:%M')}\n", style="white")
            session_text.append(f"Duration: {session.duration} minutes\n", style="yellow")
            session_text.append(f"Breaks: {', '.join(map(str, session.break_intervals))} min", style="green")
            
            self.console.print(Panel(session_text, border_style="cyan"))
        
        return True


class SocialCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.social_network = SocialProductivityNetwork(storage)
    
    def execute(self, action: str = "dashboard", **kwargs):
        try:
            if action == "dashboard":
                return self._show_dashboard()
            elif action == "buddies":
                return self._show_buddies()
            elif action == "challenges":
                return self._show_challenges()
            elif action == "leaderboard":
                return self._show_leaderboard()
            elif action == "feed":
                return self._show_social_feed()
            else:
                return self._show_dashboard()
                
        except Exception as e:
            self.console.print(f"❌ Error in social network: {e}", style="red")
            return False
    
    def _show_dashboard(self):
        dashboard = self.social_network.get_social_dashboard()
        
        # Header
        header_text = Text()
        header_text.append("👥 SOCIAL PRODUCTIVITY NETWORK\n", style="bold bright_cyan")
        header_text.append("Connect • Compete • Achieve Together", style="dim bright_white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="🌐 Social Productivity Hub",
            border_style="bright_cyan"
        ))
        
        # Stats overview
        stats_left = Text()
        stats_left.append("📊 YOUR STATS\n", style="bold bright_yellow")
        stats_left.append(f"🤝 Buddies: {dashboard['buddies']}\n", style="cyan")
        stats_left.append(f"🏆 Challenges: {dashboard['active_challenges']}\n", style="green")
        stats_left.append(f"🎖️ Social Achievements: {dashboard['social_achievements']}\n", style="magenta")
        stats_left.append(f"📈 Leaderboard: #{dashboard['leaderboard_position']}", style="yellow")
        
        stats_right = Text()
        stats_right.append("💪 SOCIAL IMPACT\n", style="bold bright_green")
        stats = dashboard['stats']
        stats_right.append(f"💌 Encouragements Sent: {stats['total_encouragements_sent']}\n", style="green")
        stats_right.append(f"❤️ Encouragements Received: {stats['total_encouragements_received']}\n", style="red")
        stats_right.append(f"🎯 Avg Accountability: {stats['average_accountability_score']:.1f}/10", style="blue")
        
        self.console.print(Panel(
            Columns([stats_left, stats_right], equal=True),
            title="📊 Social Statistics",
            border_style="bright_yellow"
        ))
        
        # Recent social feed
        feed = dashboard['social_feed']
        if feed:
            feed_text = Text()
            feed_text.append("📱 RECENT ACTIVITY\n", style="bold bright_magenta")
            for item in feed:
                timestamp = item['timestamp'].strftime('%H:%M')
                feed_text.append(f"[{timestamp}] {item['content']}\n", style="white")
                if item.get('likes'):
                    feed_text.append(f"  ❤️ {item['likes']} likes\n", style="dim red")
            
            self.console.print(Panel(feed_text, title="🌊 Social Feed", border_style="bright_magenta"))
        
        return True
    
    def _show_buddies(self):
        buddies = self.social_network.buddies
        
        if not buddies:
            self.console.print("No productivity buddies yet. Find some accountability partners!", style="yellow")
            
            # Show buddy suggestions
            suggestions = self.social_network.find_productivity_buddies({})
            if suggestions:
                self.console.print("\n💡 Suggested Productivity Buddies", style="bold bright_cyan")
                
                for suggestion in suggestions[:3]:
                    buddy_text = Text()
                    buddy_text.append(f"👤 {suggestion['username']}\n", style="bold cyan")
                    buddy_text.append(f"Compatibility: {suggestion['compatibility_score']*100:.0f}%\n", style="green")
                    buddy_text.append(f"Level: {suggestion['productivity_level'].title()}\n", style="yellow")
                    buddy_text.append(f"Achievements: {suggestion['achievements']} | Streak: {suggestion['current_streak']}\n", style="white")
                    buddy_text.append(f"Interests: {', '.join(suggestion['shared_interests'])}", style="dim white")
                    
                    self.console.print(Panel(buddy_text, border_style="cyan"))
            
            return True
        
        # Show existing buddies
        buddies_table = Table(title="🤝 Your Productivity Buddies", show_header=True, header_style="bold bright_cyan")
        buddies_table.add_column("Buddy", style="cyan", width=20)
        buddies_table.add_column("Role", style="yellow", width=12)
        buddies_table.add_column("Score", style="green", width=8)
        buddies_table.add_column("Support", style="blue", width=15)
        buddies_table.add_column("Last Contact", style="white", width=15)
        
        for buddy in buddies:
            days_ago = (datetime.datetime.now() - buddy.last_interaction).days
            last_contact = f"{days_ago} days ago" if days_ago > 0 else "Today"
            
            buddies_table.add_row(
                buddy.username,
                buddy.role.value.title(),
                f"{buddy.accountability_score:.1f}/10",
                f"↗️{buddy.support_given} ↙️{buddy.support_received}",
                last_contact
            )
        
        self.console.print(buddies_table)
        return True
    
    def _show_challenges(self):
        challenges = self.social_network.team_challenges
        
        if not challenges:
            self.console.print("No active challenges. Create or join one!", style="yellow")
            return True
        
        for challenge in challenges:
            if challenge.status != "active":
                continue
            
            challenge_text = Text()
            challenge_text.append(f"🏆 {challenge.title}\n", style="bold bright_yellow")
            challenge_text.append(f"{challenge.description}\n", style="white")
            challenge_text.append(f"Target: {challenge.target_value} {challenge.target_metric}\n", style="cyan")
            
            # Progress
            challenge_text.append(f"\n📊 Current Progress:\n", style="bold white")
            for user_id, progress in challenge.current_progress.items():
                display_name = "You" if user_id == self.social_network.user_id else user_id
                progress_pct = (progress / challenge.target_value) * 100
                challenge_text.append(f"• {display_name}: {progress}/{challenge.target_value} ({progress_pct:.0f}%)\n", style="green")
            
            # Rewards
            challenge_text.append(f"\n🎁 Rewards: Winner: {challenge.rewards['winner']} XP, Participant: {challenge.rewards['participant']} XP", style="yellow")
            
            self.console.print(Panel(challenge_text, border_style="bright_yellow"))
        
        return True
    
    def _show_leaderboard(self):
        leaderboard = self.social_network.get_leaderboard()
        
        self.console.print("🏆 Productivity Leaderboard", style="bold bright_yellow")
        
        leaderboard_table = Table(show_header=True, header_style="bold bright_yellow")
        leaderboard_table.add_column("Rank", style="yellow", width=6)
        leaderboard_table.add_column("User", style="cyan", width=20)
        leaderboard_table.add_column("Score", style="green", width=10)
        leaderboard_table.add_column("Achievements", style="magenta", width=12)
        leaderboard_table.add_column("Streak", style="orange1", width=8)
        leaderboard_table.add_column("Status", style="white", width=10)
        
        for entry in leaderboard:
            rank_style = "gold1" if entry['rank'] == 1 else "silver" if entry['rank'] == 2 else "orange3" if entry['rank'] == 3 else "white"
            
            status = ""
            if entry['is_self']:
                status = "👤 You"
            elif entry['is_buddy']:
                status = "🤝 Buddy"
            
            leaderboard_table.add_row(
                f"#{entry['rank']}",
                entry['username'],
                str(entry['score']),
                str(entry['achievements']),
                f"{entry['streak']} days",
                status,
                style=rank_style if entry['is_self'] else None
            )
        
        self.console.print(leaderboard_table)
        return True
    
    def _show_social_feed(self):
        feed = self.social_network.get_social_feed()
        
        self.console.print("📱 Social Productivity Feed", style="bold bright_magenta")
        
        for item in feed:
            feed_text = Text()
            
            # Icon based on type
            icon = {
                "buddy_achievement": "🏆",
                "challenge_update": "⚡",
                "motivation": "💪"
            }.get(item['type'], "📢")
            
            timestamp = item['timestamp'].strftime('%H:%M')
            feed_text.append(f"{icon} [{timestamp}] ", style="dim white")
            feed_text.append(f"{item['content']}\n", style="white")
            
            if item.get('likes'):
                feed_text.append(f"❤️ {item['likes']} likes", style="dim red")
            
            if item.get('can_like'):
                feed_text.append(" • 👍 Like", style="dim blue")
            
            if item.get('can_comment'):
                feed_text.append(" • 💬 Comment", style="dim cyan")
            
            self.console.print(Panel(feed_text, border_style="magenta"))
        
        return True


# Export commands
__all__ = ['SmartEnvironmentCommand', 'AutopilotCommand', 'SocialCommand']
