# backend/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()


def create_app():
    load_dotenv()  # Load .env file
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "a_default_secret_key_if_not_set"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///site.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes.main import main_bp

    app.register_blueprint(main_bp)

    from .routes.health import health_bp

    app.register_blueprint(health_bp)

    from .routes.practice_challenges import practice_challenges_bp

    app.register_blueprint(practice_challenges_bp)

    from .routes.user_routes import user_bp

    app.register_blueprint(user_bp)

    return app
