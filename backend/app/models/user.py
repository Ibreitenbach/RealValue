# backend/app/models/user.py
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length for stronger hashes

    profile = db.relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    # Relationship to ShowcaseItem for media uploads feature
    showcase_items = db.relationship(
        "ShowcaseItem",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # Add relationships for other models where User is a foreign key
    # For example:
    # exchange_offers = db.relationship('ExchangeOffer', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    # posts = db.relationship('Post', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    # favors_given = db.relationship('Favor', foreign_keys='Favor.giver_id', back_populates='giver', lazy='dynamic')
    # favors_received = db.relationship('Favor', foreign_keys='Favor.receiver_id', back_populates='receiver', lazy='dynamic')
    # circles_created = db.relationship('Circle', back_populates='creator', lazy='dynamic')
    # circle_memberships = db.relationship('CircleMember', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    # endorsements_given = db.relationship('Endorsement', foreign_keys='Endorsement.endorser_id', back_populates='endorser', lazy='dynamic')
    # endorsements_received = db.relationship('Endorsement', foreign_keys='Endorsement.endorsee_id', back_populates='endorsee', lazy='dynamic')
    # journal_entries = db.relationship('JournalEntry', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    # mindset_completions = db.relationship('UserMindsetCompletion', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    # reminder_settings = db.relationship('UserReminderSetting', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    # donations = db.relationship('Donation', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    # events_created = db.relationship('Event', back_populates='creator', lazy='dynamic', cascade='all, delete-orphan')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

   
