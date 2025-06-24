# backend/app/utils/auth.py
from functools import wraps
from flask import request, jsonify, g
import jwt  # PyJWT
from ..models import User  # Corrected import
import os

# In a real application, this key should be securely managed and consistent
# with the key used to issue tokens.
SECRET_KEY = os.getenv("SECRET_KEY", "a_default_secret_key_if_not_set")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("\n--- DEBUG: @token_required called ---")
        print(f"--- DEBUG: Request Headers: {request.headers}")
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            print(f"--- DEBUG: Auth Header: {auth_header}")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                print(f"--- DEBUG: Token extracted: {token}")
            else:
                print("--- DEBUG: Auth Header does not start with Bearer")
        else:
            print("--- DEBUG: No Authorization header found")

        if not token:
            print("--- DEBUG: No token found, returning 401 ---")
            return jsonify({"message": "Token is missing!"}), 401

        try:
            print(f"--- DEBUG: Attempting to decode token: {token}")
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"--- DEBUG: Token decoded data: {data}")
            current_user = User.query.get(data["user_id"]) # .get() is legacy, but let's keep for now to match original
            print(f"--- DEBUG: User from DB: {current_user.username if current_user else 'None'}")
            if not current_user:
                print("--- DEBUG: User not found from token user_id, returning 401 ---")
                return jsonify({"message": "Token is invalid or user not found!"}), 401

            # Instead of g.current_user, the decorator passes current_user as first arg
            # g.current_user = current_user
            print(f"--- DEBUG: @token_required successful, passing user: {current_user.username}")
        except jwt.ExpiredSignatureError:
            print("--- DEBUG: Token expired, returning 401 ---")
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            print("--- DEBUG: Token invalid, returning 401 ---")
            return jsonify({"message": "Token is invalid!"}), 401
        except Exception as e:
            print(f"--- DEBUG: Token processing error: {str(e)}, returning 401 ---")
            return jsonify({"message": f"Token processing error: {str(e)}"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
