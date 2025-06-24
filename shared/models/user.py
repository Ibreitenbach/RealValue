# shared/models/user.py
from typing import TypedDict


# Renamed from SharedUserProfile and simplified.
# This represents basic user information, often obtained from auth context.
class SharedUser(TypedDict):
    """
    Defines the common structure for basic User information.
    Typically, this would come from an authentication token's claims or a user endpoint.
    """

    id: int  # Assuming user ID is an integer, matching backend User model
    username: str
    email: str


# Example usage (not strictly necessary for TypedDict, but shows intent):
# def create_shared_user(id: int, username: str, email: str) -> SharedUser:
#     return SharedUser(id=id, username=username, email=email)

# The old class based approach:
# class SharedUser:
#     """
#     Defines the common structure for basic User information.
#     """
#     def __init__(self, id: int, username: str, email: str):
#         self.id = id
#         self.username = username
#         self.email = email

#     def to_dict(self) -> dict[str, any]:
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#         }
