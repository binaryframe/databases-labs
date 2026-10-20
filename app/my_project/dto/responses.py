from datetime import date, datetime
from decimal import Decimal


def json_safe(value):
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def success(data=None, message="ok"):
    return {"status": "success", "message": message, "data": json_safe(data)}
