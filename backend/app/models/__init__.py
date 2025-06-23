# backend/app/models/__init__.py

# Import all models here to make them accessible via the 'models' module
# and for Flask-Migrate to detect them.

from .user import User
from .practice_challenge import (
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)

__all__ = [
    "User",
    "PracticeChallengeTemplate",
    "UserChallengeCompletion",
    "ChallengeType",
    "DifficultyLevel",
    "CompletionStatus",
]
