from flask import Blueprint, jsonify, request
from mysql.connector import Error as MySQLError
from ..dto.responses import success, json_safe
from ..service.stored_programs_service import StoredProgramsService

stored_programs_bp = Blueprint("stored_programs", __name__)
service = StoredProgramsService()


def _json_object():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object")
    return payload


def _handle_lookup_error(error):
    return jsonify({"status": "error", "error": str(error)}), 404


@stored_programs_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "stored-programs-api"})


@stored_programs_bp.post("/procedures/hotel-notes")
def add_hotel_note():
    result = service.add_hotel_note(_json_object())
    return jsonify(success(result, "Stored procedure sp_add_hotel_note executed")), 201


@stored_programs_bp.get("/hotels/<int:hotel_id>/notes")
def list_hotel_notes(hotel_id):
    return jsonify(success(service.list_hotel_notes(hotel_id)))


@stored_programs_bp.patch("/hotel-notes/<int:note_id>")
def update_hotel_note(note_id):
    try:
        result = service.update_hotel_note(note_id, _json_object())
        return jsonify(success(result, "Hotel note updated; validation trigger executed"))
    except LookupError as error:
        return _handle_lookup_error(error)


@stored_programs_bp.post("/procedures/reviews-by-names")
def add_review_by_names():
    result = service.add_review_by_names(_json_object())
    return jsonify(success(result, "Stored procedure sp_add_review_by_names executed")), 201


@stored_programs_bp.post("/procedures/noname-chains")
def insert_ten_noname():
    result = service.insert_ten_noname(_json_object())
    return jsonify(success(result, "Stored procedure inserted ten Noname rows")), 201


@stored_programs_bp.get("/procedures/reservation-metric")
def reservation_metric():
    operation = request.args.get("operation", "AVG")
    result = service.show_metric(operation)
    return jsonify(success(result, "Stored procedure called user-defined function"))


@stored_programs_bp.post("/procedures/split-users")
def split_users():
    result = service.split_users()
    return jsonify(success(result, "Cursor procedure created two timestamped tables")), 201


@stored_programs_bp.post("/reservations")
def create_reservation():
    result = service.create_reservation(_json_object())
    return jsonify(success(result, "Reservation created; BEFORE INSERT trigger validated values")), 201


@stored_programs_bp.delete("/reservations/<int:reservation_id>")
def delete_reservation(reservation_id):
    try:
        result = service.delete_reservation(reservation_id)
        return jsonify(success(result, "Reservation deleted; AFTER DELETE trigger wrote audit log"))
    except LookupError as error:
        return _handle_lookup_error(error)


@stored_programs_bp.get("/audit/reservation-deletions")
def list_reservation_deletion_logs():
    try:
        limit = int(request.args.get("limit", "100"))
    except ValueError:
        raise ValueError("limit must be an integer")
    return jsonify(success(service.list_reservation_deletion_logs(limit)))
