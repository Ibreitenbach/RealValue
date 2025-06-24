# backend/app/routes/user_routes.py
from flask import Blueprint, jsonify, request  # Removed g
from backend.app.models import (
    UserChallengeCompletion,
    ExchangeOffer,
    OfferStatusEnum,
    User,  # noqa: F401 # Used for type hinting current_user
)  # Added ExchangeOffer, OfferStatusEnum, User
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


@user_bp.route("/me/exchange_offers", methods=["GET"])
@token_required
def get_my_exchange_offers(current_user: User):  # Added User type hint back for clarity
    """
    Returns a list of all ExchangeOffer records created by the authenticated user.
    """
    # Pagination can be added here if expecting many offers per user
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)  # Or a different default

    user_offers_query = ExchangeOffer.query.filter_by(user_id=current_user.id)

    # Optional: filter by status for the user's own offers
    status_filter = request.args.get("status")
    if status_filter:
        try:
            status_enum = OfferStatusEnum[
                status_filter.upper()
            ]  # Assuming OfferStatusEnum is available
            user_offers_query = user_offers_query.filter(
                ExchangeOffer.status == status_enum
            )
        except KeyError:
            # Silently ignore invalid status filters or return an error
            pass

    paginated_offers = user_offers_query.order_by(
        ExchangeOffer.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    offers = [offer.to_dict() for offer in paginated_offers.items]

    return (  # noqa: E501
        jsonify(
            {
                "offers": offers,
                "total": paginated_offers.total,
                "pages": paginated_offers.pages,
                "current_page": paginated_offers.page,
            }
        ),
        200,
    )
