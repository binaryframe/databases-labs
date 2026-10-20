"""Small MySQL connection factory; credentials are read from Flask config/env."""
import os


def get_connection():
    # Imports are lazy so service tests do not require Flask or a live DB.
    from flask import current_app
    import mysql.connector

    config = dict(current_app.config["DB_CONFIG"])
    config["host"] = os.getenv("DB_HOST", config.get("host", "127.0.0.1"))
    config["port"] = int(os.getenv("DB_PORT", config.get("port", 3306)))
    config["database"] = os.getenv("DB_NAME", config.get("name", "booking_system"))
    config["user"] = os.getenv("DB_USER", config.get("user", "root"))
    config["password"] = os.getenv("DB_PASSWORD", config.get("password", ""))
    timeout = int(os.getenv("DB_CONNECTION_TIMEOUT", config.get("connection_timeout", 10)))
    config.pop("name", None)
    config.pop("connection_timeout", None)
    config["connection_timeout"] = timeout
    return mysql.connector.connect(**config)
