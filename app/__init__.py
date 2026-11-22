"""PantryLink prototype - inventory and agency ordering service for Capital Harvest Food Bank."""
import os

from flask import Flask

from app.api.routes import api_bp, web_bp
from app.data.repository import Repository
from app.data.seed import seed


def create_app(db_path=None, with_seed=True):
    app = Flask(__name__)
    repo = Repository(db_path or os.environ.get("PANTRYLINK_DB", ":memory:"))
    if with_seed and repo.count_lots() == 0:
        seed(repo)
    app.config["REPO"] = repo
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
