#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/task.py


def add_task(
    storage, content, priority=None, tags=None, due_date=None, board="default"
):
    return storage.add_task(content, priority, tags, due_date, board)


def list_tasks(storage, show_completed=False, board=None, priority=None, tag=None):
    return storage.get_tasks(show_completed, board, priority, tag)


def complete_task(storage, task_id):
    # Get task details before completing
    tasks = storage.get_tasks(show_completed=False)
    task = None
    for t in tasks:
        if str(t.get('id')) == str(task_id):
            task = t
            break
    
    if not task:
        return False
    
    # Complete the task
    result = storage.complete_task(task_id)
    
    if result:
        # Trigger gamification rewards
        try:
            from logbuch.features.gamification import GamificationEngine, display_rewards
            gamification = GamificationEngine(storage)
            rewards = gamification.process_task_completion(task)
            
            # Display rewards to user
            if rewards:
                display_rewards(rewards)
        except Exception as e:
            # Don't fail task completion if gamification fails
            from logbuch.core.logger import get_logger
            logger = get_logger("task")
            logger.debug(f"Gamification error: {e}")
    
    return result


def delete_task(storage, task_id):
    return storage.delete_task(task_id)


def move_task(storage, task_id, board):
    return storage.move_task(task_id, board)
