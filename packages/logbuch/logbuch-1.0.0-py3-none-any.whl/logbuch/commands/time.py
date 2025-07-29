#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/time.py

from rich.console import Console

console = Console()


def start_time_tracking(storage, task_id=None, description=None):
    return storage.start_time_tracking(task_id, description)


def stop_time_tracking(storage):
    return storage.stop_time_tracking()


def add_time_entry(storage, duration, task_id=None, description=None, date=None):
    return storage.add_time_entry(duration, task_id, description, date)


def list_time_entries(storage, limit=None, date=None, task_id=None):
    return storage.get_time_entries(limit, date, task_id)


def get_current_tracking(storage):
    return storage.get_current_tracking()


def delete_time_entry(storage, entry_id):
    return storage.delete_time_entry(entry_id)
