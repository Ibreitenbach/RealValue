import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from .. import db
from ..models import User, ShowcaseItem

showcase_bp = Blueprint(
    "showcase_bp", __name__, url_prefix="/api/showcase_items"
)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@showcase_bp.route("", methods=["POST"])
@jwt_required()
def create_showcase_item():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.form
    title = data.get("title")
    description = data.get("description")

    if not title:
        return jsonify({"msg": "Title is required"}), 400

    media_filename = None
    if "media_file" in request.files:
        file = request.files["media_file"]
        if file.filename == "":
            pass  # No file selected
        elif file and allowed_file(file.filename):
            # Secure filename and add UUID to prevent collisions
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"

            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], unique_filename
            )
            try:
                file.save(file_path)
                media_filename = unique_filename  # Store only the filename
            except Exception as e:
                current_app.logger.error(f"Failed to save file: {e}")
                return jsonify({"msg": "Failed to save media file"}), 500
        else:
            return jsonify({"msg": "File type not allowed"}), 400

    new_item = ShowcaseItem(
        user_id=user.id,
        title=title,
        description=description,
        media_url=media_filename,
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201


@showcase_bp.route("", methods=["GET"])
@jwt_required()
def get_showcase_items():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    items = ShowcaseItem.query.filter_by(user_id=user.id).all()
    return jsonify([item.to_dict() for item in items]), 200


@showcase_bp.route("/<int:item_id>", methods=["GET"])
@jwt_required()
def get_showcase_item(item_id):
    current_user_id = get_jwt_identity()
    item = ShowcaseItem.query.filter_by(
        id=item_id, user_id=current_user_id
    ).first()
    if not item:
        return (
            jsonify({"msg": "Showcase item not found or access denied"}),
            404,
        )
    return jsonify(item.to_dict()), 200


@showcase_bp.route("/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_showcase_item(item_id):
    current_user_id = get_jwt_identity()
    item = ShowcaseItem.query.filter_by(
        id=item_id, user_id=current_user_id
    ).first()
    if not item:
        return (
            jsonify({"msg": "Showcase item not found or access denied"}),
            404,
        )

    data = request.form
    item.title = data.get("title", item.title)
    item.description = data.get("description", item.description)

    if "media_file" in request.files:
        file = request.files["media_file"]
        if file.filename == "":
            # No new file uploaded, retain existing media_url unless explicitly cleared
            if data.get("clear_media_file") == "true":  # Optional: media clear # noqa: E501
                # Delete old file if it exists
                if item.media_url:
                    old_file_path = os.path.join(
                        current_app.config["UPLOAD_FOLDER"], item.media_url
                    )
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except Exception as e:
                            current_app.logger.error(
                                f"Error deleting old file {item.media_url}: {e}"
                            )
                item.media_url = None
        elif file and allowed_file(file.filename):
            # Delete old file if it exists
            if item.media_url:
                old_file_path = os.path.join(
                    current_app.config["UPLOAD_FOLDER"], item.media_url
                )
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except Exception as e:
                        current_app.logger.error(
                            f"Error deleting old file {item.media_url}: {e}"
                        )

            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit(".", 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            upload_dir = current_app.config["UPLOAD_FOLDER"]
            file_path = os.path.join(upload_dir, unique_filename)  # noqa: E501
            try:
                file.save(file_path)
                item.media_url = unique_filename
            except Exception as e:
                current_app.logger.error(f"Failed to save updated file: {e}")
                return (
                    jsonify({"msg": "Failed to save updated media file"}),
                    500,
                )
        else:
            return jsonify({"msg": "New file type not allowed"}), 400
    elif (
        data.get("clear_media_file") == "true" and item.media_url
    ):  # Handle case where media is cleared without new file
        old_file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], item.media_url
        )
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except Exception as e:
                current_app.logger.error(
                    f"Error deleting old file {item.media_url}: {e}"
                )
        item.media_url = None

    db.session.commit()
    return jsonify(item.to_dict()), 200


@showcase_bp.route("/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_showcase_item(item_id):
    current_user_id = get_jwt_identity()
    item = ShowcaseItem.query.filter_by(
        id=item_id, user_id=current_user_id
    ).first()
    if not item:
        return (
            jsonify({"msg": "Showcase item not found or access denied"}),
            404,
        )

    # Delete the associated media file if it exists
    if item.media_url:
        file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], item.media_url
        )
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                current_app.logger.error(
                    f"Error deleting file {item.media_url}: {e}"
                )
                # Decide if you want to halt deletion or just log

    db.session.delete(item)
    db.session.commit()
    return jsonify({"msg": "Showcase item deleted successfully"}), 200
