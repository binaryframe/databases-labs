from flask import Flask, jsonify
from mysql.connector import Error as MySQLError
from .controller.stored_programs_controller import stored_programs_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(JSON_SORT_KEYS=False)
    if test_config:
        app.config.update(test_config)

    app.register_blueprint(stored_programs_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return jsonify({
            "application": "booking-system-stored-programs",
            "status": "ok",
            "api_prefix": "/api",
        })

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(MySQLError)
    def handle_mysql_error(error):
        errno = getattr(error, "errno", None)
        status = 400 if errno in (1644, 3819, 1452, 1062) else 500
        return jsonify({"error": "Database operation failed", "detail": str(error)}), status

    return app
