# shared/models/user.py
from typing import Optional

class SharedUserProfile:
    """
    Defines the common structure for a User Profile,
    to be used by both frontend and backend.
    """
    def __init__(self, id: str, username: str, email: str, bio: Optional[str] = None):
        self.id = id
        self.username = username
        self.email = email
        self.bio = bio

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "bio": self.bio
        }