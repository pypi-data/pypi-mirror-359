#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/utils/date_parser.py

import datetime
import re
from typing import Optional, Union


def parse_short_date(date_input: str) -> Optional[str]:
    if not date_input:
        return None
    
    # Check if it's already in YYYY-MM-DD format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
        return date_input
    
    # Parse DD:MM format
    dd_mm_pattern = r'^(\d{1,2}):(\d{1,2})$'
    match = re.match(dd_mm_pattern, date_input)
    
    if not match:
        return None
    
    try:
        day = int(match.group(1))
        month = int(match.group(2))
        
        # Validate day and month ranges
        if not (1 <= day <= 31):
            return None
        if not (1 <= month <= 12):
            return None
        
        # Use current year
        current_year = datetime.datetime.now().year
        
        # Create date object to validate (handles leap years, month lengths, etc.)
        try:
            date_obj = datetime.date(current_year, month, day)
        except ValueError:
            # Invalid date (e.g., Feb 30, Apr 31)
            return None
        
        # Return in ISO format
        return date_obj.strftime("%Y-%m-%d")
        
    except (ValueError, AttributeError):
        return None


def format_date_for_display(iso_date: str, format_type: str = "short") -> str:
    if not iso_date:
        return ""
    
    try:
        # Handle datetime strings by taking just the date part
        date_part = iso_date.split('T')[0]
        date_obj = datetime.datetime.strptime(date_part, "%Y-%m-%d")
        
        if format_type == "short":
            return date_obj.strftime("%d:%m")
        elif format_type == "display":
            return date_obj.strftime("%d-%m")
        else:
            return date_obj.strftime("%Y-%m-%d")
            
    except (ValueError, AttributeError):
        return iso_date


def parse_natural_date(date_input: str) -> str:
    if not date_input:
        return ""
    
    date_input = date_input.strip().lower()
    today = datetime.date.today()
    
    # Handle DD:MM format first
    short_date = parse_short_date(date_input)
    if short_date:
        return short_date
    
    # Handle natural language dates
    if date_input in ["today", "now"]:
        return today.strftime("%Y-%m-%d")
    
    elif date_input in ["tomorrow", "tmr"]:
        tomorrow = today + datetime.timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    
    elif date_input in ["yesterday", "yday"]:
        yesterday = today - datetime.timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")
    
    elif "next week" in date_input:
        next_week = today + datetime.timedelta(weeks=1)
        return next_week.strftime("%Y-%m-%d")
    
    elif "next month" in date_input:
        # Add approximately 30 days
        next_month = today + datetime.timedelta(days=30)
        return next_month.strftime("%Y-%m-%d")
    
    elif date_input.startswith("in "):
        # Handle "in 3 days", "in 2 weeks", etc.
        parts = date_input.split()
        if len(parts) >= 3:
            try:
                number = int(parts[1])
                unit = parts[2].lower()
                
                if unit.startswith("day"):
                    target_date = today + datetime.timedelta(days=number)
                elif unit.startswith("week"):
                    target_date = today + datetime.timedelta(weeks=number)
                elif unit.startswith("month"):
                    target_date = today + datetime.timedelta(days=number * 30)
                else:
                    return date_input  # Return original if can't parse
                
                return target_date.strftime("%Y-%m-%d")
            except ValueError:
                pass
    
    # If it's already in YYYY-MM-DD format, return as-is
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
        return date_input
    
    # Return original input if we can't parse it
    return date_input


def validate_date_input(date_input: str) -> tuple[bool, str]:
    if not date_input:
        return True, ""
    
    # Try to parse as DD:MM
    parsed = parse_short_date(date_input)
    if parsed:
        return True, ""
    
    # Try natural language parsing
    parsed_natural = parse_natural_date(date_input)
    if parsed_natural != date_input and re.match(r'^\d{4}-\d{2}-\d{2}$', parsed_natural):
        return True, ""
    
    # Check if it's already valid ISO format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
        try:
            datetime.datetime.strptime(date_input, "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, "Invalid date"
    
    return False, "Use DD:MM format (e.g., 25:12 for Dec 25) or natural language (tomorrow, next week)"


def get_date_examples() -> list[str]:
    return [
        "25:12 (December 25th)",
        "05:03 (March 5th)", 
        "tomorrow",
        "next week",
        "in 3 days",
        "2024-12-25"
    ]


# Utility functions for CLI help text
def get_date_help_text() -> str:
    examples = get_date_examples()
    return f"Date format: DD:MM or natural language. Examples: {', '.join(examples[:3])}"


def convert_legacy_date_format(old_format: str) -> str:
    if not old_format:
        return ""
    
    try:
        # If it's in YYYY-MM-DD format, convert to DD:MM
        if re.match(r'^\d{4}-\d{2}-\d{2}', old_format):
            date_obj = datetime.datetime.strptime(old_format.split('T')[0], "%Y-%m-%d")
            return date_obj.strftime("%d:%m")
    except ValueError:
        pass
    
    return old_format


# For backward compatibility
def parse_date(date_input: str) -> str:
    return parse_natural_date(date_input)
