# backend/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate  # Import Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()  # Create Migrate instance


def create_app():
    load_dotenv()  # Load .env file
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "default_dev_secret_key"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///realvalue.db"  # Changed default db name
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "default_dev_jwt_key"
    )

    # File Upload Configuration
    # Determine the absolute path to the 'backend' directory
    backend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    app.config["UPLOAD_FOLDER"] = os.path.join(backend_dir, "uploads")
    app.config["ALLOWED_EXTENSIONS"] = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "mp4",
        "mov",
        "avi",
    }
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

    # Ensure the upload folder exists
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    db.init_app(app)
    jwt.init_app(app)  # Initialize JWTManager with the app
    migrate.init_app(app, db)  # Initialize Migrate with app and db

    # User loader function for Flask-JWT-Extended
    from .models import (
        User,
        # ShowcaseItem, # F401: Unused. Models are available via models.__init__
    )  # Models (migrate) # noqa: E501

    # from .models import UserProfile # F401 unused

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        try:
            user_id = int(identity)
            user = User.query.filter_by(id=user_id).one_or_none()
            return user
        except ValueError:
            # Identity is not an int
            return None
        except Exception:
            # Other potential errors during user load
            return None

    from .routes.main import main_bp

    app.register_blueprint(main_bp)

    from .routes.health import health_bp

    app.register_blueprint(health_bp)

    from .routes.profile import profile_bp  # Import profile blueprint

    app.register_blueprint(profile_bp)  # Register profile blueprint

    from .routes.auth import auth_bp  # Import auth blueprint

    app.register_blueprint(auth_bp)  # Register auth blueprint

    from .routes.practice_challenges import practice_challenges_bp

    app.register_blueprint(practice_challenges_bp)

    from .routes.user_routes import user_bp

    app.register_blueprint(user_bp)

    from .routes.showcase_routes import (
        showcase_bp,
    )  # Import showcase blueprint

    app.register_blueprint(showcase_bp)  # Register showcase blueprint

    # Custom JSON error handler for 404
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"msg": "Resource not found"}), 404

    # Generic error handler for HTTPExceptions to get more info on 422s
    from werkzeug.exceptions import HTTPException
    from flask import current_app, jsonify  # Import current_app and jsonify

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        # Log the full error and stack trace for debugging
        description = e.description
        if (
            hasattr(e, "data") and e.data
        ):  # For some validation errors (e.g. Flask-RESTPlus)
            description = e.data.get("errors", e.description)
            if "message" in e.data:
                description = f"{e.data['message']} - {description}"

        log_msg = f"HTTPExc: {e.code} {e.name} - Desc: {description}"
        current_app.logger.error(log_msg, exc_info=True)
        # Return a JSON response
        return (
            jsonify(
                {
                    "code": e.code,
                    "name": e.name,
                    "description": description,  # Use detailed description
                }
            ),
            e.code or 500,
        )  # Ensure a status code is returned

    return app
