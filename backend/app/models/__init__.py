# backend/app/models/__init__.py
# This file makes all model classes available under the 'app.models' namespace.
# It imports the classes from their individual files.

from .donation import Donation
from .exchange_offer import ExchangeOffer, OfferStatusEnum
from .journal_entry import JournalEntry
from .mindful_moment import MindfulMomentTemplate, UserReminderSetting
from .mindset_challenge import MindsetChallengeTemplate, UserMindsetCompletion
from .practice_challenge import PracticeChallengeTemplate, UserChallengeCompletion
from .showcase_item import ShowcaseItem
from .skill import Skill
from .user import User
from .user_profile import UserProfile
# NOTE: SkillCategory was removed as it was not found in the file listing.
# Other models like Post, Favor, etc., are not imported as their files were not listed.
