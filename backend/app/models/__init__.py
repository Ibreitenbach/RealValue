# backend/app/models/__init__.py
# Import all models here to make them accessible via the 'models' module
# and for Flask-Migrate to detect them.

from .user import User
from .user_profile import UserProfile  # From feat/user-profile-management-basic side
from .practice_challenge import (  # From main side
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)
from .journal_entry import JournalEntry
from .mindset_challenge import (
    MindsetChallengeTemplate,
    UserMindsetCompletion,
    MindsetChallengeFrequency,
    MindsetCompletionStatus,
)
from .mindful_moment import (
    MindfulMomentTemplate,
    UserReminderSetting,
    MindfulMomentReminderFrequency,
)


__all__ = [
    "User",
    "UserProfile",
    "PracticeChallengeTemplate",
    "UserChallengeCompletion",
    "ChallengeType",
    "DifficultyLevel",
    "CompletionStatus",
    "JournalEntry",
    "MindsetChallengeTemplate",
    "UserMindsetCompletion",
    "MindsetChallengeFrequency",
    "MindsetCompletionStatus",
    "MindfulMomentTemplate",
    "UserReminderSetting",
    "MindfulMomentReminderFrequency",
]
