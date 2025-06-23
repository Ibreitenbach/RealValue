# backend/app/utils/auth.py
from functools import wraps
from flask import request, jsonify, g
import jwt  # PyJWT
from backend.app.models import User  # Assuming User model can be imported like this
import os

# In a real application, this key should be securely managed and consistent
# with the key used to issue tokens.
SECRET_KEY = os.getenv("SECRET_KEY", "a_default_secret_key_if_not_set")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # In a real app, you'd verify the token signature and expiration
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                return jsonify({"message": "Token is invalid or user not found!"}), 401
            g.current_user = (
                current_user  # Store user in Flask's g object for access in routes
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401
        except Exception as e:
            return jsonify({"message": f"Token processing error: {str(e)}"}), 401

        return f(
            current_user, *args, **kwargs
        )  # Pass current_user to the decorated function

    return decorated
