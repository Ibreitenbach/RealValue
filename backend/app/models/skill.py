# backend/app/models/skill.py
from .. import db
from sqlalchemy import func


class Skill(db.Model):
    __tablename__ = "skill"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Relationships:
    # For ExchangeOffer.offered_skill
    offers_made = db.relationship(
        "ExchangeOffer",
        foreign_keys="ExchangeOffer.offered_skill_id",
        back_populates="offered_skill",
        lazy="dynamic",
    )
    # For ExchangeOffer.desired_skill
    offers_desired = db.relationship(
        "ExchangeOffer",
        foreign_keys="ExchangeOffer.desired_skill_id",
        back_populates="desired_skill",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Skill {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }
