from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

_ENV_CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    from app.models import User
    return User.query.get(int(user_id))

def create_app(config_class=None):
    """Application factory pattern"""
    if config_class is None:
        env = os.getenv("FLASK_ENV", "development").lower()
        config_class = _ENV_CONFIG_MAP.get(env, DevelopmentConfig)

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Register blueprints (routes)
    from app import routes
    app.register_blueprint(routes.bp)

    return app
