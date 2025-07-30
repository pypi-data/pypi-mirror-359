#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/goal.py


def add_goal(storage, description, target_date):
    return storage.add_goal(description, target_date)


def update_goal_progress(storage, goal_id, progress):
    return storage.update_goal_progress(goal_id, progress)


def list_goals(storage, include_completed=False):
    return storage.get_goals(include_completed)


def delete_goal(storage, goal_id):
    return storage.delete_goal(goal_id)
