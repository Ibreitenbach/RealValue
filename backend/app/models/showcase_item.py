from .. import db


class ShowcaseItem(db.Model):
    __tablename__ = "showcase_item"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    media_url = db.Column(
        db.String(255), nullable=True
    )  # Stores filename or path

    # User model relationship (User will have 'showcase_items')
    user = db.relationship("User", back_populates="showcase_items")

    def __init__(self, user_id, title, description=None, media_url=None):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.media_url = media_url

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "media_url": self.media_url,
        }

    def __repr__(self):
        return f"<ShowcaseItem {self.id}: {self.title}>"
