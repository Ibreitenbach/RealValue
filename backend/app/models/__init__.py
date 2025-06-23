# backend/app/models/__init__.py
# Import all models here to make them accessible via the 'models' module
# and for Flask-Migrate to detect them.

from .user import User
from .user_profile import UserProfile # From feat/user-profile-management-basic side
from .practice_challenge import (    # From main side
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)

__all__ = [
    "User",
    "UserProfile", # From feat/user-profile-management-basic side
    "PracticeChallengeTemplate", # From main side
    "UserChallengeCompletion",   # From main side
    "ChallengeType",             # From main side
    "DifficultyLevel",           # From main side
    "CompletionStatus",          # From main side
]