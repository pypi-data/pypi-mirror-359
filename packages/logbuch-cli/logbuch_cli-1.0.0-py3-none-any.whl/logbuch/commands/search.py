#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/commands/search.py

import datetime
from rich.table import Table
from rich.console import Console
from rich import print as rprint


def smart_search(storage, query, content_type='all'):
    results = {
        'tasks': [],
        'journal': [],
        'moods': [],
        'goals': []
    }
    
    query_lower = query.lower()
    
    if content_type in ['all', 'tasks']:
        tasks = storage.get_tasks()
        for task in tasks:
            if (query_lower in task['content'].lower() or 
                (task.get('tags') and any(query_lower in tag.lower() for tag in task['tags']))):
                results['tasks'].append(task)
    
    if content_type in ['all', 'journal']:
        entries = storage.get_journal_entries(limit=1000)
        for entry in entries:
            if (query_lower in entry['text'].lower() or
                (entry.get('tags') and any(query_lower in tag.lower() for tag in entry['tags']))):
                results['journal'].append(entry)
    
    if content_type in ['all', 'moods']:
        moods = storage.get_mood_entries(limit=1000)
        for mood in moods:
            if (query_lower in mood['mood'].lower() or
                (mood.get('notes') and query_lower in mood['notes'].lower())):
                results['moods'].append(mood)
    
    if content_type in ['all', 'goals']:
        goals = storage.get_goals()
        for goal in goals:
            if query_lower in goal['description'].lower():
                results['goals'].append(goal)
    
    return results


def display_search_results(results, query):
    console = Console()
    
    console.print(f"\n[bold cyan]🔍 Search Results for: '{query}'[/bold cyan]\n")
    
    total_results = sum(len(items) for items in results.values())
    if total_results == 0:
        console.print("[yellow]No results found[/yellow]")
        return
    
    # Tasks
    if results['tasks']:
        table = Table(title=f"📋 Tasks ({len(results['tasks'])})")
        table.add_column("ID", style="cyan")
        table.add_column("Content")
        table.add_column("Status")
        table.add_column("Priority")
        
        for task in results['tasks'][:10]:  # Limit to 10 results
            status = "✅" if task.get('done') else "⏳"
            table.add_row(
                task['id'],
                task['content'][:50] + ('...' if len(task['content']) > 50 else ''),
                status,
                task.get('priority', 'medium')
            )
        console.print(table)
        console.print()
    
    # Journal entries
    if results['journal']:
        table = Table(title=f"📝 Journal Entries ({len(results['journal'])})")
        table.add_column("Date", style="blue")
        table.add_column("Content")
        table.add_column("Tags")
        
        for entry in results['journal'][:10]:
            date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%m-%d")
            tags = ', '.join(entry.get('tags', [])) if entry.get('tags') else ''
            table.add_row(
                date_str,
                entry['text'][:60] + ('...' if len(entry['text']) > 60 else ''),
                tags
            )
        console.print(table)
        console.print()
    
    # Moods
    if results['moods']:
        table = Table(title=f"😊 Mood Entries ({len(results['moods'])})")
        table.add_column("Date", style="blue")
        table.add_column("Mood", style="yellow")
        table.add_column("Notes")
        
        for mood in results['moods'][:10]:
            date_obj = datetime.datetime.fromisoformat(mood["date"].replace("Z", "+00:00"))
            date_str = date_obj.strftime("%m-%d")
            table.add_row(
                date_str,
                mood['mood'],
                mood.get('notes', '')[:40] + ('...' if mood.get('notes', '') and len(mood['notes']) > 40 else '')
            )
        console.print(table)
        console.print()
    
    # Goals
    if results['goals']:
        table = Table(title=f"🎯 Goals ({len(results['goals'])})")
        table.add_column("ID", style="cyan")
        table.add_column("Description")
        table.add_column("Progress")
        table.add_column("Status")
        
        for goal in results['goals'][:10]:
            status = "✅" if goal.get('completed') else "⏳"
            table.add_row(
                goal['id'],
                goal['description'][:50] + ('...' if len(goal['description']) > 50 else ''),
                f"{goal.get('progress', 0)}%",
                status
            )
        console.print(table)
    
    if total_results > 40:
        console.print(f"[dim]... and {total_results - 40} more results[/dim]")


def filter_by_date_range(storage, start_date, end_date, content_type='all'):
    results = {
        'tasks': [],
        'journal': [],
        'moods': [],
        'sleep': []
    }
    
    try:
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        rprint("[red]Invalid date format. Use YYYY-MM-DD[/red]")
        return results
    
    if content_type in ['all', 'tasks']:
        tasks = storage.get_tasks()
        for task in tasks:
            if task.get('created_at'):
                task_date = datetime.datetime.fromisoformat(task['created_at'].split('T')[0]).date()
                if start <= task_date <= end:
                    results['tasks'].append(task)
    
    if content_type in ['all', 'journal']:
        entries = storage.get_journal_entries(limit=1000)
        for entry in entries:
            entry_date = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00')).date()
            if start <= entry_date <= end:
                results['journal'].append(entry)
    
    if content_type in ['all', 'moods']:
        moods = storage.get_mood_entries(limit=1000)
        for mood in moods:
            mood_date = datetime.datetime.fromisoformat(mood['date'].replace('Z', '+00:00')).date()
            if start <= mood_date <= end:
                results['moods'].append(mood)
    
    if content_type in ['all', 'sleep']:
        sleep_entries = storage.get_sleep_entries(limit=1000)
        for entry in sleep_entries:
            sleep_date = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00')).date()
            if start <= sleep_date <= end:
                results['sleep'].append(entry)
    
    return results


def get_popular_tags(storage, content_type='all', limit=10):
    tag_counts = {}
    
    if content_type in ['all', 'tasks']:
        tasks = storage.get_tasks()
        for task in tasks:
            if task.get('tags'):
                for tag in task['tags']:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    if content_type in ['all', 'journal']:
        entries = storage.get_journal_entries(limit=1000)
        for entry in entries:
            if entry.get('tags'):
                for tag in entry['tags']:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Sort by count and return top tags
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags[:limit]
