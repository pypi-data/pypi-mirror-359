#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/journal.py


def add_journal_entry(storage, text, tags=None, category=None):
    result = storage.add_journal_entry(text, tags, category)
    
    if result:
        # Trigger gamification rewards
        try:
            from logbuch.features.gamification import GamificationEngine, display_rewards
            gamification = GamificationEngine(storage)
            
            # Create entry dict for gamification
            entry = {
                'text': text,
                'tags': tags or [],
                'category': category
            }
            
            rewards = gamification.process_journal_entry(entry)
            
            # Display rewards to user
            if rewards:
                display_rewards(rewards)
        except Exception as e:
            # Don't fail journal entry if gamification fails
            from logbuch.core.logger import get_logger
            logger = get_logger("journal")
            logger.debug(f"Gamification error: {e}")
    
    return result


def list_journal_entries(storage, limit=None, tag=None, category=None, date=None):
    return storage.get_journal_entries(limit, tag, category, date)


def delete_journal_entry(storage, entry_id):
    return storage.delete_journal_entry(entry_id)
