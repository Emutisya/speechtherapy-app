import os
import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException

from . import db
from .content import load_content


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder="static")
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "communication.sqlite3"),
        MAX_CONTENT_LENGTH=32_768,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        TRUSTED_HOSTS=["localhost", "127.0.0.1", "[::1]"],
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        key_file = Path(app.instance_path) / "session.key"
        try:
            with key_file.open("x", encoding="ascii") as handle:
                handle.write(secrets.token_hex(32))
            if os.name != "nt":
                key_file.chmod(0o600)
        except FileExistsError:
            pass
        app.config["SECRET_KEY"] = key_file.read_text(encoding="ascii").strip()
        if len(app.config["SECRET_KEY"]) < 64:
            raise RuntimeError("Invalid instance/session.key. Restore a valid key or remove it to reset sessions.")
    app.extensions["content"] = load_content()
    db.init_app(app)

    from .security import install_security
    from .api import api
    from .profiles import profiles
    from .progress import progress
    from .exports import exports
    from .writing import writing

    install_security(app)
    for blueprint in (api, profiles, progress, exports, writing):
        app.register_blueprint(blueprint)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error={"code": error.name.lower().replace(" ", "_"),
                              "message": error.description}), error.code

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify(error={"code": "internal_error",
                              "message": "Something went wrong. Try again; if it continues, ask your caregiver to check the server log."}), 500

    return app
