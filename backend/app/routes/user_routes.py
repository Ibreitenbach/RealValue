# backend/app/routes/user_routes.py
from flask import Blueprint, jsonify, g  # noqa: F401
from backend.app.models import UserChallengeCompletion
from backend.app.utils.auth import token_required

user_bp = Blueprint("user_routes", __name__, url_prefix="/api/users")


@user_bp.route("/me/challenge_completions", methods=["GET"])
@token_required
def get_my_challenge_completions(current_user):
    """
    Returns a list of all UserChallengeCompletion records for the authenticated user.
    """
    completions = UserChallengeCompletion.query.filter_by(user_id=current_user.id).all()
    return jsonify([completion.to_dict() for completion in completions]), 200
