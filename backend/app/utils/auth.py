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
        print("\n--- DEBUG: Custom @token_required called ---")
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        print(f"Token from header: {token}")

        if not token:
            print("Custom @token_required: Token is missing!")
            return jsonify({"message": "Token is missing!"}), 401

        try:
            print(f"Custom @token_required: Attempting to decode token with SECRET_KEY: {SECRET_KEY[:10]}...") # Print part of key for verification
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"Custom @token_required: Decoded data: {data}")
            current_user = User.query.get(data["user_id"])
            print(f"Custom @token_required: User from DB: {current_user.username if current_user else 'None'}")
            if not current_user:
                print("Custom @token_required: User not found for decoded ID.")
                return jsonify({"message": "Token is invalid or user not found!"}), 401
            g.current_user = (
                current_user  # Store user in Flask's g object for access in routes
            )
            print("Custom @token_required: User set in g.current_user")
        except jwt.ExpiredSignatureError as e:
            print(f"Custom @token_required: ExpiredSignatureError - {e}")
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError as e:
            print(f"Custom @token_required: InvalidTokenError - {e}")
            return jsonify({"message": "Token is invalid!"}), 401
        except Exception as e:
            print(f"Custom @token_required: Generic Exception - {type(e).__name__} - {e}")
            return jsonify({"message": f"Token processing error: {str(e)}"}), 401

        print("--- DEBUG: Custom @token_required successful ---")
        return f(
            current_user, *args, **kwargs
        )  # Pass current_user to the decorated function

    return decorated
