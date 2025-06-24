# shared/models/profile.py
from typing import Optional, TypedDict


class SharedUserProfileData(TypedDict, total=False):
    """
    Defines the structure for user profile data that is typically displayed
    or edited. Matches the backend UserProfile.to_dict() structure.
    `user_id` is often implicit in context (e.g. /api/profile/me) but can be present.
    """

    user_id: Optional[int]  # Read-only, from backend
    display_name: Optional[str]
    bio: Optional[str]


class SharedUserProfileUpdatePayload(TypedDict, total=False):
    """
    Defines the structure for updating a user's profile.
    Frontend will send this. All fields are optional for partial updates.
    """

    display_name: Optional[str]
    bio: Optional[str]


# For frontend convenience, we can also define a class if needed,
# but TypedDict is often sufficient for API data contracts.
# Example class if state management or methods were needed on frontend:
# class ProfileData:
#     def __init__(self, user_id: Optional[int], display_name: Optional[str], bio: Optional[str]):
#         self.user_id = user_id
#         self.display_name = display_name
#         self.bio = bio

#     @staticmethod
#     def from_dict(data: SharedUserProfileData) -> 'ProfileData':
#         return ProfileData(
#             user_id=data.get('user_id'),
#             display_name=data.get('display_name'),
#             bio=data.get('bio')
#         )

#     def to_update_payload(self) -> SharedUserProfileUpdatePayload:
#         payload: SharedUserProfileUpdatePayload = {}
#         if self.display_name is not None:
#             payload['display_name'] = self.display_name
#         if self.bio is not None:
#             payload['bio'] = self.bio
#         return payload
