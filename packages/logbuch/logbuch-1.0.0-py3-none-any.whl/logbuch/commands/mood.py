#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/mood.py

import random


def add_mood_entry(storage, mood, notes=None):
    result = storage.add_mood_entry(mood, notes)
    
    if result:
        # Trigger gamification rewards
        try:
            from logbuch.features.gamification import GamificationEngine, display_rewards
            gamification = GamificationEngine(storage)
            
            # Create mood dict for gamification
            mood_entry = {
                'mood': mood,
                'notes': notes,
                'date': result.get('date') if isinstance(result, dict) else None
            }
            
            rewards = gamification.process_mood_entry(mood_entry)
            
            # Display rewards to user
            if rewards:
                display_rewards(rewards)
        except Exception as e:
            # Don't fail mood entry if gamification fails
            from logbuch.core.logger import get_logger
            logger = get_logger("mood")
            logger.debug(f"Gamification error: {e}")
    
    return result


def list_mood_entries(storage, limit=None, date=None):
    return storage.get_mood_entries(limit, date)


def get_random_mood():
    moods = [
        # Positive moods
        "happy", "joyful", "excited", "content", "peaceful", "grateful", 
        "optimistic", "energetic", "confident", "relaxed", "inspired", 
        "motivated", "cheerful", "blissful", "euphoric", "serene",
        
        # Neutral moods
        "calm", "focused", "balanced", "steady", "neutral", "contemplative",
        "pensive", "reflective", "curious", "alert", "observant",
        
        # Challenging moods
        "tired", "stressed", "anxious", "overwhelmed", "frustrated", 
        "sad", "melancholy", "worried", "restless", "confused", 
        "disappointed", "lonely", "irritated", "bored", "uncertain",
        
        # Complex moods
        "nostalgic", "hopeful", "determined", "ambitious", "creative",
        "adventurous", "romantic", "philosophical", "introspective",
        "empathetic", "compassionate", "proud", "humble"
    ]
    return random.choice(moods)


def get_random_moods(count=5):
    moods = [
        # Positive moods
        "happy", "joyful", "excited", "content", "peaceful", "grateful", 
        "optimistic", "energetic", "confident", "relaxed", "inspired", 
        "motivated", "cheerful", "blissful", "euphoric", "serene",
        
        # Neutral moods
        "calm", "focused", "balanced", "steady", "neutral", "contemplative",
        "pensive", "reflective", "curious", "alert", "observant",
        
        # Challenging moods
        "tired", "stressed", "anxious", "overwhelmed", "frustrated", 
        "sad", "melancholy", "worried", "restless", "confused", 
        "disappointed", "lonely", "irritated", "bored", "uncertain",
        
        # Complex moods
        "nostalgic", "hopeful", "determined", "ambitious", "creative",
        "adventurous", "romantic", "philosophical", "introspective",
        "empathetic", "compassionate", "proud", "humble"
    ]
    return random.sample(moods, min(count, len(moods)))
