#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/sleep.py


def add_sleep_entry(storage, hours, notes=None):
    return storage.add_sleep_entry(hours, notes)


def list_sleep_entries(storage, limit=None, date=None):
    return storage.get_sleep_entries(limit, date)
