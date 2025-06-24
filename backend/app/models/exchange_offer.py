# backend/app/models/exchange_offer.py
from .. import db
from sqlalchemy import func
import enum


class OfferStatusEnum(enum.Enum):
    ACTIVE = "active"
    MATCHED = "matched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ExchangeOffer(db.Model):
    __tablename__ = "exchange_offer"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, index=True
    )
    offered_skill_id = db.Column(
        db.Integer, db.ForeignKey("skill.id"), nullable=False, index=True
    )
    desired_skill_id = db.Column(
        db.Integer, db.ForeignKey("skill.id"), nullable=True, index=True
    )  # Optional

    desired_description = db.Column(
        db.Text, nullable=False
    )  # E.g., "help moving", "any favor"
    description = db.Column(db.Text, nullable=True)  # Details about the offer

    status = db.Column(
        db.Enum(OfferStatusEnum), default=OfferStatusEnum.ACTIVE, nullable=False
    )
    location_preference = db.Column(
        db.String(100), nullable=True
    )  # E.g., "local", "remote"

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # noqa: E501
    )

    # Relationships
    user = db.relationship(
        "User", backref=db.backref("exchange_offers", lazy="dynamic")
    )
    offered_skill = db.relationship(
        "Skill", foreign_keys=[offered_skill_id], back_populates="offers_made"
    )
    desired_skill = db.relationship(
        "Skill", foreign_keys=[desired_skill_id], back_populates="offers_desired"
    )

    def __repr__(self):
        return f"<ExchangeOffer id={self.id} user_id={self.user_id} offered_skill_id={self.offered_skill_id} status='{self.status.value}'>"  # noqa: E501

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user": (self.user.username if self.user else None),  # User's username
            "offered_skill_id": self.offered_skill_id,
            "offered_skill_name": (
                self.offered_skill.name if self.offered_skill else None
            ),  # Offered skill  # noqa: E501
            "desired_skill_id": self.desired_skill_id,
            "desired_skill_name": (
                self.desired_skill.name if self.desired_skill else None
            ),  # Desired skill name
            "desired_description": self.desired_description,
            "description": self.description,
            "status": self.status.value,
            "location_preference": self.location_preference,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),  # ISO format
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),  # ISO format
        }
