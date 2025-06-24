# backend/app/routes/mind_progress_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services import analysis_service

# Assuming a utility for @token_required if it's different from @jwt_required
# For now, standard @jwt_required will be used, and we get user_id from get_jwt_identity()
# If you have a custom @token_required that injects current_user, that's also fine.

mind_progress_bp = Blueprint(
    "mind_progress_routes", __name__, url_prefix="/api/users/me/mind_progress"
)


@mind_progress_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_summary():
    """
    GET /api/users/me/mind_progress/summary
    Returns a high-level summary of mind progress for the authenticated user.
    """
    user_id_str = get_jwt_identity()
    try:
        user_id = int(user_id_str)
    except ValueError:
        return jsonify({"message": "Invalid user identity in token"}), 400

    summary_data = analysis_service.get_mind_progress_summary(user_id)
    return jsonify(summary_data), 200


@mind_progress_bp.route("/journaling_trends", methods=["GET"])
@jwt_required()
def get_journaling_trends():
    """
    GET /api/users/me/mind_progress/journaling_trends
    Returns data suitable for charting journaling consistency.
    Accepts 'period' query parameter ('weekly' or 'monthly', defaults to 'weekly').
    e.g., [{ "date": "YYYY-MM-DD", "count": N }, ...]
    """
    user_id_str = get_jwt_identity()
    try:
        user_id = int(user_id_str)
    except ValueError:
        return jsonify({"message": "Invalid user identity in token"}), 400

    time_period = request.args.get("period", "weekly").lower()
    if time_period not in ["weekly", "monthly"]:
        return (
            jsonify(
                {"message": "Invalid 'period' parameter. Use 'weekly' or 'monthly'."}
            ),
            400,
        )

    trends_data = analysis_service.get_journaling_consistency(user_id, time_period)
    return jsonify(trends_data), 200


@mind_progress_bp.route("/challenge_trends", methods=["GET"])
@jwt_required()
def get_challenge_trends():
    """
    GET /api/users/me/mind_progress/challenge_trends
    Returns data for challenge completion trends.
    e.g., [{ "category": "Stoicism", "completed_count": N, "month": "YYYY-MM" }, ...]
    """
    user_id_str = get_jwt_identity()
    try:
        user_id = int(user_id_str)
    except ValueError:
        return jsonify({"message": "Invalid user identity in token"}), 400

    trends_data = analysis_service.get_challenge_completion_rate(user_id)
    return jsonify(trends_data), 200


@mind_progress_bp.route("/tag_analysis", methods=["GET"])
@jwt_required()
def get_tag_analysis_trends():
    """
    GET /api/users/me/mind_progress/tag_analysis
    Returns data for journal entry tag analysis.
    e.g., {"gratitude": 10, "reframing": 5}
    """
    user_id_str = get_jwt_identity()
    try:
        user_id = int(user_id_str)
    except ValueError:
        return jsonify({"message": "Invalid user identity in token"}), 400

    tag_data = analysis_service.get_tag_analysis(user_id)
    return jsonify(tag_data), 200
