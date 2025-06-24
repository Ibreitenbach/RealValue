# backend/app/models/donation.py
import datetime  # Ensure datetime is imported for datetime.UTC
from .. import db

# Unused imports removed:
# from sqlalchemy.dialects.postgresql import (
# UUID,
# )
# import uuid


class Donation(db.Model):
    __tablename__ = "donation"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # e.g., 'USD', 'EUR'
    timestamp = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.datetime.now(datetime.UTC)
    )
    # Using String for transaction_id as it could be from various gateways
    transaction_id = db.Column(db.String(255), nullable=True, unique=True)
    is_anonymous = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(
        db.String(50), nullable=False, default="completed"
    )  # e.g., 'completed', 'pending', 'failed'

    # Relationships
    user = db.relationship("User", backref=db.backref("donations", lazy=True))

    def __init__(
        self,
        amount,
        currency,
        user_id=None,
        transaction_id=None,
        is_anonymous=False,
        status="completed",
    ):
        self.amount = amount
        self.currency = currency
        self.user_id = user_id
        self.transaction_id = transaction_id
        self.is_anonymous = is_anonymous
        self.status = status
        # Timestamp is handled by default

    def __repr__(self):
        return f"<Donation {self.id} - {self.amount} {self.currency} by User {self.user_id if self.user_id else 'Anonymous'}>"

    def to_dict(self):
        username = "Anonymous"
        if self.user and not self.is_anonymous:
            username = self.user.username

        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "transaction_id": self.transaction_id,
            "is_anonymous": self.is_anonymous,
            "status": self.status,
            "user_username": username,
        }
