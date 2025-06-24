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
from .donation import Donation # From main side


__all__ = [
    "User",
"UserProfile",
    "PracticeChallengeTemplate",
    "UserChallengeCompletion",
    "ChallengeType",
    "DifficultyLevel",
    "CompletionStatus",
    "JournalEntry", # From mind-progress-visualization-backend
    "MindsetChallengeTemplate", # From mind-progress-visualization-backend
    "UserMindsetCompletion", # From mind-progress-visualization-backend
    "MindsetChallengeFrequency", # From mind-progress-visualization-backend
    "MindsetCompletionStatus", # From mind-progress-visualization-backend
    "MindfulMomentTemplate", # From mind-progress-visualization-backend
    "UserReminderSetting", # From mind-progress-visualization-backend
    "MindfulMomentReminderFrequency", # From mind-progress-visualization-backend
    "Donation", # From main
]
