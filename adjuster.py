#!/usr/bin/env python3
"""
Dynamic Learning Adjustment System

This module provides intelligent adjustment of learning schedules based on:
- Completion rate analysis
- Time tracking
- Difficulty feedback
- Streak maintenance

Usage:
    python adjuster.py --today          # Show today's tasks
    python adjuster.py --complete ID    # Mark task as complete
    python adjuster.py --recommend      # Get adjustment recommendations
    python adjuster.py --stats          # Show learning statistics
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path


class LearningAdjuster:
    """Dynamic learning schedule adjuster."""

    def __init__(self, schedule_path="schedule.json", progress_path="progress.json"):
        """Initialize the adjuster with schedule and progress data."""
        self.schedule_path = Path(schedule_path)
        self.progress_path = Path(progress_path)
        self.schedule = self._load_json(self.schedule_path)
        self.progress = self._load_json(self.progress_path)

    def _load_json(self, path):
        """Load JSON file safely."""
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_json(self, path, data):
        """Save JSON file with proper formatting."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_today_tasks(self):
        """Get tasks scheduled for today."""
        day_name = datetime.now().strftime("%A").lower()
        daily_tasks = self.schedule.get("daily_tasks", {})
        today_schedule = daily_tasks.get(day_name, {})

        return {
            "day": day_name,
            "focus": today_schedule.get("focus", "general"),
            "tasks": today_schedule.get("tasks", []),
        }

    def complete_task(self, task_id, hours_spent=None, difficulty_rating=None):
        """Mark a task as complete and update progress."""
        # Update daily log
        log_entry = {
            "date": datetime.now().isoformat(),
            "task_id": task_id,
            "hours_spent": hours_spent or 0,
            "difficulty_rating": difficulty_rating,
        }

        if "daily_log" not in self.progress:
            self.progress["daily_log"] = []
        self.progress["daily_log"].append(log_entry)

        # Update overall stats
        stats = self.progress.get("overall_stats", {})
        stats["total_tasks_completed"] = stats.get("total_tasks_completed", 0) + 1
        if hours_spent:
            stats["total_hours_studied"] = (
                stats.get("total_hours_studied", 0) + hours_spent
            )

        # Update completion rate
        self._update_completion_rate(stats)

        # Update streak
        self._update_streak()

        # Update last modified
        self.progress["last_updated"] = datetime.now().isoformat()

        # Save progress
        self._save_json(self.progress_path, self.progress)

        return {"status": "success", "task_id": task_id, "message": "Task completed!"}

    def _update_streak(self):
        """Update the learning streak based on daily activity."""
        stats = self.progress.get("overall_stats", {})
        daily_log = self.progress.get("daily_log", [])

        if not daily_log:
            return

        # Check if there was activity today
        today = datetime.now().date()
        last_activity = datetime.fromisoformat(daily_log[-1]["date"]).date()

        if last_activity == today:
            # Activity today, increment streak if yesterday had activity
            yesterday = today - timedelta(days=1)
            yesterday_activities = [
                log
                for log in daily_log
                if datetime.fromisoformat(log["date"]).date() == yesterday
            ]

            if yesterday_activities or stats.get("current_streak_days", 0) == 0:
                stats["current_streak_days"] = stats.get("current_streak_days", 0) + 1
        else:
            # No activity today, check if streak is broken
            if (today - last_activity).days > 1:
                stats["current_streak_days"] = 0

        # Update longest streak
        if stats.get("current_streak_days", 0) > stats.get("longest_streak_days", 0):
            stats["longest_streak_days"] = stats["current_streak_days"]

        self.progress["overall_stats"] = stats

    def _update_completion_rate(self, stats):
        """Calculate and update the completion rate based on scheduled vs completed tasks."""
        daily_log = self.progress.get("daily_log", [])

        # Calculate total scheduled tasks per week
        total_scheduled_per_week = sum(
            len(day_data.get("tasks", []))
            for day_data in self.schedule.get("daily_tasks", {}).values()
        )

        if total_scheduled_per_week == 0:
            return

        # Get days since start
        start_date = self.progress.get("start_date")
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            days_elapsed = (datetime.now().date() - start).days + 1
            weeks_elapsed = max(1, days_elapsed / 7)

            # Calculate expected tasks based on time elapsed
            expected_tasks = int(total_scheduled_per_week * weeks_elapsed)
            completed_tasks = stats.get("total_tasks_completed", 0)

            if expected_tasks > 0:
                completion_rate = min(100, (completed_tasks / expected_tasks) * 100)
                stats["completion_rate_percent"] = round(completion_rate, 1)

    def get_recommendations(self):
        """Generate learning recommendations based on progress analysis."""
        stats = self.progress.get("overall_stats", {})
        recommendations = []

        # Analyze completion rate
        completion_rate = stats.get("completion_rate_percent", 0)
        if completion_rate < 70:
            recommendations.append(
                {
                    "type": "workload",
                    "priority": "high",
                    "message": "Completion rate is low. Consider reducing daily task load.",
                    "action": "reduce_tasks",
                }
            )
        elif completion_rate > 90:
            recommendations.append(
                {
                    "type": "workload",
                    "priority": "medium",
                    "message": "Excellent progress! Consider increasing challenge level.",
                    "action": "increase_difficulty",
                }
            )

        # Check streak
        current_streak = stats.get("current_streak_days", 0)
        if current_streak >= 7:
            recommendations.append(
                {
                    "type": "motivation",
                    "priority": "info",
                    "message": f"Great job! {current_streak} day streak! Keep it up!",
                    "action": "maintain",
                }
            )
        elif current_streak == 0:
            recommendations.append(
                {
                    "type": "motivation",
                    "priority": "high",
                    "message": "Start building your streak today!",
                    "action": "start_streak",
                }
            )

        # Phase progression recommendation
        current_phase = self.schedule.get("current_phase", 1)
        phase_key = f"phase_{current_phase}_"
        for key, phase_data in self.progress.get("phase_progress", {}).items():
            if key.startswith(phase_key):
                if phase_data.get("progress_percent", 0) >= 80:
                    recommendations.append(
                        {
                            "type": "progression",
                            "priority": "medium",
                            "message": "Ready to advance to the next phase!",
                            "action": "advance_phase",
                        }
                    )

        return recommendations

    def get_stats(self):
        """Get comprehensive learning statistics."""
        stats = self.progress.get("overall_stats", {})
        phase_progress = self.progress.get("phase_progress", {})

        # Calculate additional metrics
        daily_log = self.progress.get("daily_log", [])
        if daily_log:
            total_hours = stats.get("total_hours_studied", 0)
            days_active = len(
                set(
                    datetime.fromisoformat(log["date"]).date() for log in daily_log
                )
            )
            stats["average_daily_hours"] = (
                round(total_hours / days_active, 2) if days_active > 0 else 0
            )

        # Phase summaries
        phase_summaries = {}
        for phase_name, phase_data in phase_progress.items():
            phase_summaries[phase_name] = {
                "status": phase_data.get("status", "not_started"),
                "progress": phase_data.get("progress_percent", 0),
            }

        return {"overall": stats, "phases": phase_summaries, "recommendations": self.get_recommendations()}

    def adjust_schedule(self, adjustment_type, **kwargs):
        """Apply schedule adjustments based on recommendations."""
        if adjustment_type == "reduce_tasks":
            # Reduce task count by removing low priority tasks
            for day, day_data in self.schedule.get("daily_tasks", {}).items():
                tasks = day_data.get("tasks", [])
                day_data["tasks"] = [t for t in tasks if t.get("priority") != "low"]

        elif adjustment_type == "increase_difficulty":
            # Increase estimated time for tasks
            for day, day_data in self.schedule.get("daily_tasks", {}).items():
                for task in day_data.get("tasks", []):
                    task["duration_minutes"] = int(
                        task.get("duration_minutes", 60) * 1.2
                    )

        elif adjustment_type == "advance_phase":
            current_phase = self.schedule.get("current_phase", 1)
            self.schedule["current_phase"] = min(current_phase + 1, 4)

        self._save_json(self.schedule_path, self.schedule)
        return {"status": "success", "adjustment": adjustment_type}


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="AI Learning Management System - Dynamic Adjuster"
    )
    parser.add_argument("--today", action="store_true", help="Show today's tasks")
    parser.add_argument("--complete", type=str, help="Mark task as complete by ID")
    parser.add_argument(
        "--recommend", action="store_true", help="Get learning recommendations"
    )
    parser.add_argument("--stats", action="store_true", help="Show learning statistics")
    parser.add_argument(
        "--hours", type=float, help="Hours spent on task (use with --complete)"
    )
    parser.add_argument(
        "--difficulty",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Difficulty rating (use with --complete)",
    )

    args = parser.parse_args()

    # Initialize adjuster
    adjuster = LearningAdjuster()

    if args.today:
        today_tasks = adjuster.get_today_tasks()
        print(f"\n📅 Today's Focus: {today_tasks['focus'].upper()}")
        print(f"Day: {today_tasks['day'].capitalize()}\n")
        print("Tasks:")
        for task in today_tasks["tasks"]:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                task.get("priority", "medium"), "⚪"
            )
            print(
                f"  {priority_emoji} [{task['id']}] {task['description']} ({task['duration_minutes']} min)"
            )
        print()

    elif args.complete:
        result = adjuster.complete_task(
            args.complete, hours_spent=args.hours, difficulty_rating=args.difficulty
        )
        print(f"✅ {result['message']}")

    elif args.recommend:
        recommendations = adjuster.get_recommendations()
        print("\n📋 Learning Recommendations:\n")
        if not recommendations:
            print("  No specific recommendations at this time. Keep up the good work!")
        for rec in recommendations:
            priority_emoji = {"high": "🔴", "medium": "🟡", "info": "ℹ️", "low": "🟢"}.get(
                rec.get("priority", "info"), "⚪"
            )
            print(f"  {priority_emoji} {rec['message']}")
        print()

    elif args.stats:
        stats = adjuster.get_stats()
        print("\n📊 Learning Statistics:\n")
        overall = stats["overall"]
        print(f"  Total Hours Studied: {overall.get('total_hours_studied', 0)}")
        print(f"  Tasks Completed: {overall.get('total_tasks_completed', 0)}")
        print(f"  Current Streak: {overall.get('current_streak_days', 0)} days")
        print(f"  Longest Streak: {overall.get('longest_streak_days', 0)} days")
        print(f"  Avg Daily Hours: {overall.get('average_daily_hours', 0)}")
        print("\n  Phase Progress:")
        for phase, data in stats["phases"].items():
            status_emoji = {"completed": "✅", "in_progress": "🔄", "not_started": "⬜"}.get(
                data["status"], "⬜"
            )
            print(f"    {status_emoji} {phase}: {data['progress']}%")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
