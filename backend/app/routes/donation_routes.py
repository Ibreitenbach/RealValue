# backend/app/routes/donation_routes.py
# import datetime  # No longer needed here as timestamp is handled by model default
from flask import Blueprint, request, jsonify
from backend.app import db
from backend.app.models import Donation, User
from backend.app.utils.auth import token_required
from sqlalchemy.exc import IntegrityError

donation_bp = Blueprint("donation_routes", __name__, url_prefix="/api/donations")


@donation_bp.route("", methods=["POST"])
@token_required
def record_donation(current_user: User):
    """
    Records a new donation. Simulates a successful donation.
    Requires authentication.
    JSON Body:
    {
        "amount": 10.00,
        "currency": "USD",
        "is_anonymous": false (optional, default: false)
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    amount = data.get("amount")
    currency = data.get("currency")
    is_anonymous = data.get("is_anonymous", False)

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"message": "Amount must be a positive number"}), 400

    if not isinstance(currency, str) or not (
        2 < len(currency) < 5
    ):  # Basic check e.g. USD, EUR
        return (
            jsonify(
                {"message": "Currency must be a 3 or 4 letter string (e.g., USD, EUR)"}
            ),
            400,
        )

    if not isinstance(is_anonymous, bool):
        return jsonify({"message": "'is_anonymous' must be a boolean"}), 400

    try:
        donation = Donation(
            user_id=current_user.id,
            amount=float(amount),
            currency=currency.upper(),
            is_anonymous=is_anonymous,
            status="completed",  # As per requirements
            # timestamp is handled by model default
        )
        db.session.add(donation)
        db.session.commit()
        return jsonify(donation.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        # This might happen if a unique constraint is violated (e.g. transaction_id if we were using it)
        # For now, it's less likely with the current model structure for this endpoint.
        return jsonify({"message": "Database integrity error", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "An unexpected error occurred", "error": str(e)}),
            500,
        )


@donation_bp.route("/total", methods=["GET"])
def get_total_donations():
    """
    Returns the total amount of all completed donations.
    This endpoint is currently open.
    """
    try:
        # Summing up amounts for all 'completed' donations.
        # Using db.func.sum and filtering by status.
        total = (
            db.session.query(db.func.sum(Donation.amount))
            .filter(Donation.status == "completed")
            .scalar()
        )

        # If there are no donations, total will be None. Convert to 0.0 in that case.
        total_donations = total if total is not None else 0.0

        return jsonify({"total_donations": total_donations}), 200
    except Exception as e:
        # Log the exception e for debugging purposes if a logger is configured
        return (
            jsonify({"message": "Failed to retrieve total donations", "error": str(e)}),
            500,
        )
