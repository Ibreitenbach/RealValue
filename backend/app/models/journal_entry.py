# backend/app/models/journal_entry.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .. import db  # Assuming db is initialized in backend/app/__init__.py


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    prompt = Column(Text, nullable=True)
    reflection_tags = Column(
        Text, nullable=True
    )  # Storing as comma-separated string or JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_private = Column(Boolean, default=True, nullable=False)

    user = relationship("User", backref=db.backref("journal_entries", lazy=True))

    def __repr__(self):
        return f"<JournalEntry {self.id} (User: {self.user_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "prompt": self.prompt,
            "reflection_tags": self.reflection_tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_private": self.is_private,
        }
