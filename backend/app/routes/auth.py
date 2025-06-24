from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..models import User, UserProfile
from .. import db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if (
        not data
        or not data.get("username")
        or not data.get("email")
        or not data.get("password")
    ):
        return jsonify({"msg": "Missing username, email, or password"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "Username already exists"}), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email already exists"}), 409

    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()  # Commit to get user ID

    # Create a default profile upon registration
    # This fulfills part of the testing requirement: "ensure a default profile is created upon new user registration"
    user_profile = UserProfile(
        user_id=new_user.id,
        display_name=new_user.username,  # Default display name
        bio="",  # Empty bio
    )
    db.session.add(user_profile)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))  # Cast to string
    return (
        jsonify(
            access_token=access_token, user_id=new_user.id, username=new_user.username
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity=str(user.id))  # Cast to string
        # Ensure profile exists, create if not (e.g., for users created before profile system)
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id, display_name=user.username, bio="")
            db.session.add(profile)
            db.session.commit()
        return (
            jsonify(access_token=access_token, user_id=user.id, username=user.username),
            200,
        )

    return jsonify({"msg": "Bad username or password"}), 401
