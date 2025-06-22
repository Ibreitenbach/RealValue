# backend/app/routes/health.py
import datetime
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def health_check():
    """
    Health check endpoint for the backend.
    Returns the current status and server timestamp.
    """
    return jsonify(
        {
            "status": "Backend is healthy!",
            "timestamp": datetime.datetime.now().isoformat(),
        }
    )
