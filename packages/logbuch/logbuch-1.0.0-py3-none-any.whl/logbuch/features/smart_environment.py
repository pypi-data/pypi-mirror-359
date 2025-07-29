#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/smart_environment.py

import datetime
import json
import requests
import psutil
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from logbuch.core.logger import get_logger


class EnvironmentMode(Enum):
    FOCUS = "focus"
    CREATIVE = "creative"
    COLLABORATIVE = "collaborative"
    MAINTENANCE = "maintenance"
    BREAK = "break"
    DEEP_WORK = "deep_work"
    MEETING = "meeting"


@dataclass
class EnvironmentContext:
    weather: str
    temperature: float
    time_of_day: str
    battery_level: float
    cpu_usage: float
    memory_usage: float
    network_status: bool
    focus_mode: bool
    calendar_events: List[Dict]
    location: Optional[str] = None


@dataclass
class SmartSuggestion:
    title: str
    description: str
    action: str
    priority: int
    context: str
    auto_apply: bool = False


class SmartEnvironmentManager:
    def __init__(self):
        self.logger = get_logger("smart_environment")
        self.current_mode = EnvironmentMode.FOCUS
        self.context_history = []
        
        # Weather API (you'd need to get a free API key)
        self.weather_api_key = None  # Set this in config
        
        self.logger.debug("Smart Environment Manager initialized")
    
    def get_current_context(self) -> EnvironmentContext:
        try:
            # System metrics
            battery = self._get_battery_level()
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            network = self._check_network_status()
            
            # Time context
            now = datetime.datetime.now()
            time_of_day = self._get_time_of_day(now)
            
            # Weather (mock for now - would integrate with real API)
            weather_data = self._get_weather_data()
            
            # Focus detection
            focus_mode = self._detect_focus_mode()
            
            # Calendar events (mock for now)
            calendar_events = self._get_calendar_events()
            
            context = EnvironmentContext(
                weather=weather_data.get('condition', 'unknown'),
                temperature=weather_data.get('temperature', 20.0),
                time_of_day=time_of_day,
                battery_level=battery,
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                network_status=network,
                focus_mode=focus_mode,
                calendar_events=calendar_events
            )
            
            self.context_history.append(context)
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting environment context: {e}")
            return self._get_default_context()
    
    def _get_battery_level(self) -> float:
        try:
            battery = psutil.sensors_battery()
            if battery:
                return battery.percent
            return 100.0  # Desktop/plugged in
        except:
            return 100.0
    
    def _check_network_status(self) -> bool:
        try:
            response = requests.get("https://8.8.8.8", timeout=3)
            return True
        except:
            return False
    
    def _get_time_of_day(self, now: datetime.datetime) -> str:
        hour = now.hour
        
        if 5 <= hour < 9:
            return "early_morning"
        elif 9 <= hour < 12:
            return "morning"
        elif 12 <= hour < 14:
            return "lunch"
        elif 14 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening"
        elif 20 <= hour < 23:
            return "night"
        else:
            return "late_night"
    
    def _get_weather_data(self) -> Dict:
        # Mock weather data - in real implementation, use weather API
        import random
        
        conditions = ["sunny", "cloudy", "rainy", "stormy", "foggy", "clear"]
        return {
            "condition": random.choice(conditions),
            "temperature": random.uniform(15, 30),
            "humidity": random.uniform(30, 80)
        }
    
    def _detect_focus_mode(self) -> bool:
        # Check for focus apps, do not disturb mode, etc.
        # This is a simplified version
        try:
            # On macOS, check for Do Not Disturb
            if platform.system() == "Darwin":
                # Would check system preferences
                pass
            
            # Check for focus apps running
            focus_apps = ["focus", "cold turkey", "freedom", "rescuetime"]
            running_processes = [p.info['name'].lower() for p in psutil.process_iter(['name'])]
            
            return any(app in ' '.join(running_processes) for app in focus_apps)
        except:
            return False
    
    def _get_calendar_events(self) -> List[Dict]:
        # Mock calendar events - would integrate with real calendar
        now = datetime.datetime.now()
        return [
            {
                "title": "Team Meeting",
                "start": (now + datetime.timedelta(hours=1)).isoformat(),
                "duration": 60,
                "type": "meeting"
            }
        ]
    
    def _get_default_context(self) -> EnvironmentContext:
        return EnvironmentContext(
            weather="unknown",
            temperature=20.0,
            time_of_day="unknown",
            battery_level=100.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            network_status=True,
            focus_mode=False,
            calendar_events=[]
        )
    
    def generate_smart_suggestions(self, context: EnvironmentContext) -> List[SmartSuggestion]:
        suggestions = []
        
        # Battery-based suggestions
        if context.battery_level < 20:
            suggestions.append(SmartSuggestion(
                title="🔋 Low Battery Alert",
                description="Battery is low. Consider plugging in or switching to low-power tasks.",
                action="switch_to_low_power_tasks",
                priority=9,
                context="battery",
                auto_apply=True
            ))
        
        # Weather-based suggestions
        if context.weather == "rainy":
            suggestions.append(SmartSuggestion(
                title="🌧️ Perfect Indoor Focus Weather",
                description="Rainy weather is perfect for deep work. Consider tackling your most challenging tasks.",
                action="suggest_deep_work_tasks",
                priority=7,
                context="weather"
            ))
        elif context.weather == "sunny":
            suggestions.append(SmartSuggestion(
                title="☀️ Beautiful Day Energy Boost",
                description="Sunny weather boosts mood and energy. Great time for creative or collaborative work.",
                action="suggest_creative_tasks",
                priority=6,
                context="weather"
            ))
        
        # Time-based suggestions
        if context.time_of_day == "early_morning":
            suggestions.append(SmartSuggestion(
                title="🌅 Morning Peak Performance",
                description="Early morning is prime time for your most important tasks.",
                action="suggest_high_priority_tasks",
                priority=8,
                context="time"
            ))
        elif context.time_of_day == "afternoon":
            suggestions.append(SmartSuggestion(
                title="🕐 Afternoon Energy Dip",
                description="Energy typically dips in afternoon. Consider lighter tasks or a break.",
                action="suggest_light_tasks_or_break",
                priority=5,
                context="time"
            ))
        
        # System performance suggestions
        if context.cpu_usage > 80:
            suggestions.append(SmartSuggestion(
                title="💻 High System Load",
                description="System is under heavy load. Consider closing unnecessary apps.",
                action="suggest_system_cleanup",
                priority=7,
                context="system",
                auto_apply=True
            ))
        
        # Focus mode suggestions
        if context.focus_mode:
            suggestions.append(SmartSuggestion(
                title="🎯 Focus Mode Detected",
                description="Focus mode is active. Perfect time for deep work sessions.",
                action="start_deep_work_session",
                priority=9,
                context="focus"
            ))
        
        # Calendar-based suggestions
        for event in context.calendar_events:
            event_time = datetime.datetime.fromisoformat(event['start'])
            time_until = event_time - datetime.datetime.now()
            
            if 0 < time_until.total_seconds() < 3600:  # Within next hour
                suggestions.append(SmartSuggestion(
                    title=f"📅 Upcoming: {event['title']}",
                    description=f"Meeting in {int(time_until.total_seconds()/60)} minutes. Prepare now?",
                    action="prepare_for_meeting",
                    priority=8,
                    context="calendar"
                ))
        
        # Sort by priority
        suggestions.sort(key=lambda x: x.priority, reverse=True)
        return suggestions[:5]  # Return top 5
    
    def auto_optimize_environment(self, context: EnvironmentContext) -> List[str]:
        optimizations = []
        
        # Auto-apply high-priority suggestions
        suggestions = self.generate_smart_suggestions(context)
        
        for suggestion in suggestions:
            if suggestion.auto_apply and suggestion.priority >= 8:
                result = self._apply_optimization(suggestion)
                if result:
                    optimizations.append(f"✅ {suggestion.title}: {result}")
        
        return optimizations
    
    def _apply_optimization(self, suggestion: SmartSuggestion) -> Optional[str]:
        try:
            if suggestion.action == "switch_to_low_power_tasks":
                return "Switched to low-power task recommendations"
            elif suggestion.action == "suggest_system_cleanup":
                return "Recommended system cleanup tasks"
            elif suggestion.action == "start_deep_work_session":
                return "Initiated deep work mode"
            
            return f"Applied: {suggestion.action}"
        except Exception as e:
            self.logger.error(f"Error applying optimization: {e}")
            return None
    
    def get_environment_dashboard(self) -> Dict[str, Any]:
        context = self.get_current_context()
        suggestions = self.generate_smart_suggestions(context)
        optimizations = self.auto_optimize_environment(context)
        
        return {
            "context": context,
            "suggestions": suggestions,
            "optimizations": optimizations,
            "mode": self.current_mode.value,
            "timestamp": datetime.datetime.now().isoformat()
        }


# Export for CLI integration
__all__ = ['SmartEnvironmentManager', 'EnvironmentContext', 'SmartSuggestion', 'EnvironmentMode']
