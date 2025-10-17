from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()


def create_app(test_config: dict | None = None) -> Flask:
    """Application factory for the streaming platform."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.update(
        SECRET_KEY="change-me",
        SQLALCHEMY_DATABASE_URI="sqlite:///streambox.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(Path("uploads")),
    )

    if test_config:
        app.config.update(test_config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from . import models  # noqa: F401 - ensure models are registered
    from .routes import main_bp
    from .auth import auth_bp
    from .admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        models.seed_data()

    return app
