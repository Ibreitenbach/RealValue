# backend/app/models/__init__.py
# Import all models here to make them accessible via the 'models' module
# and for Flask-Migrate to detect them.
# The __all__ list explicitly defines the public API of this package.

from .user import User
from .user_profile import UserProfile
from .skill import Skill, SkillCategory # Assuming Skill and SkillCategory are here
from .exchange_offer import ExchangeOffer, OfferStatusEnum # Assuming these are here
from .post import Post, PostType # Assuming these are here
from .favor import Favor # Assuming Favor is here
from .circle import Circle, CircleMember # Assuming these are here
from .endorsement import Endorsement # Assuming Endorsement is here

from .practice_challenge import (
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    ChallengeType,
    DifficultyLevel,
    CompletionStatus,
)
from .event import Event # Assuming Event is here

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
from .mind_content import MindContent, MindContentCategory # Assuming these are here
from .showcase_item import ShowcaseItem # Assuming this is here
from .donation import Donation # Assuming this is here


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