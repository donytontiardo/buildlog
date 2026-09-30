import os

from flask import Flask

from .models import db


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///buildlog.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # None disables the login gate entirely (fine for local dev; set this in
    # production so the deployed URL isn't wide open to anyone who finds it).
    app.config["APP_PASSWORD"] = os.environ.get("APP_PASSWORD")
    if config:
        app.config.update(config)

    db.init_app(app)

    from . import routes

    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
