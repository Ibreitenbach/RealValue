# backend/tests/mock_auth.py
from functools import wraps
from flask import g
from backend.app.models import User
from backend.app import db  # Import db for session access


def mock_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "current_user_id") or g.current_user_id is None:
            # This is a fallback if a test doesn't explicitly set g.current_user_id.
            # Tests SHOULD set g.current_user_id for clarity.
            # print("Warning: g.current_user_id not set by test, attempting fallback in mock_token_required.")

            # Query within the current app/session context, provided by Flask test runner for routes
            default_user = User.query.first()
            if not default_user:
                raise RuntimeError(
                    "mock_token_required: No user found in DB for fallback "
                    "and g.current_user_id was not set by the test."
                )
            g.current_user_id = default_user.id

        # Fetch the user fresh from the current session using the ID
        # Assumes an app context is active here, which Flask tests usually provide for routes.
        current_user = db.session.get(User, g.current_user_id)  # Use Session.get for PK lookups
        if not current_user:
            raise RuntimeError(
                f"mock_token_required: User with id {g.current_user_id} "
                "not found in the current session."
            )

        # Store the fetched, session-bound user object in g for the route to use
        g.current_user = current_user

        return f(current_user, *args, **kwargs)  # Pass current_user to the decorated function

    return decorated


def get_mock_auth_token(user_id):  # Parameter changed for clarity, will be an ID
    """
    Generates a mock token string using a user ID.
    """
    # This is NOT a real JWT token, just a placeholder for header presence.
    return f"mock_token_for_user_{user_id}"
