# backend/app/utils/auth.py
from functools import wraps
from flask import request, jsonify, g # Ensure g is imported for consistency if needed by other parts of the app
import jwt  # PyJWT
from ..models import User
import os

# In a real application, this key should be securely managed and consistent
# with the key used to issue tokens.
SECRET_KEY = os.getenv("SECRET_KEY", "a_default_secret_key_if_not_set")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("\n--- DEBUG: @token_required called ---") # From main and feat
        print(f"--- DEBUG: Request Headers: {request.headers}") # From main

        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            print(f"--- DEBUG: Auth Header: {auth_header}") # From feat
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                print(f"--- DEBUG: Token extracted: {token}") # From main
            else: # From main
                print("--- DEBUG: Auth Header does not start with Bearer") # From main
        else: # From main
            print("--- DEBUG: No Authorization header found") # From main

        if not token:
            print("--- DEBUG: No token found, returning 401 ---") # From main
            return jsonify({"message": "Token is missing!"}), 401

        try:
            print(f"--- DEBUG: Attempting to decode token: {token}") # From main
            # Keep the detailed print with partial key for verification from feat branch
            print(f"Custom @token_required: Attempting to decode token with SECRET_KEY: {SECRET_KEY[:10]}...") # From feat
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"--- DEBUG: Token decoded data: {data}") # From main

            # Keep User.query.get for now as it matches the main branch's context
            current_user = User.query.get(data["user_id"])
            print(f"--- DEBUG: User from DB: {current_user.username if current_user else 'None'}") # From main
            if not current_user:
                print("--- DEBUG: User not found from token user_id, returning 401 ---") # From main
                return jsonify({"message": "Token is invalid or user not found!"}), 401
            
            # The decorator is expected to pass current_user as the first argument,
            # so setting g.current_user here is optional unless needed by other parts of the app.
            # However, `g.current_user` is often set for broader context access.
            g.current_user = current_user # Keep g.current_user for broader context access if needed
            print("Custom @token_required: User set in g.current_user") # From feat

            print(f"--- DEBUG: @token_required successful, passing user: {current_user.username}") # From main
        except jwt.ExpiredSignatureError as e: # Catch specific exception for better logging from feat
            print(f"--- DEBUG: Token expired, returning 401 --- ({e})") # From main, added exception detail
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError as e: # Catch specific exception for better logging from feat
            print(f"--- DEBUG: Token invalid, returning 401 --- ({e})") # From main, added exception detail
            return jsonify({"message": "Token is invalid!"}), 401
        except Exception as e: # Generic exception handling from feat
            print(f"--- DEBUG: Token processing error: {type(e).__name__} - {e}, returning 401 ---") # Combined from both
            return jsonify({"message": f"Token processing error: {str(e)}"}), 401

        return f(current_user, *args, **kwargs) # Pass current_user to the decorated function

    return decorated