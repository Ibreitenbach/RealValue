# backend/app/routes/main.py
from flask import Blueprint, jsonify, send_from_directory, current_app

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return jsonify({"message": "Welcome to the RealValue Backend API!"})


@main_bp.route("/status")
def status():
    return jsonify({"status": "Backend is running!"})


# Endpoint to serve uploaded files
@main_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    # UPLOAD_FOLDER is configured as absolute in app.__init__
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    # No need to check os.path.isabs(upload_folder) here, assume config is correct.

    # Basic security: Filenames secured on upload.
    # send_from_dir offers path prot. # noqa: E501

    # send_from_directory raises NotFound (404) if file doesn't exist.
    # Flask handles this by default. Catch other unexpected errors.
    try:
        return send_from_directory(
            upload_folder, filename, as_attachment=False
        )
    except Exception as e:
        # For HTTPExceptions (like NotFound), re-raise.
        # The generic app error handler will catch them.
        # For other exceptions, log and return 500.
        from werkzeug.exceptions import HTTPException

        if isinstance(e, HTTPException):
            raise e

        current_app.logger.error(
            f"Unexpected error serving file {filename}: {e}"
        )
        return jsonify({"msg": "Error serving file"}), 500
