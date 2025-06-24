# backend/app/routes/practice_challenges.py
from flask import Blueprint, jsonify, request, g  # noqa: F401
from datetime import datetime
from backend.app import db  # Import db from backend.app
from backend.app.models import (  # Import models from backend.app.models
    PracticeChallengeTemplate,
    UserChallengeCompletion,
    # ChallengeType, # Removed as it's unused
    DifficultyLevel,
    CompletionStatus,
)
from ..utils.auth import token_required  # Import auth utils from .. (parent directory)

practice_challenges_bp = Blueprint(
    "practice_challenges", __name__, url_prefix="/api/practice_challenges"
)


@practice_challenges_bp.route("/templates", methods=["GET"])
@token_required
def get_practice_challenge_templates(current_user):
    """
    Returns a list of all active PracticeChallengeTemplates.
    Supports filtering by associated_skill_id or difficulty.
    """
    query = PracticeChallengeTemplate.query.filter_by(is_active=True)

    associated_skill_id = request.args.get("associated_skill_id")
    difficulty_str = request.args.get("difficulty")

    if associated_skill_id:
        try:
            query = query.filter_by(associated_skill_id=int(associated_skill_id))
        except ValueError:
            return jsonify({"message": "Invalid associated_skill_id format"}), 400

    if difficulty_str:
        try:
            difficulty_enum = DifficultyLevel[difficulty_str.upper()]
            query = query.filter_by(difficulty=difficulty_enum)
        except KeyError:
            return (
                jsonify(
                    {
                        "message": f"Invalid difficulty level: {difficulty_str}. Supported values: EASY, MEDIUM, HARD"
                    }
                ),
                400,
            )

    templates = query.all()
    return jsonify([template.to_dict() for template in templates]), 200


@practice_challenges_bp.route("/templates/<int:template_id>", methods=["GET"])
@token_required
def get_practice_challenge_template_detail(current_user, template_id):
    """
    Returns details for a specific PracticeChallengeTemplate.
    """
    template = PracticeChallengeTemplate.query.get(template_id)
    if not template:
        return jsonify({"message": "PracticeChallengeTemplate not found"}), 404

    # Optionally, you might want to check if it's active, depending on requirements
    # if not template.is_active:
    #     return jsonify({"message": "PracticeChallengeTemplate is not active"}), 404

    return jsonify(template.to_dict()), 200


@practice_challenges_bp.route("/complete", methods=["POST"])
@token_required
def complete_practice_challenge(current_user):
    """
    Allows an authenticated user to submit a UserChallengeCompletion
    for a specific PracticeChallengeTemplate.
    """
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body is missing"}), 400

    challenge_template_id = data.get("challenge_template_id")
    user_response = data.get("user_response")  # Optional, depending on challenge type

    if not challenge_template_id:
        return jsonify({"message": "challenge_template_id is required"}), 400

    template = PracticeChallengeTemplate.query.get(challenge_template_id)
    if not template:
        return jsonify({"message": "PracticeChallengeTemplate not found"}), 404

    if not template.is_active:
        return jsonify({"message": "Cannot complete an inactive challenge"}), 400

    # TODO: Add more validation based on challenge_type.
    # For example, if challenge_type is PHOTO_UPLOAD, user_response (URL) might be mandatory.
    # If TEXT_RESPONSE, user_response (text) might be mandatory.

    # For now, we'll assume a default status.
    # In a more complex system, status might be 'pending_review' initially.
    completion_status = CompletionStatus.COMPLETED  # Defaulting to COMPLETED for now

    new_completion = UserChallengeCompletion(
        user_id=current_user.id,
        challenge_template_id=template.id,
        user_response=user_response,
        status=completion_status,
        completed_at=datetime.utcnow(),  # Mark as completed now
    )

    db.session.add(new_completion)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return (
            jsonify(
                {"message": "Failed to save challenge completion", "error": str(e)}
            ),
            500,
        )

    return jsonify(new_completion.to_dict()), 201
