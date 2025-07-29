#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

import re
from typing import Optional, Dict, List, Tuple
from enum import Enum

class PriorityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class PriorityHandler:
    def __init__(self):
        # Priority mappings for flexible input
        self.priority_mappings = {
            # Standard priorities
            'low': PriorityLevel.LOW,
            'medium': PriorityLevel.MEDIUM,
            'med': PriorityLevel.MEDIUM,
            'high': PriorityLevel.HIGH,
            'urgent': PriorityLevel.URGENT,
            'critical': PriorityLevel.CRITICAL,
            'crit': PriorityLevel.CRITICAL,
            
            # Numeric priorities (1-5 scale)
            '1': PriorityLevel.LOW,
            '2': PriorityLevel.MEDIUM,
            '3': PriorityLevel.HIGH,
            '4': PriorityLevel.URGENT,
            '5': PriorityLevel.CRITICAL,
            
            # Alternative names
            'normal': PriorityLevel.MEDIUM,
            'important': PriorityLevel.HIGH,
            'asap': PriorityLevel.URGENT,
            'emergency': PriorityLevel.CRITICAL,
            'emerg': PriorityLevel.CRITICAL,
            
            # Emoji-based (fun!)
            '🔥': PriorityLevel.URGENT,
            '💥': PriorityLevel.CRITICAL,
            '⚡': PriorityLevel.HIGH,
            '📌': PriorityLevel.MEDIUM,
            '💤': PriorityLevel.LOW,
            
            # Casual language
            'meh': PriorityLevel.LOW,
            'whatever': PriorityLevel.LOW,
            'soon': PriorityLevel.MEDIUM,
            'now': PriorityLevel.HIGH,
            'yesterday': PriorityLevel.URGENT,
            'omg': PriorityLevel.CRITICAL,
            
            # Single letters
            'l': PriorityLevel.LOW,
            'm': PriorityLevel.MEDIUM,
            'h': PriorityLevel.HIGH,
            'u': PriorityLevel.URGENT,
            'c': PriorityLevel.CRITICAL,
        }
        
        # Priority colors for display
        self.priority_colors = {
            PriorityLevel.LOW: 'dim',
            PriorityLevel.MEDIUM: 'bright_blue',
            PriorityLevel.HIGH: 'bright_yellow',
            PriorityLevel.URGENT: 'bright_red',
            PriorityLevel.CRITICAL: 'bold red'
        }
        
        # Priority emojis
        self.priority_emojis = {
            PriorityLevel.LOW: '📌',
            PriorityLevel.MEDIUM: '⚡',
            PriorityLevel.HIGH: '🔥',
            PriorityLevel.URGENT: '💥',
            PriorityLevel.CRITICAL: '🚨'
        }
    
    def parse_priority(self, priority_input: str) -> Optional[PriorityLevel]:
        if not priority_input:
            return None
        
        # Normalize input
        normalized = priority_input.lower().strip()
        
        # Direct mapping
        if normalized in self.priority_mappings:
            return self.priority_mappings[normalized]
        
        # Pattern matching for more complex inputs
        patterns = [
            # "very high", "super urgent", etc.
            (r'(very|super|extremely?)\s*(high|urgent|important)', PriorityLevel.CRITICAL),
            (r'(kind of|sort of|somewhat)\s*(high|urgent|important)', PriorityLevel.HIGH),
            (r'(not very|not really)\s*(urgent|important)', PriorityLevel.MEDIUM),
            
            # "high priority", "urgent task", etc.
            (r'(high|urgent|critical)\s*(priority|task|item)', PriorityLevel.HIGH),
            (r'(low|normal)\s*(priority|task|item)', PriorityLevel.LOW),
            
            # Time-based priorities
            (r'(today|asap|now)', PriorityLevel.URGENT),
            (r'(this week|soon)', PriorityLevel.HIGH),
            (r'(next week|later)', PriorityLevel.MEDIUM),
            (r'(someday|eventually)', PriorityLevel.LOW),
        ]
        
        for pattern, priority_level in patterns:
            if re.search(pattern, normalized):
                return priority_level
        
        # If no match found, return None (will trigger suggestion)
        return None
    
    def normalize_priority(self, priority_input: str) -> Tuple[Optional[str], List[str]]:
        parsed = self.parse_priority(priority_input)
        
        if parsed:
            return parsed.value, []
        
        # Generate suggestions for invalid input
        suggestions = self.get_priority_suggestions(priority_input)
        
        return None, suggestions
    
    def get_priority_suggestions(self, invalid_input: str) -> List[str]:
        suggestions = []
        normalized = invalid_input.lower().strip()
        
        # Find close matches
        close_matches = []
        for key in self.priority_mappings.keys():
            if self.is_similar(normalized, key):
                close_matches.append(key)
        
        if close_matches:
            suggestions.extend([f"Did you mean '{match}'?" for match in close_matches[:3]])
        
        # Always include standard options
        suggestions.extend([
            "Standard priorities: low, medium, high, urgent, critical",
            "Numbers work too: 1 (low) to 5 (critical)",
            "Try: 'asap', 'soon', 'later', or even emojis like 🔥"
        ])
        
        return suggestions
    
    def is_similar(self, input_str: str, target: str) -> bool:
        # Check if input is contained in target or vice versa
        if input_str in target or target in input_str:
            return True
        
        # Check for common typos/abbreviations
        if len(input_str) >= 2 and len(target) >= 2:
            if input_str[:2] == target[:2]:  # Same first 2 letters
                return True
        
        return False
    
    def get_priority_display(self, priority: str) -> str:
        try:
            priority_level = PriorityLevel(priority)
            emoji = self.priority_emojis[priority_level]
            color = self.priority_colors[priority_level]
            
            return f"[{color}]{emoji} {priority.upper()}[/{color}]"
        except (ValueError, KeyError):
            return f"📌 {priority.upper()}"
    
    def get_all_valid_priorities(self) -> List[str]:
        return list(self.priority_mappings.keys())
    
    def get_priority_help(self) -> str:
        help_text = """
🎯 **Priority Options** (very flexible!):

**Standard**: low, medium, high, urgent, critical
**Numbers**: 1-5 (1=low, 5=critical)  
**Short**: l, m, h, u, c
**Casual**: meh, soon, now, asap, omg
**Emojis**: 💤 📌 ⚡ 🔥 💥
**Time**: today, this week, later, someday

**Examples**:
• `logbuch t "Fix bug" --priority 🔥`
• `logbuch t "Review code" --priority asap`
• `logbuch t "Clean desk" --priority meh`
• `logbuch t "Deploy app" --priority 5`
"""
        return help_text.strip()


# Global priority handler instance
priority_handler = PriorityHandler()


def validate_and_normalize_priority(priority_input: str) -> Tuple[Optional[str], List[str]]:
    return priority_handler.normalize_priority(priority_input)


def get_priority_display(priority: str) -> str:
    return priority_handler.get_priority_display(priority)


def get_priority_help() -> str:
    return priority_handler.get_priority_help()


# Export priority utilities
__all__ = [
    'PriorityLevel',
    'PriorityHandler', 
    'priority_handler',
    'validate_and_normalize_priority',
    'get_priority_display',
    'get_priority_help'
]
