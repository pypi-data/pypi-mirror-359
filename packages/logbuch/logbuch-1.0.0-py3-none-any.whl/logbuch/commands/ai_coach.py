#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/ai_coach.py

import datetime
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn

from logbuch.features.ai_coach import AIProductivityCoach, CoachingType


class BaseCommand:
    def __init__(self, storage):
        self.storage = storage
    
    def execute(self, args: Dict) -> bool:
        return True


class CoachCommand(BaseCommand):
    def __init__(self, storage, ai_coach: AIProductivityCoach):
        super().__init__(storage)
        self.ai_coach = ai_coach
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            # Show loading animation
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]AI Coach analyzing your productivity patterns..."),
                console=self.console
            ) as progress:
                task = progress.add_task("Analyzing", total=None)
                
                # Generate coaching brief
                brief = self.ai_coach.get_daily_coaching_brief()
                progress.update(task, completed=100)
            
            # Display coaching dashboard
            self._display_coaching_header(brief)
            self._display_productivity_score(brief['productivity_score'])
            self._display_today_focus(brief['today_focus'])
            self._display_key_insights(brief['key_insights'])
            self._display_quick_wins(brief['quick_wins'])
            self._display_energy_forecast(brief['energy_forecast'])
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error generating coaching insights: {e}", style="red")
            return False
    
    def _display_coaching_header(self, brief):
        header_text = Text()
        header_text.append("🧠 AI PRODUCTIVITY COACH\n", style="bold cyan")
        header_text.append(f"Daily Brief for {brief['date']}\n", style="bright_white")
        header_text.append("Your Personal Success Strategist", style="dim white")
        
        self.console.print(Panel(
            Align.center(header_text),
            title="AI Coach Dashboard",
            border_style="cyan"
        ))
    
    def _display_productivity_score(self, score: float):
        # Create score visualization
        score_text = Text()
        score_text.append("📊 Productivity Score: ", style="bold white")
        
        # Color based on score
        if score >= 8:
            color = "bright_green"
            status = "Excellent"
        elif score >= 6:
            color = "yellow"
            status = "Good"
        elif score >= 4:
            color = "orange1"
            status = "Fair"
        else:
            color = "red"
            status = "Needs Improvement"
        
        score_text.append(f"{score:.1f}/10", style=f"bold {color}")
        score_text.append(f" ({status})", style=f"dim {color}")
        
        # Progress bar
        with Progress(
            TextColumn("[bold blue]Productivity"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("Score", total=10)
            progress.update(task, completed=score)
        
        self.console.print(score_text)
        self.console.print()
    
    def _display_today_focus(self, focus: str):
        focus_text = Text()
        focus_text.append("🎯 Today's Focus\n", style="bold yellow")
        focus_text.append(focus, style="white")
        
        self.console.print(Panel(focus_text, border_style="yellow"))
    
    def _display_key_insights(self, insights: List):
        if not insights:
            return
        
        self.console.print("💡 Key Insights", style="bold magenta")
        
        for i, insight in enumerate(insights[:3], 1):
            # Urgency styling
            urgency_colors = {
                'low': 'dim white',
                'medium': 'yellow',
                'high': 'orange1',
                'critical': 'red'
            }
            urgency_color = urgency_colors.get(insight.urgency, 'white')
            
            insight_text = Text()
            insight_text.append(f"{i}. {insight.title}\n", style="bold white")
            insight_text.append(f"{insight.insight}\n", style="dim white")
            insight_text.append(f"Confidence: {insight.confidence*100:.0f}% | ", style="dim cyan")
            insight_text.append(f"Impact: {insight.impact_score:.1f}/10 | ", style="dim green")
            insight_text.append(f"Urgency: {insight.urgency.title()}", style=urgency_color)
            
            # Action items
            if insight.action_items:
                insight_text.append("\n\nRecommended Actions:", style="bold cyan")
                for action in insight.action_items[:2]:  # Show top 2 actions
                    insight_text.append(f"\n• {action}", style="cyan")
            
            self.console.print(Panel(insight_text, border_style=urgency_color))
    
    def _display_quick_wins(self, quick_wins: List[str]):
        wins_text = Text()
        wins_text.append("⚡ Quick Wins (5 min each)\n", style="bold green")
        
        for i, win in enumerate(quick_wins[:3], 1):
            wins_text.append(f"{i}. {win}\n", style="green")
        
        self.console.print(Panel(wins_text, border_style="green"))
    
    def _display_energy_forecast(self, forecast: str):
        energy_text = Text()
        energy_text.append("🔋 Energy Forecast\n", style="bold blue")
        energy_text.append(forecast, style="blue")
        
        self.console.print(Panel(energy_text, border_style="blue"))


class InsightsCommand(BaseCommand):
    def __init__(self, storage, ai_coach: AIProductivityCoach):
        super().__init__(storage)
        self.ai_coach = ai_coach
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            # Generate fresh insights
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Generating personalized insights..."),
                console=self.console
            ) as progress:
                task = progress.add_task("Analyzing", total=None)
                insights = self.ai_coach.generate_coaching_insights()
                progress.update(task, completed=100)
            
            if not insights:
                self.console.print("No new insights available. Keep using Logbuch to generate more data!", style="yellow")
                return True
            
            self.console.print("🧠 Personalized Coaching Insights", style="bold cyan")
            self.console.print(f"Generated {len(insights)} insights based on your productivity patterns\n", style="dim white")
            
            for i, insight in enumerate(insights, 1):
                self._display_detailed_insight(i, insight)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error generating insights: {e}", style="red")
            return False
    
    def _display_detailed_insight(self, index: int, insight):
        # Type styling
        type_colors = {
            CoachingType.PRODUCTIVITY_OPTIMIZATION: "bright_green",
            CoachingType.HABIT_FORMATION: "blue",
            CoachingType.STRESS_MANAGEMENT: "red",
            CoachingType.GOAL_ACHIEVEMENT: "magenta",
            CoachingType.TIME_MANAGEMENT: "yellow",
            CoachingType.ENERGY_OPTIMIZATION: "orange1",
            CoachingType.FOCUS_ENHANCEMENT: "cyan"
        }
        type_color = type_colors.get(insight.type, "white")
        
        # Urgency styling
        urgency_colors = {
            'low': 'dim white',
            'medium': 'yellow',
            'high': 'orange1',
            'critical': 'red'
        }
        urgency_color = urgency_colors.get(insight.urgency, 'white')
        
        insight_text = Text()
        insight_text.append(f"#{index} {insight.title}\n", style=f"bold {type_color}")
        insight_text.append(f"Category: {insight.type.value.replace('_', ' ').title()}\n", style=f"dim {type_color}")
        insight_text.append(f"\n{insight.insight}\n", style="white")
        
        # Metrics
        insight_text.append(f"\n📊 Metrics:\n", style="bold white")
        insight_text.append(f"• Confidence: {insight.confidence*100:.0f}%\n", style="cyan")
        insight_text.append(f"• Impact Score: {insight.impact_score:.1f}/10\n", style="green")
        insight_text.append(f"• Urgency: {insight.urgency.title()}\n", style=urgency_color)
        
        # Data points
        if insight.data_points:
            insight_text.append(f"\n📈 Based on:\n", style="bold white")
            for point in insight.data_points:
                insight_text.append(f"• {point}\n", style="dim white")
        
        # Action items
        if insight.action_items:
            insight_text.append(f"\n🎯 Action Plan:\n", style="bold cyan")
            for j, action in enumerate(insight.action_items, 1):
                insight_text.append(f"{j}. {action}\n", style="cyan")
        
        self.console.print(Panel(insight_text, border_style=type_color))
        self.console.print()


class PatternsCommand(BaseCommand):
    def __init__(self, storage, ai_coach: AIProductivityCoach):
        super().__init__(storage)
        self.ai_coach = ai_coach
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            # Analyze patterns
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Analyzing your productivity patterns..."),
                console=self.console
            ) as progress:
                task = progress.add_task("Analyzing", total=None)
                patterns = self.ai_coach.analyze_productivity_patterns()
                progress.update(task, completed=100)
            
            if not patterns:
                self.console.print("Not enough data to identify patterns. Keep using Logbuch!", style="yellow")
                return True
            
            self.console.print("📊 Your Productivity Patterns", style="bold cyan")
            self.console.print(f"Discovered {len(patterns)} patterns in your behavior\n", style="dim white")
            
            # Create patterns table
            patterns_table = Table(title="Pattern Analysis", show_header=True, header_style="bold magenta")
            patterns_table.add_column("Pattern", style="cyan", width=20)
            patterns_table.add_column("Description", style="white", width=40)
            patterns_table.add_column("Impact", style="yellow", width=10)
            patterns_table.add_column("Confidence", style="green", width=12)
            patterns_table.add_column("Recommendation", style="blue", width=35)
            
            for pattern in patterns:
                confidence_pct = f"{pattern.confidence*100:.0f}%"
                patterns_table.add_row(
                    pattern.pattern_type.replace('_', ' ').title(),
                    pattern.description,
                    pattern.impact,
                    confidence_pct,
                    pattern.recommendation
                )
            
            self.console.print(patterns_table)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error analyzing patterns: {e}", style="red")
            return False


class CoachStatsCommand(BaseCommand):
    def __init__(self, storage, ai_coach: AIProductivityCoach):
        super().__init__(storage)
        self.ai_coach = ai_coach
        self.console = Console()
    
    def execute(self, args: Dict) -> bool:
        try:
            insights_history = self.ai_coach.insights_history
            
            if not insights_history:
                self.console.print("No coaching history available yet.", style="yellow")
                return True
            
            # Calculate statistics
            total_insights = len(insights_history)
            implemented = len([i for i in insights_history if i.implemented])
            avg_confidence = sum(i.confidence for i in insights_history) / total_insights
            avg_impact = sum(i.impact_score for i in insights_history) / total_insights
            
            # Group by type
            type_counts = {}
            for insight in insights_history:
                type_name = insight.type.value.replace('_', ' ').title()
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            # Display header
            stats_text = Text()
            stats_text.append("🧠 AI Coach Performance\n", style="bold cyan")
            stats_text.append(f"Total Insights Generated: {total_insights}\n", style="white")
            stats_text.append(f"Insights Implemented: {implemented} ({implemented/total_insights*100:.1f}%)\n", style="green")
            stats_text.append(f"Average Confidence: {avg_confidence*100:.1f}%\n", style="cyan")
            stats_text.append(f"Average Impact Score: {avg_impact:.1f}/10", style="yellow")
            
            self.console.print(Panel(stats_text, title="Coach Statistics", border_style="cyan"))
            
            # Insights by category
            category_table = Table(title="Insights by Category", show_header=True, header_style="bold magenta")
            category_table.add_column("Category", style="cyan")
            category_table.add_column("Count", style="white")
            category_table.add_column("Percentage", style="yellow")
            
            for category, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = f"{count/total_insights*100:.1f}%"
                category_table.add_row(category, str(count), percentage)
            
            self.console.print(category_table)
            
            # Recent insights
            recent_insights = sorted(insights_history, key=lambda x: x.created_at, reverse=True)[:5]
            
            self.console.print("\n🕐 Recent Insights", style="bold cyan")
            for insight in recent_insights:
                days_ago = (datetime.datetime.now() - insight.created_at).days
                time_text = f"{days_ago} days ago" if days_ago > 0 else "Today"
                
                recent_text = Text()
                recent_text.append(f"• {insight.title}", style="white")
                recent_text.append(f" ({time_text})", style="dim white")
                if insight.implemented:
                    recent_text.append(" ✅", style="green")
                
                self.console.print(recent_text)
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error displaying coach stats: {e}", style="red")
            return False


# Export commands
__all__ = ['CoachCommand', 'InsightsCommand', 'PatternsCommand', 'CoachStatsCommand']
