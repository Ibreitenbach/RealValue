# backend/app/models/practice_challenge.py
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from .. import db  # Assuming db is initialized in backend/app/__init__.py
from .user import User  # noqa: F401 # Used in relationship string arguments


class ChallengeType(enum.Enum):
    TEXT_RESPONSE = "text_response"
    PHOTO_UPLOAD = "photo_upload"
    CHECKBOX_COMPLETION = "checkbox_completion"
    # Add other types as needed


class DifficultyLevel(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    # Add other levels as needed


class CompletionStatus(enum.Enum):
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    FAILED = "failed"
    # Add other statuses as needed


class PracticeChallengeTemplate(db.Model):
    __tablename__ = "practice_challenge_templates"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # TODO: Change to ForeignKey('skills.id') once Skill model is implemented
    associated_skill_id = Column(Integer, nullable=True)

    challenge_type = Column(Enum(ChallengeType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to completions (one-to-many)
    completions = relationship(
        "UserChallengeCompletion", back_populates="challenge_template"
    )

    def __repr__(self):
        return f"<PracticeChallengeTemplate {self.id}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "associated_skill_id": self.associated_skill_id,
            "challenge_type": (
                self.challenge_type.value if self.challenge_type else None
            ),
            "difficulty": self.difficulty.value if self.difficulty else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserChallengeCompletion(db.Model):
    __tablename__ = "user_challenge_completions"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("user.id"), nullable=False
    )  # Corrected table name to 'user'
    challenge_template_id = Column(
        Integer, ForeignKey("practice_challenge_templates.id"), nullable=False
    )

    completed_at = Column(DateTime, nullable=True)  # Nullable if completion is pending
    user_response = Column(Text, nullable=True)  # e.g., text or URL
    status = Column(
        Enum(CompletionStatus), nullable=False, default=CompletionStatus.PENDING_REVIEW
    )

    # Relationships
    user = relationship("User", backref=db.backref("challenge_completions", lazy=True))
    challenge_template = relationship(
        "PracticeChallengeTemplate", back_populates="completions"
    )

    def __repr__(self):
        return f"<UserChallengeCompletion {self.id} (User: {self.user_id}, Challenge: {self.challenge_template_id}, Status: {self.status})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "challenge_template_id": self.challenge_template_id,
            "challenge_title": (
                self.challenge_template.title if self.challenge_template else None
            ),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "user_response": self.user_response,
            "status": self.status.value if self.status else None,
        }
