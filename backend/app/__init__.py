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
        "SECRET_KEY", "a_default_secret_key_if_not_set_for_dev" # Ensure this is strong in prod
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///realvalue.db" # Changed default db name
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "a_default_jwt_secret_key_if_not_set_for_dev" # Ensure this is strong in prod
    )

    db.init_app(app)
    jwt.init_app(app)  # Initialize JWTManager with the app
    migrate.init_app(app, db)  # Initialize Migrate with app and db

    # User loader function for Flask-JWT-Extended
    from .models import User # Models need to be imported for migrate to detect them
    from .models import UserProfile
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        # The identity is now a string, convert to int for DB query if user ID is integer
        try:
            user_id = int(identity)
        except ValueError:
            # Handle cases where identity might not be a valid integer string
            return None
        return User.query.filter_by(id=user_id).one_or_none()

    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    from .routes.profile import profile_bp # Import profile blueprint
    app.register_blueprint(profile_bp)   # Register profile blueprint

    from .routes.auth import auth_bp # Import auth blueprint
    app.register_blueprint(auth_bp)   # Register auth blueprint

    return app
