#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on 2025-06-30, 09:09.
# Last modified: Jun.
# Copyright (c) 2025. All rights reserved.

# logbuch/features/visual_dashboard.py

import time
import datetime
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

try:
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
    from rich.table import Table
    from rich.console import Console, Group
    from rich.align import Align
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from logbuch.core.logger import get_logger
from logbuch.core.config import get_config


@dataclass
class DashboardMetrics:
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    overdue_tasks: int
    due_today: int
    high_priority: int
    recent_journal_entries: int
    mood_trend: str
    productivity_score: float
    streak_days: int


class VisualDashboard:
    def __init__(self, storage):
        self.storage = storage
        self.logger = get_logger("visual_dashboard")
        self.config = get_config()
        self.console = Console()
        
        # Dashboard state
        self.is_running = False
        self.refresh_interval = 2.0  # seconds
        self.last_update = 0
        
        # Visual elements
        self.layout = Layout()
        self.setup_layout()
        
        # Animations
        self.animation_frame = 0
        self.sparkline_data = []
        
        self.logger.debug("Visual Dashboard initialized")
    
    def setup_layout(self):
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        self.layout["left"].split_column(
            Layout(name="stats", size=8),
            Layout(name="tasks", ratio=1),
            Layout(name="timeline", size=6)
        )
        
        self.layout["right"].split_column(
            Layout(name="mood", size=8),
            Layout(name="goals", size=8),
            Layout(name="insights", ratio=1)
        )
    
    def get_metrics(self) -> DashboardMetrics:
        tasks = self.storage.get_tasks()
        journal_entries = self.storage.get_journal_entries(limit=7)
        mood_entries = self.storage.get_mood_entries(limit=7)
        goals = self.storage.get_goals()
        
        # Task metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('done')])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Due date analysis
        today = datetime.date.today()
        overdue_tasks = 0
        due_today = 0
        
        for task in tasks:
            if not task.get('done') and task.get('due_date'):
                try:
                    due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                    if due_date < today:
                        overdue_tasks += 1
                    elif due_date == today:
                        due_today += 1
                except:
                    continue
        
        # Priority analysis
        high_priority = len([t for t in tasks if not t.get('done') and t.get('priority') == 'high'])
        
        # Mood trend
        mood_trend = self._analyze_mood_trend(mood_entries)
        
        # Productivity score (0-100)
        productivity_score = self._calculate_productivity_score(tasks, journal_entries, mood_entries)
        
        # Streak calculation
        streak_days = self._calculate_streak(journal_entries, mood_entries)
        
        return DashboardMetrics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            completion_rate=completion_rate,
            overdue_tasks=overdue_tasks,
            due_today=due_today,
            high_priority=high_priority,
            recent_journal_entries=len(journal_entries),
            mood_trend=mood_trend,
            productivity_score=productivity_score,
            streak_days=streak_days
        )
    
    def create_header(self) -> Panel:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        
        # Animated title with sparkles
        sparkles = "✨" if self.animation_frame % 4 < 2 else "🌟"
        title = f"{sparkles} Logbuch Visual Dashboard {sparkles}"
        
        header_text = Text()
        header_text.append(title, style="bold cyan")
        header_text.append(f"\n{current_date} • {current_time}", style="dim white")
        
        return Panel(
            Align.center(header_text),
            box=box.DOUBLE,
            style="bright_blue"
        )
    
    def create_stats_panel(self, metrics: DashboardMetrics) -> Panel:
        # Completion rate progress bar
        completion_bar = self._create_progress_bar(
            metrics.completion_rate, 
            100, 
            "Completion Rate",
            "green" if metrics.completion_rate > 70 else "yellow" if metrics.completion_rate > 40 else "red"
        )
        
        # Productivity score with sparkline
        productivity_bar = self._create_progress_bar(
            metrics.productivity_score,
            100,
            "Productivity Score",
            "bright_green" if metrics.productivity_score > 80 else "yellow" if metrics.productivity_score > 60 else "orange"
        )
        
        # Stats table
        stats_table = Table(show_header=False, box=None, padding=(0, 1))
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="bright_white")
        stats_table.add_column("Indicator", style="green")
        
        stats_table.add_row("📋 Total Tasks", str(metrics.total_tasks), "📊")
        stats_table.add_row("✅ Completed", str(metrics.completed_tasks), "🎯")
        stats_table.add_row("🔥 High Priority", str(metrics.high_priority), "⚡" if metrics.high_priority > 0 else "✨")
        stats_table.add_row("⏰ Due Today", str(metrics.due_today), "🚨" if metrics.due_today > 0 else "✅")
        stats_table.add_row("⚠️ Overdue", str(metrics.overdue_tasks), "🔴" if metrics.overdue_tasks > 0 else "🟢")
        stats_table.add_row("🔥 Streak Days", str(metrics.streak_days), "🏆" if metrics.streak_days > 7 else "💪")
        
        content = Group(
            completion_bar,
            productivity_bar,
            "",
            stats_table
        )
        
        return Panel(
            content,
            title="📊 Live Statistics",
            border_style="bright_green"
        )
    
    def create_tasks_panel(self, metrics: DashboardMetrics) -> Panel:
        tasks = self.storage.get_tasks()
        incomplete_tasks = [t for t in tasks if not t.get('done')][:8]  # Show top 8
        
        if not incomplete_tasks:
            return Panel(
                Align.center("🎉 All tasks completed!\nYou're amazing! 🌟"),
                title="📋 Active Tasks",
                border_style="green"
            )
        
        tasks_table = Table(show_header=True, box=box.SIMPLE)
        tasks_table.add_column("Priority", width=8)
        tasks_table.add_column("Task", ratio=1)
        tasks_table.add_column("Due", width=10)
        
        for task in incomplete_tasks:
            # Priority with emoji
            priority = task.get('priority', 'medium')
            priority_display = {
                'high': '🔥 HIGH',
                'medium': '⚡ MED',
                'low': '💡 LOW'
            }.get(priority, '📝 MED')
            
            # Task content (truncated)
            content = task['content'][:40] + ('...' if len(task['content']) > 40 else '')
            
            # Due date
            due_display = ""
            if task.get('due_date'):
                try:
                    due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                    today = datetime.date.today()
                    
                    if due_date == today:
                        due_display = "🔥 TODAY"
                    elif due_date < today:
                        due_display = "⚠️ OVERDUE"
                    else:
                        due_display = due_date.strftime("%m-%d")
                except:
                    due_display = ""
            
            tasks_table.add_row(priority_display, content, due_display)
        
        return Panel(
            tasks_table,
            title=f"📋 Active Tasks ({len(incomplete_tasks)})",
            border_style="yellow"
        )
    
    def create_timeline_panel(self) -> Panel:
        # Get recent activity
        journal_entries = self.storage.get_journal_entries(limit=3)
        mood_entries = self.storage.get_mood_entries(limit=3)
        
        timeline_items = []
        
        # Add journal entries
        for entry in journal_entries:
            date_obj = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
            time_str = date_obj.strftime("%H:%M")
            preview = entry['text'][:30] + ('...' if len(entry['text']) > 30 else '')
            timeline_items.append((date_obj, f"📝 {time_str} Journal: {preview}"))
        
        # Add mood entries
        for mood in mood_entries:
            date_obj = datetime.datetime.fromisoformat(mood['date'].replace('Z', '+00:00'))
            time_str = date_obj.strftime("%H:%M")
            timeline_items.append((date_obj, f"😊 {time_str} Mood: {mood['mood']}"))
        
        # Sort by time
        timeline_items.sort(key=lambda x: x[0], reverse=True)
        
        if not timeline_items:
            content = Align.center("No recent activity\nStart journaling or tracking mood! 📝")
        else:
            timeline_text = "\n".join([item[1] for item in timeline_items[:5]])
            content = timeline_text
        
        return Panel(
            content,
            title="⏰ Recent Activity",
            border_style="blue"
        )
    
    def create_mood_panel(self, metrics: DashboardMetrics) -> Panel:
        mood_entries = self.storage.get_mood_entries(limit=7)
        
        if not mood_entries:
            content = Align.center("No mood data yet\nTrack your mood with:\nlogbuch mood happy 😊")
        else:
            # Current mood
            current_mood = mood_entries[0]['mood']
            mood_emoji = self._get_mood_emoji(current_mood)
            
            # Mood trend
            trend_indicator = {
                'improving': '📈 Improving',
                'stable': '➡️ Stable', 
                'declining': '📉 Needs attention'
            }.get(metrics.mood_trend, '➡️ Stable')
            
            # Recent moods
            recent_moods = []
            for mood in mood_entries[:5]:
                date_obj = datetime.datetime.fromisoformat(mood['date'].replace('Z', '+00:00'))
                date_str = date_obj.strftime("%m-%d")
                emoji = self._get_mood_emoji(mood['mood'])
                recent_moods.append(f"{date_str}: {emoji} {mood['mood']}")
            
            content = Group(
                Align.center(f"Current Mood\n{mood_emoji} {current_mood.title()}"),
                "",
                f"Trend: {trend_indicator}",
                "",
                "Recent Moods:",
                *recent_moods
            )
        
        return Panel(
            content,
            title="😊 Mood Tracking",
            border_style="magenta"
        )
    
    def create_goals_panel(self) -> Panel:
        goals = self.storage.get_goals()
        
        if not goals:
            content = Align.center("No goals set yet\nCreate goals with:\nlogbuch goal 'Your goal' 🎯")
        else:
            goals_content = []
            for goal in goals[:3]:  # Show top 3 goals
                progress = goal.get('progress', 0)
                status = "✅" if goal.get('completed') else "⏳"
                
                # Progress bar
                bar_length = 10
                filled = int(progress / 10)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                goal_text = goal['description'][:25] + ('...' if len(goal['description']) > 25 else '')
                goals_content.append(f"{status} {goal_text}")
                goals_content.append(f"   {bar} {progress}%")
                goals_content.append("")
            
            content = Group(*goals_content)
        
        return Panel(
            content,
            title="🎯 Goals Progress",
            border_style="cyan"
        )
    
    def create_insights_panel(self, metrics: DashboardMetrics) -> Panel:
        insights = []
        
        # Generate dynamic insights
        if metrics.completion_rate > 80:
            insights.append("🌟 Excellent completion rate!")
        elif metrics.completion_rate < 30:
            insights.append("💪 Focus on completing tasks")
        
        if metrics.overdue_tasks > 0:
            insights.append(f"⚠️ {metrics.overdue_tasks} overdue tasks need attention")
        
        if metrics.streak_days > 7:
            insights.append(f"🔥 Amazing {metrics.streak_days}-day streak!")
        elif metrics.streak_days == 0:
            insights.append("📝 Start a productivity streak today!")
        
        if metrics.high_priority > 5:
            insights.append("🎯 Consider prioritizing fewer tasks")
        
        if not insights:
            insights.append("✨ Everything looks great!")
            insights.append("🚀 Keep up the momentum!")
        
        content = "\n".join(insights)
        
        return Panel(
            content,
            title="🧠 AI Insights",
            border_style="bright_yellow"
        )
    
    def create_footer(self) -> Panel:
        controls = [
            "Press 'q' to quit",
            "Press 'r' to refresh", 
            "Press 'h' for help",
            f"Updates every {self.refresh_interval}s"
        ]
        
        footer_text = " • ".join(controls)
        
        return Panel(
            Align.center(footer_text),
            style="dim white"
        )
    
    def update_dashboard(self):
        metrics = self.get_metrics()
        
        # Update layout components
        self.layout["header"].update(self.create_header())
        self.layout["stats"].update(self.create_stats_panel(metrics))
        self.layout["tasks"].update(self.create_tasks_panel(metrics))
        self.layout["timeline"].update(self.create_timeline_panel())
        self.layout["mood"].update(self.create_mood_panel(metrics))
        self.layout["goals"].update(self.create_goals_panel())
        self.layout["insights"].update(self.create_insights_panel(metrics))
        self.layout["footer"].update(self.create_footer())
        
        # Update animation frame
        self.animation_frame += 1
        self.last_update = time.time()
    
    def run_live_dashboard(self):
        if not RICH_AVAILABLE:
            self.console.print("[red]Rich library not available for visual dashboard[/red]")
            return
        
        self.is_running = True
        
        with Live(self.layout, console=self.console, screen=True, auto_refresh=False) as live:
            while self.is_running:
                try:
                    self.update_dashboard()
                    live.update(self.layout)
                    live.refresh()
                    
                    time.sleep(self.refresh_interval)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Dashboard error: {e}")
                    time.sleep(1)
        
        self.is_running = False
    
    def _create_progress_bar(self, value: float, max_value: float, label: str, color: str) -> str:
        percentage = (value / max_value) * 100 if max_value > 0 else 0
        bar_length = 20
        filled = int(percentage / 5)  # 5% per character
        
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"{label}: {bar} {percentage:.1f}%"
    
    def _analyze_mood_trend(self, mood_entries: List[Dict]) -> str:
        if len(mood_entries) < 3:
            return "stable"
        
        # Simple sentiment analysis
        positive_moods = ['happy', 'excited', 'great', 'amazing', 'wonderful', 'fantastic', 'good', 'cheerful', 'joyful']
        negative_moods = ['sad', 'angry', 'frustrated', 'depressed', 'anxious', 'stressed', 'overwhelmed', 'tired']
        
        recent_scores = []
        for mood in mood_entries[:5]:
            mood_text = mood['mood'].lower()
            if any(pos in mood_text for pos in positive_moods):
                recent_scores.append(1)
            elif any(neg in mood_text for neg in negative_moods):
                recent_scores.append(-1)
            else:
                recent_scores.append(0)
        
        if len(recent_scores) >= 3:
            trend = sum(recent_scores[-3:]) - sum(recent_scores[-5:-3]) if len(recent_scores) >= 5 else sum(recent_scores)
            
            if trend > 0:
                return "improving"
            elif trend < 0:
                return "declining"
        
        return "stable"
    
    def _calculate_productivity_score(self, tasks: List[Dict], journal_entries: List[Dict], mood_entries: List[Dict]) -> float:
        score = 50  # Base score
        
        # Task completion factor
        if tasks:
            completion_rate = len([t for t in tasks if t.get('done')]) / len(tasks)
            score += completion_rate * 30
        
        # Recent activity factor
        recent_activity = len(journal_entries) + len(mood_entries)
        score += min(recent_activity * 2, 15)
        
        # Overdue penalty
        today = datetime.date.today()
        overdue_count = 0
        for task in tasks:
            if not task.get('done') and task.get('due_date'):
                try:
                    due_date = datetime.datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                    if due_date < today:
                        overdue_count += 1
                except:
                    continue
        
        score -= overdue_count * 5
        
        return max(0, min(100, score))
    
    def _calculate_streak(self, journal_entries: List[Dict], mood_entries: List[Dict]) -> int:
        if not journal_entries and not mood_entries:
            return 0
        
        # Get all activity dates
        activity_dates = set()
        
        for entry in journal_entries:
            try:
                date = datetime.datetime.fromisoformat(entry['date'].replace('Z', '+00:00')).date()
                activity_dates.add(date)
            except:
                continue
        
        for mood in mood_entries:
            try:
                date = datetime.datetime.fromisoformat(mood['date'].replace('Z', '+00:00')).date()
                activity_dates.add(date)
            except:
                continue
        
        if not activity_dates:
            return 0
        
        # Calculate streak from today backwards
        today = datetime.date.today()
        streak = 0
        
        current_date = today
        while current_date in activity_dates:
            streak += 1
            current_date -= datetime.timedelta(days=1)
        
        return streak
    
    def _get_mood_emoji(self, mood: str) -> str:
        mood_emojis = {
            'happy': '😊', 'sad': '😢', 'excited': '🤩', 'angry': '😠',
            'calm': '😌', 'stressed': '😰', 'tired': '😴', 'focused': '🧠',
            'grateful': '🙏', 'anxious': '😟', 'confident': '💪', 'peaceful': '☮️',
            'motivated': '🔥', 'content': '😌', 'frustrated': '😤', 'hopeful': '🌟'
        }
        
        return mood_emojis.get(mood.lower(), '😊')


# Dashboard command integration
def create_visual_dashboard_command(storage):
    dashboard = VisualDashboard(storage)
    
    try:
        dashboard.run_live_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed. Have a productive day!")
    except Exception as e:
        print(f"Dashboard error: {e}")


# Export for CLI integration
__all__ = ['VisualDashboard', 'create_visual_dashboard_command']
