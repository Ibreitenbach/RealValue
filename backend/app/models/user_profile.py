from .. import db


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True
    )
    display_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile {self.display_name or self.user.username}>"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "bio": self.bio,
        }
