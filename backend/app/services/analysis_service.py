# backend/app/services/analysis_service.py
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict

from .. import db
from ..models import (
    JournalEntry,
    UserMindsetCompletion,
    MindsetChallengeTemplate,
    UserReminderSetting,
    # MindfulMomentTemplate, # Removed as unused in this service file directly
)


def get_journaling_consistency(user_id: int, time_period: str = "weekly"):
    """
    Calculates journaling consistency for a user.
    Counts JournalEntry submissions per week or month.

    Args:
        user_id: The ID of the user.
        time_period: "weekly" or "monthly".

    Returns:
        A list of dictionaries, e.g., [{"date": "YYYY-MM-DD", "count": N}] for weekly,
        or [{"month": "YYYY-MM", "count": N}] for monthly.
    """
    now = datetime.utcnow()
    results = []

    if time_period == "weekly":
        # Get data for the last 12 weeks
        start_date = now - timedelta(weeks=12)
        # Ensure we group by the start of the week (Monday)
        query = (
            db.session.query(
                func.date(
                    JournalEntry.created_at,
                    func.julianday(JournalEntry.created_at)
                    - func.strftime("%w", JournalEntry.created_at)
                    + 1,  # Monday as start of week
                ).label("week_start_date"),
                func.count(JournalEntry.id).label("count"),
            )
            .filter(JournalEntry.user_id == user_id)
            .filter(JournalEntry.created_at >= start_date)
            .group_by("week_start_date")
            .order_by("week_start_date")
            .all()
        )
        for row in query:
            results.append({"date": row.week_start_date, "count": row.count})

    elif time_period == "monthly":
        # Get data for the last 12 months
        start_date = now - timedelta(days=365)  # Approximate for 12 months
        query = (
            db.session.query(
                func.strftime("%Y-%m", JournalEntry.created_at).label("month"),
                func.count(JournalEntry.id).label("count"),
            )
            .filter(JournalEntry.user_id == user_id)
            .filter(JournalEntry.created_at >= start_date)
            .group_by("month")
            .order_by("month")
            .all()
        )
        for row in query:
            results.append({"month": row.month, "count": row.count})
    else:
        raise ValueError("Invalid time_period. Must be 'weekly' or 'monthly'.")

    return results


def get_challenge_completion_rate(user_id: int):
    """
    Calculates challenge completion rates, categorized by MindsetChallengeTemplate.category.
    Shows trends by month.

    Args:
        user_id: The ID of the user.

    Returns:
        A list of dictionaries, e.g.,
        [{"category": "Stoicism", "completed_count": N, "month": "YYYY-MM"}, ...]
    """
    now = datetime.utcnow()
    # Get data for the last 12 months
    start_date = now - timedelta(days=365)

    query = (
        db.session.query(
            MindsetChallengeTemplate.category.label("category"),
            func.strftime("%Y-%m", UserMindsetCompletion.completed_at).label("month"),
            func.count(UserMindsetCompletion.id).label("completed_count"),
        )
        .join(
            MindsetChallengeTemplate,
            UserMindsetCompletion.challenge_template_id == MindsetChallengeTemplate.id,
        )
        .filter(UserMindsetCompletion.user_id == user_id)
        .filter(
            UserMindsetCompletion.status == "COMPLETED"
        )  # Assuming 'COMPLETED' status
        .filter(UserMindsetCompletion.completed_at >= start_date)
        .group_by("category", "month")
        .order_by("month", "category")
        .all()
    )

    results = [
        {
            "category": (
                row.category if row.category else "Uncategorized"
            ),  # Handle null categories
            "completed_count": row.completed_count,
            "month": row.month,
        }
        for row in query
    ]
    return results


def get_reminder_engagement(user_id: int):
    """
    Counts the number of MindfulMomentTemplates a user has enabled.

    Args:
        user_id: The ID of the user.

    Returns:
        An integer representing the count of enabled reminders.
    """
    count = UserReminderSetting.query.filter_by(
        user_id=user_id, is_enabled=True
    ).count()
    return count


def get_tag_analysis(user_id: int):
    """
    Counts occurrences of reflection_tags in JournalEntry submissions for a user.
    Assumes tags are stored as comma-separated strings in JournalEntry.reflection_tags.

    Args:
        user_id: The ID of the user.

    Returns:
        A dictionary with tags as keys and their counts as values,
        e.g., {"gratitude": 10, "reframing": 5}
    """
    entries = (
        JournalEntry.query.filter_by(user_id=user_id)
        .filter(JournalEntry.reflection_tags.isnot(None))
        .all()
    )
    tag_counts = defaultdict(int)

    for entry in entries:
        if entry.reflection_tags:
            tags = [
                tag.strip().lower()
                for tag in entry.reflection_tags.split(",")
                if tag.strip()
            ]
            for tag in tags:
                tag_counts[tag] += 1

    # Sort by count descending for better presentation if needed by frontend
    sorted_tags = dict(
        sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    )
    return sorted_tags


def get_mind_progress_summary(user_id: int):
    """
    Provides a high-level summary of mind progress for the user.

    Args:
        user_id: The ID of the user.

    Returns:
        A dictionary containing:
        - total_journal_entries: Count of all journal entries.
        - total_challenges_completed: Count of all completed mindset challenges.
        - active_reminders: Count of enabled mindful moment reminders.
    """
    total_journal_entries = JournalEntry.query.filter_by(user_id=user_id).count()
    total_challenges_completed = UserMindsetCompletion.query.filter_by(
        user_id=user_id, status="COMPLETED"  # Assuming 'COMPLETED' status
    ).count()
    active_reminders = get_reminder_engagement(user_id)  # Reuse existing function

    return {
        "total_journal_entries": total_journal_entries,
        "total_challenges_completed": total_challenges_completed,
        "active_reminders": active_reminders,
    }


# Helper for weekly grouping if needed, specifically for SQLite
# For PostgreSQL, func.date_trunc('week', JournalEntry.created_at) is better
# For SQLite, we need to calculate the start of the week manually
# This logic is now embedded in get_journaling_consistency to avoid issues with direct func calls in query
# def get_week_start_sqlite(date_column):
#     """
#     SQLite compatible way to get the start of the week (Monday).
#     This is a bit complex due to SQLite's date functions.
#     """
#     # day of week: 0=Sunday, 1=Monday, ..., 6=Saturday
#     # We want to subtract (day_of_week - 1 (for Monday)) days if day_of_week > 0
#     # If Sunday (0), we want to subtract 6 days (or add 1 and subtract 7)
#     # julianday('now') - strftime('%w', 'now') + 1 (Monday)
#     # julianday('now') - strftime('%w', 'now')     (Sunday)
#     # For Monday as start: date(date_column, '-' || strftime('%w', date_column) || ' days', '+1 day') if strftime('%w', date_column) != '0'
#     # else date(date_column, '-6 days')
#     # A simpler approach: date(date_column, 'weekday 0', '-6 days') might give Sunday for some locales
#     # The most reliable for Monday start:
#     # date(YourDateColumn, CAST((strftime('%w', YourDateColumn) - 1) AS TEXT) || ' days')
#     # No, this is not right.
#     # Correct for Monday: DATE(date_column, '-' || STRFTIME('%w', date_column) || ' DAYS', '+1 DAYS') for Sunday=0
#     # If Monday is 1: DATE(date_column, '-' || (STRFTIME('%w', date_column)-1) || ' DAYS')
#     # Assuming strftime('%w', ...) gives 0 for Sunday, 1 for Monday, etc.
#     # We want to get to Monday. If current day is Wednesday (3), subtract 2 days. (3-1)
#     # If current day is Sunday (0), we want to subtract 6 days to get to previous Monday.
#     # This is equivalent to adding 1 day (to make it like Monday) then subtracting (original_weekday + 1) days.
#     # Or: date(my_date, '-' || ((strftime('%w', my_date) + 6) % 7) || ' days')
#     # The version used in query: func.date(JournalEntry.created_at, func.julianday(JournalEntry.created_at) - func.strftime('%w', JournalEntry.created_at) + 1)
#     # This should give Monday as the start of the week (assuming %w = 0 for Sunday)
#     # julianday(date) - strftime('%w', date) gets Sunday. Add 1 day for Monday.
#     return func.date(date_column, '-' || (func.strftime('%w', date_column) -1) || ' days')

# Example of how to adjust for SQLite week start if needed, not directly used now
# if db.engine.dialect.name == "sqlite":
#     # Adjust week calculation for SQLite if needed
#     # For instance, if func.date_trunc is not available or behaves differently
#     # The current get_journaling_consistency tries to handle SQLite's week start
#     pass
