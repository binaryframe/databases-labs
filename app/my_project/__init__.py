import os
from pathlib import Path


def create_app(test_config: dict | None = None):
    import yaml
    from flask import Flask, jsonify

    from .auth.controller.booking_controller import BookingController
    from .route.api_routes import api
    from .utils.errors import ApiError

    app = Flask(__name__)
    config_path = Path(__file__).resolve().parents[1] / "config" / "app.yml"
    with config_path.open("r", encoding="utf-8") as config_file:
        loaded = yaml.safe_load(config_file) or {}

    app_config = loaded.get("app", {})
    db_config = loaded.get("database", {})
    app.config["DB_CONFIG"] = {
        "host": os.getenv("DB_HOST", db_config.get("host", "127.0.0.1")),
        "port": int(os.getenv("DB_PORT", db_config.get("port", 3306))),
        "name": os.getenv("DB_NAME", db_config.get("name", "booking_system")),
        "user": os.getenv("DB_USER", db_config.get("user", "root")),
        "password": os.getenv("DB_PASSWORD", db_config.get("password", "")),
        "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", db_config.get("connection_timeout", 10))),
    }
    app.config["JSON_SORT_KEYS"] = False
    if test_config:
        app.config.update(test_config)

    app.extensions["booking_controller"] = BookingController()
    app.register_blueprint(api)

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify({"error": {"code": error.error_code, "message": error.message}}), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        errno = getattr(error, "errno", None)
        if errno in {1062, 1451, 1452, 3819}:
            return jsonify({"error": {"code": "data_conflict", "message": "Операція порушує унікальність або зовнішній ключ бази даних"}}), 409
        app.logger.exception("Unhandled API error", exc_info=error)
        return jsonify({"error": {"code": "internal_error", "message": "Внутрішня помилка сервера"}}), 500

    return app
