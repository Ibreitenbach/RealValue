# backend/app/routes/exchange_routes.py
from flask import Blueprint, request, jsonify
from .. import db  # Import db from the app package level
from ..models import Skill, ExchangeOffer, User, OfferStatusEnum  # Import models
from ..utils.auth import token_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

exchange_bp = Blueprint("exchange_bp", __name__, url_prefix="/api/exchange_offers")


@exchange_bp.route("", methods=["POST"])
@token_required
def create_exchange_offer(current_user: User):
    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid JSON payload"}), 400

    required_fields = ["offered_skill_id", "desired_description"]
    missing_fields = [
        field for field in required_fields if field not in data or data[field] is None
    ]
    if missing_fields:
        return (  # noqa: E501
            jsonify(
                {"message": f"Missing required fields: {', '.join(missing_fields)}"}
            ),
            400,
        )

    offered_skill_id = data.get("offered_skill_id")
    desired_skill_id = data.get("desired_skill_id")  # Optional
    desired_description = data.get("desired_description")
    description = data.get("description")
    location_preference = data.get("location_preference")
    status_str = data.get("status", "active")  # Default to active

    # Validate offered_skill_id
    if not isinstance(offered_skill_id, int):
        return jsonify({"message": "offered_skill_id must be an integer"}), 400
    offered_skill = Skill.query.get(offered_skill_id)
    if not offered_skill:
        return (  # noqa: E501
            jsonify({"message": f"Offered skill with id {offered_skill_id} not found"}),
            404,
        )

    # Validate desired_skill_id if provided
    if desired_skill_id is not None:
        if not isinstance(desired_skill_id, int):
            return (  # noqa: E501
                jsonify({"message": "desired_skill_id must be an integer if provided"}),
                400,
            )
        desired_skill = Skill.query.get(desired_skill_id)
        if not desired_skill:
            return (  # noqa: E501
                jsonify(
                    {"message": f"Desired skill with id {desired_skill_id} not found"}
                ),
                404,
            )

    # Validate status
    try:
        status_enum = OfferStatusEnum(status_str.lower())
    except ValueError:
        valid_statuses = [s.value for s in OfferStatusEnum]
        return (  # noqa: E501
            jsonify(
                {
                    "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                }
            ),
            400,
        )

    new_offer = ExchangeOffer(
        user_id=current_user.id,
        offered_skill_id=offered_skill_id,
        desired_skill_id=desired_skill_id,
        desired_description=desired_description,
        description=description,
        status=status_enum,
        location_preference=location_preference,
    )

    try:
        db.session.add(new_offer)
        db.session.commit()
        return jsonify(new_offer.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        return (
            jsonify({"message": "Database integrity error", "error": str(e)}),
            500,
        )  # noqa: E501
    except Exception as e:
        db.session.rollback()
        return (  # noqa: E501
            jsonify({"message": "Could not create exchange offer", "error": str(e)}),
            500,
        )


@exchange_bp.route("", methods=["GET"])
@token_required
def get_exchange_offers(current_user: User):
    query = ExchangeOffer.query.filter(ExchangeOffer.status == OfferStatusEnum.ACTIVE)

    # Filtering
    offered_skill_id = request.args.get("offered_skill_id", type=int)
    if offered_skill_id:
        query = query.filter(ExchangeOffer.offered_skill_id == offered_skill_id)

    desired_skill_id = request.args.get("desired_skill_id", type=int)
    if desired_skill_id:
        query = query.filter(ExchangeOffer.desired_skill_id == desired_skill_id)

    # Keyword search
    search_term = request.args.get("search")
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                ExchangeOffer.description.ilike(search_pattern),
                ExchangeOffer.desired_description.ilike(search_pattern),
                Skill.name.ilike(search_pattern),  # Search in offered skill name
            )
        ).join(
            ExchangeOffer.offered_skill
        )  # Join to search in skill name

    # Future: Add location filtering here

    # Pagination (optional, but good practice for lists)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    paginated_offers = query.order_by(ExchangeOffer.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

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


@exchange_bp.route("/<int:offer_id>", methods=["GET"])
@token_required
def get_exchange_offer_detail(current_user: User, offer_id: int):
    offer = ExchangeOffer.query.get_or_404(offer_id)
    return jsonify(offer.to_dict()), 200


@exchange_bp.route("/<int:offer_id>", methods=["PUT"])
@token_required
def update_exchange_offer(current_user: User, offer_id: int):
    offer = ExchangeOffer.query.get_or_404(offer_id)

    if offer.user_id != current_user.id:
        return jsonify({"message": "Not authorized to update this offer"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON payload"}), 400

    # Update fields if provided in the payload
    if "offered_skill_id" in data:
        new_offered_skill_id = data["offered_skill_id"]
        if not isinstance(new_offered_skill_id, int):
            return jsonify({"message": "offered_skill_id must be an integer"}), 400
        offered_skill = Skill.query.get(new_offered_skill_id)
        if not offered_skill:
            return (  # noqa: E501
                jsonify(
                    {
                        "message": f"Offered skill with id {new_offered_skill_id} not found"
                    }
                ),
                404,
            )
        offer.offered_skill_id = new_offered_skill_id

    if "desired_skill_id" in data:  # Allows setting to null or a new ID
        new_desired_skill_id = data["desired_skill_id"]
        if new_desired_skill_id is not None:
            if not isinstance(new_desired_skill_id, int):
                return (  # noqa: E501
                    jsonify(
                        {"message": "desired_skill_id must be an integer if provided"}
                    ),
                    400,
                )
            desired_skill = Skill.query.get(new_desired_skill_id)
            if not desired_skill:
                return (  # noqa: E501
                    jsonify(
                        {
                            "message": f"Desired skill with id {new_desired_skill_id} not found"
                        }
                    ),
                    404,
                )
        offer.desired_skill_id = new_desired_skill_id

    if "desired_description" in data:
        if (
            data["desired_description"] is None
            or data["desired_description"].strip() == ""
        ):
            return jsonify({"message": "desired_description cannot be empty"}), 400
        offer.desired_description = data["desired_description"]

    if "description" in data:
        offer.description = data["description"]  # Allow empty or null

    if "location_preference" in data:
        offer.location_preference = data["location_preference"]  # Allow empty or null

    if "status" in data:
        try:
            status_enum = OfferStatusEnum(data["status"].lower())
            offer.status = status_enum
        except ValueError:
            valid_statuses = [s.value for s in OfferStatusEnum]
            return (  # noqa: E501
                jsonify(
                    {
                        "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                    }
                ),
                400,
            )

    try:
        db.session.commit()
        return jsonify(offer.to_dict()), 200
    except IntegrityError as e:
        db.session.rollback()
        return (  # noqa: E501
            jsonify(
                {"message": "Database integrity error during update", "error": str(e)}
            ),
            500,
        )
    except Exception as e:
        db.session.rollback()
        return (  # noqa: E501
            jsonify({"message": "Could not update exchange offer", "error": str(e)}),
            500,
        )


@exchange_bp.route("/<int:offer_id>", methods=["DELETE"])
@token_required
def delete_exchange_offer(current_user: User, offer_id: int):
    offer = ExchangeOffer.query.get_or_404(offer_id)

    if offer.user_id != current_user.id:
        return jsonify({"message": "Not authorized to delete this offer"}), 403

    try:
        db.session.delete(offer)
        db.session.commit()
        return jsonify({"message": "Exchange offer deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return (  # noqa: E501
            jsonify({"message": "Could not delete exchange offer", "error": str(e)}),
            500,
        )
