# backend/app/models/mindful_moment.py
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
    Time,
)
from sqlalchemy.orm import relationship
from .. import db


class MindfulMomentReminderFrequency(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SPECIFIC_TIME = "specific_time"


class MindfulMomentTemplate(db.Model):
    __tablename__ = "mindful_moment_templates"

    id = Column(Integer, primary_key=True)
    text = Column(
        Text, nullable=False
    )  # e.g., "Be a rock," "Find one unexpected beauty"
    category = Column(
        String(100), nullable=True
    )  # e.g., 'gratitude', 'focus', 'breathing'
    is_active = Column(db.Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_settings = relationship(
        "UserReminderSetting", back_populates="mindful_moment_template"
    )

    def __repr__(self):
        return f"<MindfulMomentTemplate {self.id}: {self.text[:50]}>"

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserReminderSetting(db.Model):
    __tablename__ = "user_reminder_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    mindful_moment_template_id = Column(
        Integer, ForeignKey("mindful_moment_templates.id"), nullable=False
    )
    frequency = Column(SQLAlchemyEnum(MindfulMomentReminderFrequency), nullable=False)
    time_of_day = Column(Time, nullable=True)  # Optional, for specific_time frequency
    is_enabled = Column(db.Boolean, default=True, nullable=False)

    user = relationship("User", backref=db.backref("reminder_settings", lazy=True))
    mindful_moment_template = relationship(
        "MindfulMomentTemplate", back_populates="user_settings"
    )

    def __repr__(self):
        return f"<UserReminderSetting {self.id} (User: {self.user_id}, Template: {self.mindful_moment_template_id}, Enabled: {self.is_enabled})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mindful_moment_template_id": self.mindful_moment_template_id,
            "template_text": (
                self.mindful_moment_template.text
                if self.mindful_moment_template
                else None
            ),
            "frequency": self.frequency.value if self.frequency else None,
            "time_of_day": self.time_of_day.isoformat() if self.time_of_day else None,
            "is_enabled": self.is_enabled,
        }
