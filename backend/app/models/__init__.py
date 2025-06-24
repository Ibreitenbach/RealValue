# backend/app/models/__init__.py
# Import all models here to make them accessible via the 'models' module
# and for Flask-Migrate to detect them.

from .user import User
from .user_profile import UserProfile
from .practice_challenge import (
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)
from .skill import Skill
from .exchange_offer import ExchangeOffer, OfferStatusEnum

__all__ = [
    "User",
    "UserProfile",
    "PracticeChallengeTemplate",
    "UserChallengeCompletion",
    "ChallengeType",
    "DifficultyLevel",
    "CompletionStatus",
    "Skill",
    "ExchangeOffer",
    "OfferStatusEnum",
]
