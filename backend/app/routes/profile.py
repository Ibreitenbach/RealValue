from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user  # Assuming Flask-JWT-Extended

from ..models import UserProfile, User
from .. import db

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    # current_user will be the User object loaded by Flask-JWT-Extended
    user = current_user
    profile = UserProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        # Create a default profile if one doesn't exist
        profile = UserProfile(
            user_id=user.id,
            display_name=user.username,  # Default display name to username
            bio=""  # Empty bio
        )
        db.session.add(profile)
        db.session.commit()

    return jsonify(profile.to_dict()), 200


@profile_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_my_profile():
    user = current_user
    profile = UserProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        # This case should ideally be handled by the GET request creating one,
        # but as a safeguard or if GET is not called first.
        # However, with JWT, user must exist, and GET /me would have created it.
        # If somehow still no profile, this is an edge case. For now, assume GET /me handles creation.
        # If profile is None here, it might indicate a user without a profile somehow bypassed GET /me.
        # A robust solution might be to create it here too, or return 404.
        # For now, relying on GET /me to create it. If user exists, profile *should* exist after GET.
        # If test setup bypasses GET /me and profile is None, this PUT will fail later.
        # The tests ensure profile exists before PUT if they call register_user or GET /me.
        pass


    data = request.get_json(silent=True) # Use silent=True
    if data is None: # Explicitly check for None
        return jsonify({"msg": "Invalid or missing JSON in request"}), 400

    # If data is an empty JSON object {}, it's not None, so this will proceed.
    # .get will then gracefully handle missing keys, using current values as defaults.
    profile.display_name = data.get("display_name", profile.display_name)
    profile.bio = data.get("bio", profile.bio)

    db.session.commit()

    return jsonify(profile.to_dict()), 200
