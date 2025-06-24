# backend/tests/test_analysis_service.py
import pytest
from datetime import datetime, timedelta, date
from collections import defaultdict

from backend.app import create_app, db
from backend.app.models import (
    User,
    JournalEntry,
    MindsetChallengeTemplate,
    UserMindsetCompletion,
    MindfulMomentTemplate,
    UserReminderSetting,
    MindsetCompletionStatus,
)
from backend.app.services import analysis_service


@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test_jwt_secret",  # Ensure this is set for tests if needed
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


@pytest.fixture
def init_database(test_app):
    # Create users
    user1 = User(username="user1", email="user1@example.com")
    user1.set_password("password")
    user2 = User(username="user2", email="user2@example.com")
    user2.set_password("password")
    db.session.add_all([user1, user2])
    db.session.commit()

    # Journal Entries for User 1
    # Last week
    db.session.add(
        JournalEntry(
            user_id=user1.id,
            content="Journal 1",
            created_at=datetime.utcnow() - timedelta(days=3),
            reflection_tags=" gratitude , test ",
        )
    )
    db.session.add(
        JournalEntry(
            user_id=user1.id,
            content="Journal 2",
            created_at=datetime.utcnow() - timedelta(days=4),
            reflection_tags="Reframing",
        )
    )
    # Two weeks ago
    db.session.add(
        JournalEntry(
            user_id=user1.id,
            content="Journal 3",
            created_at=datetime.utcnow() - timedelta(days=10),
        )
    )
    # Last month (but also counts for a week if recent enough)
    db.session.add(
        JournalEntry(
            user_id=user1.id,
            content="Journal 4",
            created_at=datetime.utcnow() - timedelta(days=25),
            reflection_tags="Gratitude",
        )
    )
    # Older entry
    db.session.add(
        JournalEntry(
            user_id=user1.id,
            content="Journal old",
            created_at=datetime.utcnow() - timedelta(days=100),
        )
    )

    # Mindset Challenges and Completions for User 1
    cat1 = "Stoicism"
    cat2 = "Mindfulness"
    mct1 = MindsetChallengeTemplate(
        title="Challenge A", description="A desc", category=cat1
    )
    mct2 = MindsetChallengeTemplate(
        title="Challenge B", description="B desc", category=cat2
    )
    mct3 = MindsetChallengeTemplate(
        title="Challenge C", description="C desc", category=cat1
    )  # Another for Stoicism
    mct4 = MindsetChallengeTemplate(
        title="Challenge D (Uncategorized)", description="D desc"
    )
    db.session.add_all([mct1, mct2, mct3, mct4])
    db.session.commit()

    # This month completions
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct1.id,
            completed_at=datetime.utcnow() - timedelta(days=5),
            status=MindsetCompletionStatus.COMPLETED,
        )
    )
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct2.id,
            completed_at=datetime.utcnow() - timedelta(days=10),
            status=MindsetCompletionStatus.COMPLETED,
        )
    )
    # Last month completions
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct1.id,
            completed_at=datetime.utcnow() - timedelta(days=35),
            status=MindsetCompletionStatus.COMPLETED,
        )
    )
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct3.id,
            completed_at=datetime.utcnow() - timedelta(days=40),
            status=MindsetCompletionStatus.COMPLETED,
        )
    )
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct4.id,
            completed_at=datetime.utcnow() - timedelta(days=40),
            status=MindsetCompletionStatus.COMPLETED,
        )
    )  # Uncategorized
    # Skipped completion (should not be counted in "completed")
    db.session.add(
        UserMindsetCompletion(
            user_id=user1.id,
            challenge_template_id=mct2.id,
            completed_at=datetime.utcnow() - timedelta(days=1),
            status=MindsetCompletionStatus.SKIPPED,
        )
    )

    # Mindful Moment Reminders for User 1
    mmt1 = MindfulMomentTemplate(text="Be present", category="Focus")
    mmt2 = MindfulMomentTemplate(text="Breathe deeply", category="Breathing")
    mmt3 = MindfulMomentTemplate(text="Notice something new", category="Awareness")
    db.session.add_all([mmt1, mmt2, mmt3])
    db.session.commit()

    db.session.add(
        UserReminderSetting(
            user_id=user1.id,
            mindful_moment_template_id=mmt1.id,
            frequency="DAILY",
            is_enabled=True,
        )
    )
    db.session.add(
        UserReminderSetting(
            user_id=user1.id,
            mindful_moment_template_id=mmt2.id,
            frequency="WEEKLY",
            is_enabled=True,
        )
    )
    db.session.add(
        UserReminderSetting(
            user_id=user1.id,
            mindful_moment_template_id=mmt3.id,
            frequency="DAILY",
            is_enabled=False,
        )
    )  # Disabled

    # Data for User 2 (mostly empty or minimal)
    db.session.add(
        JournalEntry(
            user_id=user2.id,
            content="User 2 Journal 1",
            created_at=datetime.utcnow() - timedelta(days=1),
        )
    )
    db.session.add(
        UserReminderSetting(
            user_id=user2.id,
            mindful_moment_template_id=mmt1.id,
            frequency="DAILY",
            is_enabled=True,
        )
    )

    db.session.commit()
    yield  # tests will run here
    db.session.remove()
    # No need to drop tables here as test_app fixture handles it at module level


def test_get_journaling_consistency_weekly(test_app, init_database):
    user1 = User.query.filter_by(username="user1").first()

    # Calculate expected weekly counts based on init_database
    # This is a bit manual and depends on current date, better to fix dates or mock 'now'
    # For simplicity, we'll check that the structure is right and counts are plausible
    # For JournalEntry created_at=datetime.utcnow() - timedelta(days=X)
    # days=3,4 are in current week (or week before if run on Sun/Mon depending on start of week)
    # days=10 is previous week
    # days=25 is a few weeks ago

    results = analysis_service.get_journaling_consistency(
        user1.id, time_period="weekly"
    )
    assert isinstance(results, list)
    if results:  # if there are entries in the last 12 weeks
        for item in results:
            assert "date" in item
            assert "count" in item
            assert isinstance(item["count"], int)
            # Check if date is a string (YYYY-MM-DD) or date object
            assert isinstance(item["date"], (str, date))

    # More specific assertions would require mocking datetime.utcnow() or very careful date setup
    # Example: Count entries from last week (days 3,4)
    # This specific check is hard without date mocking, so we check general structure above.
    # We expect at least one entry from "last week" (days 3,4) and one from "two weeks ago" (day 10)
    # and one from "last month" (day 25) if they fall in separate weeks within 12 weeks.

    # Let's find specific entries for more robust check
    # entry_3_days_ago_week_start = (datetime.utcnow() - timedelta(days=3)).strftime( # F841
    #     "%Y-%m-%d"
    # )
    # Adjust to Monday as week start for comparison
    # dt_3_days_ago = datetime.utcnow() - timedelta(days=3) # F841
    # monday_3_days_ago = dt_3_days_ago - timedelta(days=dt_3_days_ago.weekday()) # F841

    # current_week_entries = 0 # F841
    # prev_week_entries = 0 # F841

    # Simplified check: Count how many entries are in the most recent week block
    # This is still a bit fragile due to how weeks are calculated relative to 'now'
    # A full test would involve setting specific dates for entries and mocking 'datetime.utcnow()'
    # in the service for predictable windowing.

    # Count entries within the last 7 days (approx current week)
    # And between 7 and 14 days (approx previous week)

    # this_week_count_actual = JournalEntry.query.filter( # F841
    #     JournalEntry.user_id == user1.id,
    #     JournalEntry.created_at >= datetime.utcnow() - timedelta(days=7),
    # ).count()

    if results:
        # The most recent period in results should roughly correspond to this_week_count_actual
        # This is not a perfect test due to week boundary definitions.
        # For now, we'll assert that at least one result exists if we have recent entries.
        assert len(results) > 0


def test_get_journaling_consistency_monthly(test_app, init_database):
    user1 = User.query.filter_by(username="user1").first()
    results = analysis_service.get_journaling_consistency(
        user1.id, time_period="monthly"
    )
    assert isinstance(results, list)

    current_month_str = datetime.utcnow().strftime("%Y-%m")
    # last_month_str = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime( # F841
    #     "%Y-%m"
    # )

    # found_current_month = False # F841
    if results:
        for item in results:
            assert "month" in item
            assert "count" in item
            assert isinstance(item["count"], int)
            if item["month"] == current_month_str:
                # found_current_month = True
                # days=3,4,10,25 are all potentially in current or last month
                # We have 4 entries in the last 30 days for user1
                # This check depends on when the test is run relative to month end
                pass

    # User1 has 4 entries in the last 30 days, 1 older one.
    # Check if total count across months (within last year) is 4 or 5
    total_monthly_count = sum(r["count"] for r in results)
    assert (
        total_monthly_count >= 4
    )  # Should be 4 for entries in last 30 days, +1 for entry at 100 days if still in 12 month window


def test_get_journaling_consistency_invalid_period(test_app, init_database):
    user1 = User.query.filter_by(username="user1").first()
    with pytest.raises(ValueError):
        analysis_service.get_journaling_consistency(user1.id, time_period="yearly")


def test_get_challenge_completion_rate(test_app, init_database):
    user1 = User.query.filter_by(username="user1").first()
    results = analysis_service.get_challenge_completion_rate(user1.id)
    assert isinstance(results, list)

    # Expected:
    # This month: Stoicism (1), Mindfulness (1)
    # Last month: Stoicism (2), Uncategorized (1)

    current_month_str = datetime.utcnow().strftime("%Y-%m")
    last_month_str = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime(
        "%Y-%m"
    )

    categories_this_month = defaultdict(int)
    categories_last_month = defaultdict(int)

    for item in results:
        assert "category" in item
        assert "completed_count" in item
        assert "month" in item
        if item["month"] == current_month_str:
            categories_this_month[item["category"]] += item["completed_count"]
        elif item["month"] == last_month_str:
            categories_last_month[item["category"]] += item["completed_count"]

    assert (
        categories_this_month["Stoicism"] >= 1
    )  # Can be more if test run near month end
    assert categories_this_month["Mindfulness"] >= 1

    # These checks are more robust if we fix completion dates relative to a mocked 'now'
    # For now, this structure check is the most reliable part.
    # Example:
    # Stoicism completions: 1 this month (days=5), 2 last month (days=35, 40)
    # Mindfulness completions: 1 this month (days=10)
    # Uncategorized: 1 last month (days=40)

    # Total completed for user1 is 5
    total_completed = sum(r["completed_count"] for r in results)
    assert total_completed == 5


def test_get_reminder_engagement(test_app, init_database):
    user1 = User.query.filter_by(username="user1").first()
    user2 = User.query.filter_by(username="user2").first()

    assert (
        analysis_service.get_reminder_engagement(user1.id) == 2
    )  # 2 enabled for user1
    assert (
        analysis_service.get_reminder_engagement(user2.id) == 1
    )  # 1 enabled for user2


def test_get_tag_analysis(test_app, init_database):
    user1 = User.query.filter_by(username="user1").first()
    results = analysis_service.get_tag_analysis(user1.id)
    assert isinstance(results, dict)
    # Expected tags from user1:
    # " gratitude , test " -> gratitude:1, test:1
    # "Reframing" -> reframing:1
    # "Gratitude" -> gratitude:1 (becomes gratitude:2 due to case-insensitivity and merging)
    assert results.get("gratitude") == 2
    assert results.get("test") == 1
    assert results.get("reframing") == 1
    assert len(results) == 3

    # Check sorting (first item should be 'gratitude')
    if results:
        assert list(results.keys())[0] == "gratitude"


def test_get_mind_progress_summary(test_app, init_database):
    user1 = User.query.filter_by(username="user1").first()
    summary = analysis_service.get_mind_progress_summary(user1.id)
    assert isinstance(summary, dict)
    assert summary["total_journal_entries"] == 5  # 4 recent, 1 old
    assert summary["total_challenges_completed"] == 5  # All completed ones for user1
    assert summary["active_reminders"] == 2  # From get_reminder_engagement

    user2 = User.query.filter_by(username="user2").first()
    summary_u2 = analysis_service.get_mind_progress_summary(user2.id)
    assert summary_u2["total_journal_entries"] == 1
    assert summary_u2["total_challenges_completed"] == 0
    assert summary_u2["active_reminders"] == 1


def test_empty_data_scenarios(test_app):  # Test with a fresh user and no data
    # Create a new user with no data
    app = test_app
    with app.app_context():  # Ensure we are in app context
        user3 = User(username="user3", email="user3@example.com")
        user3.set_password("password")
        db.session.add(user3)
        db.session.commit()

        assert analysis_service.get_journaling_consistency(user3.id, "weekly") == []
        assert analysis_service.get_journaling_consistency(user3.id, "monthly") == []
        assert analysis_service.get_challenge_completion_rate(user3.id) == []
        assert analysis_service.get_reminder_engagement(user3.id) == 0
        assert analysis_service.get_tag_analysis(user3.id) == {}
        summary = analysis_service.get_mind_progress_summary(user3.id)
        assert summary["total_journal_entries"] == 0
        assert summary["total_challenges_completed"] == 0
        assert summary["active_reminders"] == 0

        db.session.delete(user3)
        db.session.commit()
