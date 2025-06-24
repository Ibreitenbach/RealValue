# backend/app/models/__init__.py
# Import all models here to make them accessible via the 'models' module
# and for Flask-Migrate to detect them.
# The __all__ list explicitly defines the public API of this package.

from .user import User
from .user_profile import UserProfile
from .skill import Skill, SkillCategory
from .exchange_offer import ExchangeOffer, OfferStatusEnum
from .post import Post, PostType
from .favor import Favor
from .circle import Circle, CircleMember
from .endorsement import Endorsement

from .practice_challenge import (
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)
from .event import Event

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
from .mind_content import MindContent, MindContentCategory
from .showcase_item import ShowcaseItem
from .donation import Donation


__all__ = [
    "User",
    "UserProfile",
    "Skill",
    "SkillCategory",
    "ExchangeOffer",
    "OfferStatusEnum",
    "Post",
    "PostType",
    "Favor",
    "Circle",
    "CircleMember",
    "Endorsement",
    "PracticeChallengeTemplate",
    "UserChallengeCompletion",
    "ChallengeType",
    "DifficultyLevel",
    "CompletionStatus",
    "Event",
    "JournalEntry",
    "MindsetChallengeTemplate",
    "UserMindsetCompletion",
    "MindsetChallengeFrequency",
    "MindsetCompletionStatus",
    "MindfulMomentTemplate",
    "UserReminderSetting",
    "MindfulMomentReminderFrequency",
    "MindContent",
    "MindContentCategory",
    "ShowcaseItem",
    "Donation",
]