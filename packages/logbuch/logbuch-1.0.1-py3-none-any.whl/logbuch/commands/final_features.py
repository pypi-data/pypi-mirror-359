#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/final_features.py

import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from logbuch.features.quick_capture import QuickCaptureSystem, CaptureType
from logbuch.features.weather_productivity import WeatherProductivitySystem


class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
        self.console = Console()
    
    def execute(self, **kwargs):
        return True


class QuickCaptureCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.capture_system = QuickCaptureSystem(storage)
    
    def execute(self, action: str = "list", content: str = None, 
               capture_type: str = "auto", **kwargs):
        try:
            if action == "add" and content:
                return self._add_capture(content, capture_type)
            elif action == "list":
                return self._list_captures()
            elif action == "process":
                return self._process_captures()
            elif action == "stats":
                return self._show_stats()
            elif action == "search" and content:
                return self._search_captures(content)
            else:
                return self._show_help()
                
        except Exception as e:
            self.console.print(f"❌ Error in quick capture: {e}", style="red")
            return False
    
    def _add_capture(self, content: str, capture_type: str):
        capture_id = self.capture_system.quick_capture(content, capture_type)
        
        # Determine emoji based on type
        type_emojis = {
            "idea": "💡",
            "task": "✅", 
            "note": "📝",
            "quote": "💬",
            "link": "🔗",
            "reminder": "⏰",
            "goal": "🎯"
        }
        
        detected_type = self.capture_system._detect_type(content) if capture_type == "auto" else capture_type
        emoji = type_emojis.get(detected_type, "📝")
        
        success_text = Text()
        success_text.append(f"{emoji} Quick Capture Added!\n", style="bold bright_green")
        success_text.append(f"Type: {detected_type.title()}\n", style="cyan")
        success_text.append(f"Content: {content}\n", style="white")
        success_text.append(f"ID: {capture_id}", style="dim white")
        
        self.console.print(Panel(success_text, title="⚡ Lightning Fast Capture", border_style="bright_green"))
        return True
    
    def _list_captures(self):
        captures = self.capture_system.list_captures(unprocessed_only=True)
        
        if not captures:
            self.console.print("📝 No unprocessed captures. Use 'logbuch capture add \"your idea\"' to start!", style="yellow")
            return True
        
        # Header
        header_text = Text()
        header_text.append("⚡ QUICK CAPTURES\n", style="bold bright_cyan")
        header_text.append("Lightning-fast idea and task capture", style="dim bright_white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="💡 Capture System",
            border_style="bright_cyan"
        ))
        
        # Captures table
        captures_table = Table(title="📝 Unprocessed Captures", show_header=True, header_style="bold bright_yellow")
        captures_table.add_column("Type", style="cyan", width=10)
        captures_table.add_column("Content", style="white", width=50)
        captures_table.add_column("Tags", style="magenta", width=15)
        captures_table.add_column("Age", style="green", width=10)
        captures_table.add_column("ID", style="dim white", width=15)
        
        type_emojis = {
            "idea": "💡",
            "task": "✅",
            "note": "📝", 
            "quote": "💬",
            "link": "🔗",
            "reminder": "⏰",
            "goal": "🎯"
        }
        
        for capture in captures[:10]:  # Show latest 10
            age = datetime.datetime.now() - capture.created_at
            age_str = f"{age.days}d" if age.days > 0 else f"{age.seconds//3600}h"
            
            emoji = type_emojis.get(capture.type.value, "📝")
            type_display = f"{emoji} {capture.type.value.title()}"
            
            tags_display = " ".join([f"#{tag}" for tag in capture.tags]) if capture.tags else ""
            
            captures_table.add_row(
                type_display,
                capture.content[:47] + "..." if len(capture.content) > 50 else capture.content,
                tags_display,
                age_str,
                capture.id[-8:]  # Show last 8 chars of ID
            )
        
        self.console.print(captures_table)
        
        # Quick actions
        actions_text = Text()
        actions_text.append("🚀 Quick Actions:\n", style="bold bright_yellow")
        actions_text.append("logbuch capture process", style="cyan")
        actions_text.append(" - Convert captures to tasks/notes\n", style="dim white")
        actions_text.append("logbuch capture stats", style="cyan")
        actions_text.append("    - View capture statistics", style="dim white")
        
        self.console.print(Panel(actions_text, title="⚡ Next Steps", border_style="bright_yellow"))
        return True
    
    def _process_captures(self):
        unprocessed = self.capture_system.list_captures(unprocessed_only=True)
        
        if not unprocessed:
            self.console.print("✅ All captures are processed!", style="green")
            return True
        
        self.console.print(f"🔄 Processing {len(unprocessed)} captures...", style="cyan")
        
        processed_count = 0
        for capture in unprocessed[:5]:  # Process first 5
            if self.capture_system.process_capture(capture.id, "convert"):
                processed_count += 1
                
                type_emojis = {
                    "idea": "💡",
                    "task": "✅",
                    "note": "📝",
                    "quote": "💬", 
                    "link": "🔗",
                    "reminder": "⏰",
                    "goal": "🎯"
                }
                
                emoji = type_emojis.get(capture.type.value, "📝")
                self.console.print(f"  {emoji} Processed: {capture.content[:50]}...", style="green")
        
        success_text = Text()
        success_text.append(f"✅ Processed {processed_count} captures!\n", style="bold bright_green")
        success_text.append("Converted to tasks, notes, and goals in your Logbuch system.", style="white")
        
        self.console.print(Panel(success_text, title="🎉 Processing Complete", border_style="bright_green"))
        return True
    
    def _show_stats(self):
        stats = self.capture_system.get_capture_stats()
        
        # Header
        self.console.print("📊 Quick Capture Statistics", style="bold bright_cyan")
        
        # Main stats
        stats_left = Text()
        stats_left.append("📈 CAPTURE STATS\n", style="bold bright_yellow")
        stats_left.append(f"📝 Total Captures: {stats['total_captures']}\n", style="white")
        stats_left.append(f"✅ Processed: {stats['processed']}\n", style="green")
        stats_left.append(f"⏳ Unprocessed: {stats['unprocessed']}\n", style="yellow")
        stats_left.append(f"📊 Processing Rate: {stats['processing_rate']*100:.1f}%", style="cyan")
        
        stats_right = Text()
        stats_right.append("🎯 ACTIVITY\n", style="bold bright_green")
        stats_right.append(f"📅 Recent (7 days): {stats['recent_captures']}\n", style="white")
        if stats['most_common_type']:
            stats_right.append(f"🏆 Most Common: {stats['most_common_type'].title()}\n", style="magenta")
        
        # Type distribution
        if stats['type_distribution']:
            stats_right.append("\n📊 Type Distribution:\n", style="bold white")
            for type_name, count in stats['type_distribution'].items():
                stats_right.append(f"  {type_name}: {count}\n", style="dim white")
        
        self.console.print(Panel(
            Columns([stats_left, stats_right], equal=True),
            title="📊 Capture Analytics",
            border_style="bright_yellow"
        ))
        
        return True
    
    def _search_captures(self, query: str):
        results = self.capture_system.search_captures(query)
        
        if not results:
            self.console.print(f"🔍 No captures found matching '{query}'", style="yellow")
            return True
        
        self.console.print(f"🔍 Found {len(results)} captures matching '{query}':", style="cyan")
        
        for result in results[:5]:
            result_text = Text()
            result_text.append(f"💡 {result.type.value.title()}: ", style="cyan")
            result_text.append(f"{result.content}\n", style="white")
            result_text.append(f"Created: {result.created_at.strftime('%Y-%m-%d %H:%M')}", style="dim white")
            
            self.console.print(Panel(result_text, border_style="cyan"))
        
        return True
    
    def _show_help(self):
        help_text = Text()
        help_text.append("⚡ QUICK CAPTURE SYSTEM\n", style="bold bright_cyan")
        help_text.append("Lightning-fast idea and task capture inspired by Eureka\n\n", style="dim white")
        
        help_text.append("📝 Usage:\n", style="bold bright_yellow")
        help_text.append("logbuch capture add \"your idea\"", style="cyan")
        help_text.append("     # Quick capture\n", style="dim white")
        help_text.append("logbuch capture list", style="cyan")
        help_text.append("                # List captures\n", style="dim white")
        help_text.append("logbuch capture process", style="cyan")
        help_text.append("             # Convert to tasks\n", style="dim white")
        help_text.append("logbuch capture stats", style="cyan")
        help_text.append("               # View statistics\n", style="dim white")
        help_text.append("logbuch capture search \"query\"", style="cyan")
        help_text.append("      # Search captures", style="dim white")
        
        self.console.print(Panel(help_text, title="💡 Quick Capture Help", border_style="bright_cyan"))
        return True


class WeatherCommand(BaseCommand):
    def __init__(self, storage):
        super().__init__(storage)
        self.weather_system = WeatherProductivitySystem()
    
    def execute(self, action: str = "current", **kwargs):
        try:
            if action == "current":
                return self._show_current_weather()
            elif action == "advice":
                return self._show_productivity_advice()
            elif action == "week":
                return self._show_weekly_forecast()
            else:
                return self._show_current_weather()
                
        except Exception as e:
            self.console.print(f"❌ Error in weather system: {e}", style="red")
            return False
    
    def _show_current_weather(self):
        dashboard = self.weather_system.get_weather_dashboard()
        
        # Beautiful weather display
        weather_display = dashboard['weather_display']
        self.console.print(weather_display, style="bright_cyan")
        
        # Quick productivity tip
        advice = dashboard['productivity_advice']
        if 'recommendation' in advice:
            tip_text = Text()
            tip_text.append("💡 Productivity Tip: ", style="bold bright_yellow")
            tip_text.append(advice['recommendation']['title'], style="cyan")
            
            self.console.print(Panel(tip_text, border_style="bright_yellow"))
        
        return True
    
    def _show_productivity_advice(self):
        advice = self.weather_system.get_weather_productivity_advice()
        
        if 'error' in advice:
            self.console.print(f"❌ {advice['error']}", style="red")
            return False
        
        # Header
        weather_icon = advice['weather']['icon']
        condition = advice['weather']['condition'].title()
        temp = advice['weather']['temperature']
        
        header_text = Text()
        header_text.append(f"{weather_icon} WEATHER PRODUCTIVITY ADVISOR\n", style="bold bright_cyan")
        header_text.append(f"{condition} • {temp:.1f}°C", style="dim bright_white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="🌤️ Weather-Based Optimization",
            border_style="bright_cyan"
        ))
        
        # Recommendation
        rec = advice['recommendation']
        rec_text = Text()
        rec_text.append(f"{rec['title']}\n", style="bold bright_yellow")
        rec_text.append(f"{rec['description']}\n\n", style="white")
        rec_text.append(f"⚡ Energy Level: {rec['energy_level'].title()}\n", style="green")
        rec_text.append(f"🎯 Focus Rating: {rec['focus_rating']}/10\n", style="cyan")
        rec_text.append(f"🎨 Creativity Boost: {'Yes' if rec['creativity_boost'] else 'No'}\n", style="magenta")
        rec_text.append(f"🏠 Work Location: {'Indoors preferred' if rec['indoor_preference'] else 'Flexible'}", style="blue")
        
        self.console.print(Panel(rec_text, title="🎯 Today's Recommendation", border_style="bright_yellow"))
        
        # Task suggestions
        if advice['task_suggestions']:
            tasks_text = Text()
            tasks_text.append("📋 OPTIMAL TASKS FOR TODAY\n", style="bold bright_green")
            for i, task in enumerate(advice['task_suggestions'], 1):
                tasks_text.append(f"{i}. {task}\n", style="white")
            
            self.console.print(Panel(tasks_text, title="✅ Recommended Tasks", border_style="bright_green"))
        
        # Productivity multiplier
        multiplier = advice['productivity_multiplier']
        energy_forecast = advice['energy_forecast']
        
        bonus_text = Text()
        bonus_text.append(f"📈 Productivity Multiplier: {multiplier}x\n", style="bold bright_cyan")
        bonus_text.append(f"{energy_forecast}", style="yellow")
        
        self.console.print(Panel(bonus_text, title="⚡ Performance Forecast", border_style="bright_cyan"))
        
        return True
    
    def _show_weekly_forecast(self):
        weekly_data = self.weather_system.get_weekly_weather_productivity()
        
        self.console.print("📅 Weekly Weather-Productivity Forecast", style="bold bright_cyan")
        
        # Weekly table
        weekly_table = Table(show_header=True, header_style="bold bright_yellow")
        weekly_table.add_column("Day", style="cyan", width=12)
        weekly_table.add_column("Weather", style="white", width=15)
        weekly_table.add_column("Temp", style="green", width=8)
        weekly_table.add_column("Productivity", style="yellow", width=12)
        weekly_table.add_column("Energy", style="magenta", width=10)
        weekly_table.add_column("Best For", style="blue", width=20)
        
        for day_data in weekly_data:
            weather = day_data['weather']
            
            # Productivity rating as stars
            rating = day_data['productivity_rating']
            stars = "⭐" * (rating // 2) + "☆" * (5 - rating // 2)
            
            # Best tasks
            best_tasks = ", ".join(day_data['recommended_tasks'][:2])
            
            weekly_table.add_row(
                day_data['day_name'],
                f"{weather['icon']} {weather['condition'].title()}",
                f"{weather['temperature']:.0f}°C",
                f"{stars} ({rating}/10)",
                day_data['energy_level'].title(),
                best_tasks.replace('_', ' ').title()
            )
        
        self.console.print(weekly_table)
        
        # Weekly tip
        tip_text = Text()
        tip_text.append("💡 Weekly Planning Tip:\n", style="bold bright_yellow")
        tip_text.append("Schedule your most important tasks on high-productivity days!", style="white")
        
        self.console.print(Panel(tip_text, title="📈 Weekly Strategy", border_style="bright_yellow"))
        
        return True


# Export commands
__all__ = ['QuickCaptureCommand', 'WeatherCommand']
