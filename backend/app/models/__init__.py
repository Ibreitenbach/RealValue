# backend/app/__init__.py
from flask import Flask, jsonify, current_app, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from werkzeug.exceptions import HTTPException # Import HTTPException for error handler
import logging
from logging.handlers import RotatingFileHandler # For file logging

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    load_dotenv()  # Load .env file
    app = Flask(__name__)
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/realvalue.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('RealValue startup')


    # General app configuration
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "a_default_secret_key_if_not_set_for_dev"  # Ensure this is strong in prod
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///realvalue.db"  # Changed default db name
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY", "a_default_jwt_secret_key_if_not_set_for_dev"  # Ensure this is strong in prod
    )

    # File Upload Configuration
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join(app.root_path, 'uploads'))
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'} # Example extensions
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])


    db.init_app(app)
    jwt.init_app(app)  # Initialize JWTManager with the app
    migrate.init_app(app, db)  # Initialize Migrate with app and db

    # Import all models so Flask-Migrate can discover them.
    # Keep F401 noqas if models are not directly used in this file but needed for discovery.
    from .models import (
        User,
        UserProfile,
        PracticeChallengeTemplate,  # noqa: F401
        UserChallengeCompletion,  # noqa: F401
        JournalEntry,  # noqa: F401
        MindsetChallengeTemplate,  # noqa: F401
        UserMindsetCompletion,  # noqa: F401
        MindfulMomentTemplate,  # noqa: F401
        UserReminderSetting,  # noqa: F401
        Skill, # noqa: F401
        SkillCategory, # noqa: F401
        ExchangeOffer, # noqa: F401
        OfferStatusEnum, # noqa: F401
        Post, # noqa: F401
        PostType, # noqa: F401
        Favor, # noqa: F401
        Circle, # noqa: F401
        CircleMember, # noqa: F401
        Endorsement, # noqa: F401
        Event, # noqa: F401
        MindContent, # noqa: F401
        MindContentCategory, # noqa: F401
        ShowcaseItem, # noqa: F401
        Donation # noqa: F401
    )


    # JWT user loader function
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        # Identity is str, convert to int for DB query if user ID is int
        try:
            user_id = int(identity)
        except ValueError:
            # Handle cases where identity might not be a valid integer string
            return None
        return User.query.filter_by(id=user_id).one_or_none()

    # Register blueprints (routes)
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    from .routes.health import health_bp
    app.register_blueprint(health_bp)

    from .routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes.exchange_routes import exchange_bp
    app.register_blueprint(exchange_bp)

    from .routes.mind_progress_routes import mind_progress_bp
    app.register_blueprint(mind_progress_bp)

    from .routes.donation_routes import donation_bp
    app.register_blueprint(donation_bp)

    from .routes.showcase_routes import showcase_bp
    app.register_blueprint(showcase_bp)

    from .routes.skill_routes import skill_bp # Assuming skill routes are available
    app.register_blueprint(skill_bp)

    from .routes.post_routes import post_bp # Assuming post routes are available
    app.register_blueprint(post_bp)

    from .routes.favor_routes import favors_bp # Assuming favor routes are available
    app.register_blueprint(favors_bp)

    from .routes.circle_routes import circles_bp # Assuming circle routes are available
    app.register_blueprint(circles_bp)

    from .routes.endorsement_routes import endorsement_bp # Assuming endorsement routes are available
    app.register_blueprint(endorsement_bp)

    from .routes.event_routes import events_bp # Assuming event routes are available
    app.register_blueprint(events_bp)

    from .routes.journal_routes import journal_bp # Assuming journal routes are available
    app.register_blueprint(journal_bp)

    from .routes.mindset_routes import mindset_bp # Assuming mindset routes are available
    app.register_blueprint(mindset_bp)

    from .routes.mindful_moment_routes import mindful_moments_bp # Assuming mindful moments routes are available
    app.register_blueprint(mindful_moments_bp)

    from .routes.mind_content_routes import mind_content_bp # Assuming mind content routes are available
    app.register_blueprint(mind_content_bp)


    # Custom JSON error handler for 404
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"msg": "Resource not found"}), 404

    # Generic error handler for HTTPExceptions to get more info on 422s, etc.
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        description = e.description
        if hasattr(e, "data") and e.data:
            description = e.data.get("errors", e.description)
            if "message" in e.data:
                description = f"{e.data['message']} - {description}"

        if hasattr(current_app, 'logger'):
             log_msg = f"HTTPExc: {e.code} {e.name} - Desc: {description}"
             current_app.logger.error(log_msg, exc_info=True)
        
        return (
            jsonify(
                {
                    "code": e.code,
                    "name": e.name,
                    "description": description,
                }
            ),
            e.code or 500,
        )

    return app