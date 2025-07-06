# C:\realvalue\backend\app\__init__.py (Corrected Version 2)
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from werkzeug.exceptions import HTTPException

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    load_dotenv()

    # Load configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "a-very-secret-dev-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///realvalue.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "a-very-secret-jwt-key")

    # Configure file uploads
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app.config["UPLOAD_FOLDER"] = os.path.join(backend_dir, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions with the app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import models HERE so that they are registered with SQLAlchemy
    # before any blueprints or commands need them.
    from . import models

    # JWT user lookup loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        try:
            user_id = int(jwt_data["sub"])
            return models.User.query.get(user_id)
        except (ValueError, TypeError):
            return None

    # Register blueprints
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    from .routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # --- Add all other blueprint registrations here ---
    # (Assuming they follow the same pattern)
    from .routes.exchange_routes import exchange_bp
    app.register_blueprint(exchange_bp)
    from .routes.showcase_routes import showcase_bp
    app.register_blueprint(showcase_bp)
    # ... etc.

    # Register custom error handlers
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response

    return app