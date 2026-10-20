from flask import Blueprint, current_app, jsonify, request
from ..utils.errors import ValidationError

api = Blueprint("api", __name__, url_prefix="/api")


def _controller():
    return current_app.extensions["booking_controller"]


def _data(value):
    if isinstance(value, list):
        return [item.to_dict() if hasattr(item, "to_dict") else item for item in value]
    return value.to_dict() if hasattr(value, "to_dict") else value


@api.get("/health")
def health():
    return jsonify({"status": "ok", "service": "booking_system_api"})


@api.get("/<string:resource>")
def list_records(resource: str):
    limit = _parse_query_int("limit", 50)
    offset = _parse_query_int("offset", 0)
    records = _controller().list(resource, limit, offset)
    return jsonify({"data": _data(records), "meta": {"count": len(records), "limit": limit, "offset": offset}})


@api.post("/<string:resource>")
def create_record(resource: str):
    record = _controller().create(resource, request.get_json(silent=True))
    return jsonify({"data": _data(record)}), 201


@api.get("/<string:resource>/<int:record_id>")
def get_record(resource: str, record_id: int):
    return jsonify({"data": _data(_controller().get(resource, record_id))})


@api.put("/<string:resource>/<int:record_id>")
@api.patch("/<string:resource>/<int:record_id>")
def update_record(resource: str, record_id: int):
    record = _controller().update(resource, record_id, request.get_json(silent=True))
    return jsonify({"data": _data(record)})


@api.delete("/<string:resource>/<int:record_id>")
def delete_record(resource: str, record_id: int):
    return jsonify({"data": _controller().delete(resource, record_id)})


@api.get("/hotels/with-location")
def hotels_with_location():
    records = _controller().hotels_with_location()
    return jsonify({"data": _data(records), "meta": {"count": len(records)}})


@api.get("/locations/<int:location_id>/hotels")
def hotels_for_location(location_id: int):
    records = _controller().hotels_for_location(location_id)
    return jsonify({"data": _data(records), "meta": {"count": len(records), "location_id": location_id}})


@api.get("/hotels/<int:hotel_id>/reviewers")
def reviewers_for_hotel(hotel_id: int):
    records = _controller().reviewers_for_hotel(hotel_id)
    return jsonify({"data": _data(records), "meta": {"count": len(records), "hotel_id": hotel_id}})


@api.get("/users/<int:user_id>/reviewed-hotels")
def hotels_reviewed_by_user(user_id: int):
    records = _controller().hotels_reviewed_by_user(user_id)
    return jsonify({"data": _data(records), "meta": {"count": len(records), "user_id": user_id}})


@api.get("/reservations/details")
def reservation_details():
    records = _controller().reservation_details()
    return jsonify({"data": _data(records), "meta": {"count": len(records)}})


def _parse_query_int(key: str, default: int) -> int:
    raw = request.args.get(key, str(default))
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Query-параметр {key} має бути цілим числом") from exc
