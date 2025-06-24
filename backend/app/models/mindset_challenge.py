# backend/app/models/mindset_challenge.py
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship
from .. import db


class MindsetChallengeFrequency(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ONE_TIME = "one-time"


class MindsetCompletionStatus(enum.Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    # PENDING = "pending" # If challenges can be in a pending state before completion


class MindsetChallengeTemplate(db.Model):
    __tablename__ = "mindset_challenge_templates"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(
        String(100), nullable=True
    )  # e.g., 'gratitude', 'reframing', 'stoicism'
    frequency = Column(SQLAlchemyEnum(MindsetChallengeFrequency), nullable=True)
    is_active = Column(db.Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    completions = relationship(
        "UserMindsetCompletion", back_populates="challenge_template"
    )

    def __repr__(self):
        return f"<MindsetChallengeTemplate {self.id}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "frequency": self.frequency.value if self.frequency else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserMindsetCompletion(db.Model):
    __tablename__ = "user_mindset_completions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    challenge_template_id = Column(
        Integer, ForeignKey("mindset_challenge_templates.id"), nullable=False
    )
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_reflection = Column(Text, nullable=True)
    status = Column(
        SQLAlchemyEnum(MindsetCompletionStatus),
        nullable=False,
        default=MindsetCompletionStatus.COMPLETED,
    )

    user = relationship("User", backref=db.backref("mindset_completions", lazy=True))
    challenge_template = relationship(
        "MindsetChallengeTemplate", back_populates="completions"
    )

    def __repr__(self):
        return f"<UserMindsetCompletion {self.id} (User: {self.user_id}, Challenge: {self.challenge_template_id}, Status: {self.status})>"

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
            "user_reflection": self.user_reflection,
            "status": self.status.value if self.status else None,
        }
