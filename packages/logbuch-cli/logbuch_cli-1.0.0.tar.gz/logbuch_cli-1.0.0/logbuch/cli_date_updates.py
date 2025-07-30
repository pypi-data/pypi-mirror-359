#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/cli_date_updates.py

import click
import datetime
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from logbuch.storage import Storage
from logbuch.utils.date_parser import (
    parse_short_date, 
    format_date_for_display, 
    parse_natural_date,
    validate_date_input,
    get_date_help_text
)

console = Console()


# Updated task command with DD:MM support
@click.command("task", short_help="Manage tasks [t]")
@click.argument("content", required=False)
@click.option("-v", "--view", is_flag=True, help="View all tasks")
@click.option("-a", "--all", is_flag=True, help="Show all tasks including completed")
@click.option("-c", "--complete", help="Complete a task by ID")
@click.option("-d", "--delete", help="Delete a task by ID")
@click.option("-m", "--move", help="Move task to different board (format: task_id:board_name)")
@click.option("-t", "--tags", help="Comma-separated list of tags")
@click.option("-d", "--due", help="Due date in DD:MM format (e.g., 25:12 for Dec 25)")
@click.option("-p", "--priority", help="Priority (low, medium, high)")
@click.option("-b", "--board", help='Board name (default: "default")')
def task_command_updated(content, view, all, complete, delete, move, tags, due, priority, board):
    storage = Storage()
    
    if complete:
        # Complete task logic remains the same
        from logbuch.commands.task import complete_task
        result = complete_task(storage, complete)
        if result:
            rprint(f"[green]✅ Task {complete} completed![/green]")
        else:
            rprint(f"[red]❌ Task {complete} not found[/red]")
        return
    
    if delete:
        # Delete task logic remains the same
        from logbuch.commands.task import delete_task
        result = delete_task(storage, delete)
        if result:
            rprint(f"[green]🗑️ Task {delete} deleted![/green]")
        else:
            rprint(f"[red]❌ Task {delete} not found[/red]")
        return
    
    if move:
        # Move task logic remains the same
        if ":" in move:
            task_id, new_board = move.split(":", 1)
            from logbuch.commands.task import move_task
            result = move_task(storage, task_id, new_board)
            if result:
                rprint(f"[green]📋 Task {task_id} moved to {new_board}![/green]")
            else:
                rprint(f"[red]❌ Task {task_id} not found[/red]")
        else:
            rprint("[red]❌ Move format: task_id:board_name[/red]")
        return
    
    if view or all or not content:
        # Display tasks with updated date formatting
        from logbuch.commands.task import list_tasks
        tasks = list_tasks(storage, show_completed=all)
        
        if not tasks:
            rprint("[yellow]No tasks found[/yellow]")
            return
        
        table = Table(title="Tasks")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Content")
        table.add_column("Tags", style="magenta")
        table.add_column("Priority")
        table.add_column("Status")
        table.add_column("Due Date", style="yellow")
        
        for task in tasks:
            status = "[green]✓[/green]" if task.get("completed") else "☐"
            
            # Format due date using new DD:MM format
            due_date = task.get("due_date", "")
            if due_date:
                formatted_due = format_date_for_display(due_date, "short")  # Returns DD:MM
                # Add visual indicators for urgency
                try:
                    date_obj = datetime.datetime.strptime(due_date.split('T')[0], "%Y-%m-%d")
                    today = datetime.date.today()
                    days_until = (date_obj.date() - today).days
                    
                    if days_until < 0:
                        formatted_due = f"[red]{formatted_due} (overdue)[/red]"
                    elif days_until == 0:
                        formatted_due = f"[yellow]{formatted_due} (today)[/yellow]"
                    elif days_until == 1:
                        formatted_due = f"[orange1]{formatted_due} (tomorrow)[/orange1]"
                    else:
                        formatted_due = f"[green]{formatted_due}[/green]"
                except (ValueError, TypeError):
                    formatted_due = due_date
            else:
                formatted_due = ""
            
            table.add_row(
                str(task["id"]),
                task["content"],
                ", ".join(task.get("tags", [])),
                task.get("priority", "medium"),
                status,
                formatted_due,
            )
        
        console.print(table)
        
        if not all and len(tasks) >= 20:
            rprint(f"[dim]Showing recent tasks. Use --all to see all tasks.[/dim]")
    
    elif content:
        # Add new task with DD:MM date parsing
        if len(content.strip()) == 0:
            rprint("[red]❌ Task content cannot be empty[/red]")
            return
        
        # Parse and validate due date
        parsed_due = None
        if due:
            is_valid, error_msg = validate_date_input(due)
            if not is_valid:
                rprint(f"[red]❌ Invalid date format: {error_msg}[/red]")
                rprint(f"[yellow]💡 {get_date_help_text()}[/yellow]")
                return
            
            parsed_due = parse_natural_date(due)
            if parsed_due != due:
                # Show what we interpreted
                display_date = format_date_for_display(parsed_due, "short")
                rprint(f"[cyan]📅 Interpreted '{due}' as {display_date}[/cyan]")
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Add the task
        from logbuch.commands.task import add_task
        task_id = add_task(
            storage, 
            content, 
            priority=priority, 
            tags=tag_list, 
            due_date=parsed_due, 
            board=board or "default"
        )
        
        if task_id:
            rprint(f"[green]✅ Task added: {content}[/green]")
            if parsed_due:
                display_date = format_date_for_display(parsed_due, "short")
                rprint(f"[cyan]📅 Due: {display_date}[/cyan]")
        else:
            rprint("[red]❌ Failed to add task[/red]")


# Updated goal command with DD:MM support
@click.command("goal", short_help="Manage goals [g]")
@click.argument("description", required=False)
@click.option("-v", "--view", is_flag=True, help="View all goals")
@click.option("-a", "--all", is_flag=True, help="Include completed goals when viewing")
@click.option("-d", "--due", help="Target date in DD:MM format (e.g., 31:12 for Dec 31)")
@click.option("-p", "--progress", help="Update progress (0-100) for a goal ID")
@click.option("-g", "--goal-id", help="Goal ID for updating progress")
@click.option("-r", "--remove", help="Delete a goal by ID")
def goal_command_updated(description, view, all, due, progress, goal_id, remove):
    storage = Storage()
    
    if remove:
        # Delete goal logic
        from logbuch.commands.goal import delete_goal
        result = delete_goal(storage, remove)
        if result:
            rprint(f"[green]🗑️ Goal {remove} deleted![/green]")
        else:
            rprint(f"[red]❌ Goal {remove} not found[/red]")
        return
    
    if progress and goal_id:
        # Update progress logic
        try:
            progress_val = int(progress)
            if 0 <= progress_val <= 100:
                from logbuch.commands.goal import update_goal_progress
                goal = update_goal_progress(storage, goal_id, progress_val)
                if goal:
                    status = "completed" if goal["completed"] else "in progress"
                    rprint(f"[green]Goal progress updated: {goal['description']} ({progress_val}% {status})[/green]")
                else:
                    rprint(f"[red]❌ Goal {goal_id} not found[/red]")
            else:
                rprint("[red]❌ Progress must be between 0 and 100[/red]")
        except ValueError:
            rprint("[red]❌ Progress must be a number[/red]")
        return
    
    if view or all or not description:
        # Display goals with updated date formatting
        from logbuch.commands.goal import list_goals
        goals = list_goals(storage, show_completed=all)
        
        if not goals:
            rprint("[yellow]No goals found[/yellow]")
            return
        
        table = Table(title="Goals")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Description")
        table.add_column("Progress")
        table.add_column("Target Date", style="yellow")
        table.add_column("Status")
        
        for goal in goals:
            status = "Completed" if goal["completed"] else "In Progress"
            
            # Format target date using DD:MM format
            target_date = goal.get("target_date", "")
            if target_date:
                formatted_date = format_date_for_display(target_date, "short")
                
                # Add visual indicators for deadlines
                try:
                    date_obj = datetime.datetime.strptime(target_date.split('T')[0], "%Y-%m-%d")
                    today = datetime.date.today()
                    days_until = (date_obj.date() - today).days
                    
                    if days_until < 0:
                        formatted_date = f"[red]{formatted_date} (overdue)[/red]"
                    elif days_until <= 7:
                        formatted_date = f"[yellow]{formatted_date} (soon)[/yellow]"
                    else:
                        formatted_date = f"[green]{formatted_date}[/green]"
                except (ValueError, TypeError):
                    formatted_date = target_date
            else:
                formatted_date = ""
            
            table.add_row(
                str(goal["id"]),
                goal["description"],
                f"{goal['progress']}%",
                formatted_date,
                status,
            )
        
        console.print(table)
    
    elif description and due:
        # Add new goal with DD:MM date parsing
        is_valid, error_msg = validate_date_input(due)
        if not is_valid:
            rprint(f"[red]❌ Invalid date format: {error_msg}[/red]")
            rprint(f"[yellow]💡 {get_date_help_text()}[/yellow]")
            return
        
        parsed_due = parse_natural_date(due)
        if parsed_due != due:
            # Show what we interpreted
            display_date = format_date_for_display(parsed_due, "short")
            rprint(f"[cyan]📅 Interpreted '{due}' as {display_date}[/cyan]")
        
        from logbuch.commands.goal import add_goal
        goal = add_goal(storage, description, parsed_due)
        if goal:
            rprint(f"[green]🎯 Goal added: {description}[/green]")
            display_date = format_date_for_display(parsed_due, "short")
            rprint(f"[cyan]📅 Target: {display_date}[/cyan]")
        else:
            rprint("[red]❌ Failed to add goal[/red]")
    
    else:
        rprint("[yellow]💡 Target date required when adding a goal.[/yellow]")
        rprint(f"[yellow]💡 {get_date_help_text()}[/yellow]")


# Updated mood command with DD:MM date filtering
@click.command("mood", short_help="Track your mood [m]")
@click.argument("mood", required=False)
@click.option("-v", "--view", is_flag=True, help="View mood history")
@click.option("-n", "--notes", help="Add notes about your mood")
@click.option("-l", "--limit", type=int, default=10, help="Limit number of entries shown")
@click.option("-d", "--date", help="Filter by date in DD:MM format")
@click.option("-r", "--random", is_flag=True, help="Get a random mood suggestion")
@click.option("--random-list", type=int, help="Get multiple random mood suggestions")
def mood_command_updated(mood, view, notes, limit, date, random, random_list):
    storage = Storage()
    
    if random:
        from logbuch.commands.mood import get_random_mood
        suggested_mood = get_random_mood()
        rprint(f"[cyan]💭 Mood suggestion: {suggested_mood}[/cyan]")
        rprint("[dim]Use any mood with: logbuch mood <mood_name>[/dim]")
        return
    
    if random_list:
        from logbuch.commands.mood import get_random_moods
        suggested_moods = get_random_moods(random_list)
        rprint(f"[cyan]💭 Mood suggestions:[/cyan]")
        for i, suggested_mood in enumerate(suggested_moods, 1):
            rprint(f"  {i}. {suggested_mood}")
        rprint("[dim]Use any mood with: logbuch mood <mood_name>[/dim]")
        return
    
    if view or not mood:
        # Parse date filter if provided
        date_filter = None
        if date:
            is_valid, error_msg = validate_date_input(date)
            if not is_valid:
                rprint(f"[red]❌ Invalid date format: {error_msg}[/red]")
                return
            date_filter = parse_natural_date(date)
        
        from logbuch.commands.mood import list_mood_entries
        entries = list_mood_entries(storage, limit, date_filter)
        
        if not entries:
            rprint("[yellow]No mood entries found[/yellow]")
            return
        
        table = Table(title="Mood History")
        table.add_column("Date", style="blue")
        table.add_column("Time", style="cyan")
        table.add_column("Mood")
        table.add_column("Notes")
        
        for entry in entries:
            try:
                date_obj = datetime.datetime.fromisoformat(entry["date"].replace("Z", "+00:00"))
                date_str = date_obj.strftime("%d:%m")  # DD:MM format
                time_str = date_obj.strftime("%H:%M")
                table.add_row(date_str, time_str, entry["mood"], entry.get("notes", ""))
            except (ValueError, TypeError):
                # Fallback for parsing issues
                date_parts = entry["date"].split("T")
                date_str = date_parts[0]
                time_str = date_parts[1].split(".")[0][:5] if len(date_parts) > 1 else ""
                table.add_row(date_str, time_str, entry["mood"], entry.get("notes", ""))
        
        console.print(table)
    
    elif mood:
        # Add mood entry
        from logbuch.commands.mood import add_mood_entry
        entry_id = add_mood_entry(storage, mood, notes)
        if entry_id:
            rprint(f"[green]😊 Mood logged: {mood}[/green]")
            if notes:
                rprint(f"[dim]Notes: {notes}[/dim]")
        else:
            rprint("[red]❌ Failed to log mood[/red]")


def update_cli_help_text():
    help_updates = {
        "task_due_help": "Due date in DD:MM format (e.g., 25:12 for Dec 25) or natural language",
        "goal_due_help": "Target date in DD:MM format (e.g., 31:12 for Dec 31) or natural language", 
        "date_filter_help": "Filter by date in DD:MM format or natural language",
        "examples": [
            "25:12 (December 25th)",
            "05:03 (March 5th)",
            "tomorrow",
            "next week"
        ]
    }
    return help_updates


# Configuration update function
def update_date_format_config():
    storage = Storage()
    
    # Update the default date format
    try:
        # Set new date format
        storage.set_config('dateFormat', '%d:%m')
        rprint("[green]✅ Date format updated to DD:MM[/green]")
        rprint("[cyan]💡 You can now use dates like: 25:12, 05:03, tomorrow, next week[/cyan]")
        
        # Show examples
        from logbuch.utils.date_parser import get_date_examples
        examples = get_date_examples()
        rprint("[yellow]📅 Date format examples:[/yellow]")
        for example in examples:
            rprint(f"  • {example}")
            
    except Exception as e:
        rprint(f"[red]❌ Failed to update date format: {e}[/red]")


if __name__ == "__main__":
    # Demo the new date parsing
    from logbuch.utils.date_parser import parse_short_date, format_date_for_display
    
    test_dates = ["25:12", "05:03", "31:01", "29:02", "invalid"]
    
    print("🧪 Testing DD:MM date parsing:")
    for test_date in test_dates:
        parsed = parse_short_date(test_date)
        if parsed:
            display = format_date_for_display(parsed, "short")
            print(f"  {test_date} → {parsed} → {display}")
        else:
            print(f"  {test_date} → Invalid")
