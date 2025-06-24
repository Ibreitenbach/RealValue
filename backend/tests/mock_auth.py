# backend/tests/mock_auth.py
from functools import wraps
from flask import g, jsonify  # Ensure jsonify is imported
from backend.app.models import User
from backend.app import db  # Import db for session access

# Duplicate imports removed below


def mock_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # If g.current_user_id is not set or is None, simulate token missing/invalid
        if not hasattr(g, "current_user_id") or g.current_user_id is None:
            return jsonify({"message": "Token is missing or invalid"}), 401

        # Fetch the user fresh from the current session using the ID
        # Assumes an app context is active here, which Flask tests usually provide for routes.
current_user = db.session.get(User, g.current_user_id)  # Use Session.get for PK lookups
        if not current_user:
            # This case simulates a token for a user that no longer exists.
            return (
                jsonify(
                    {"message": f"User with id {g.current_user_id} not found"}
                ),  # Line-too-long can be fixed by black
                401,
            )

        # Store the fetched, session-bound user object in g for the route to use by convention,
        # although the route itself receives current_user as an argument.
        g.current_user = current_user

        return f(
            current_user, *args, **kwargs
        )  # Pass current_user to the decorated function

    return decorated


def get_mock_auth_token(user_id):  # Parameter changed for clarity, will be an ID
    """
    Generates a mock token string using a user ID.
    """
    # This is NOT a real JWT token, just a placeholder for header presence.
    return f"mock_token_for_user_{user_id}"
