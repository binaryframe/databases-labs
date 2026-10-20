from datetime import date
from decimal import Decimal, InvalidOperation
from ..dao.stored_programs_dao import StoredProgramsDAO


class StoredProgramsService:
    def __init__(self, dao=None):
        self.dao = dao or StoredProgramsDAO()

    @staticmethod
    def _required_text(value, field, max_len=None):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        value = value.strip()
        if max_len is not None and len(value) > max_len:
            raise ValueError(f"{field} must be at most {max_len} characters")
        return value

    def add_hotel_note(self, payload):
        hotel_id = payload.get("hotel_id")
        if not isinstance(hotel_id, int) or hotel_id <= 0:
            raise ValueError("hotel_id must be a positive integer")
        title = self._required_text(payload.get("title"), "title", 100)
        note_text = self._required_text(payload.get("note_text"), "note_text")
        return self.dao.add_hotel_note(hotel_id, title, note_text)

    def add_review_by_names(self, payload):
        first_name = self._required_text(payload.get("first_name"), "first_name", 50)
        last_name = self._required_text(payload.get("last_name"), "last_name", 50)
        hotel_name = self._required_text(payload.get("hotel_name"), "hotel_name", 100)
        try:
            rating = int(payload.get("rating"))
        except (TypeError, ValueError):
            raise ValueError("rating must be an integer from 1 to 5")
        if rating < 1 or rating > 5:
            raise ValueError("rating must be an integer from 1 to 5")
        comment = payload.get("comment")
        if comment is not None and not isinstance(comment, str):
            raise ValueError("comment must be a string or null")
        date_value = payload.get("review_date") or date.today().isoformat()
        try:
            date.fromisoformat(date_value)
        except (TypeError, ValueError):
            raise ValueError("review_date must use YYYY-MM-DD format")
        return self.dao.add_review_by_names(
            first_name, last_name, hotel_name, rating, comment, date_value
        )

    def insert_ten_noname(self, payload):
        start_number = payload.get("start_number")
        if not isinstance(start_number, int) or start_number < 0:
            raise ValueError("start_number must be a non-negative integer")
        return self.dao.insert_ten_noname(start_number)

    def show_metric(self, operation):
        if not isinstance(operation, str) or operation.upper().strip() not in {"MAX", "MIN", "SUM", "AVG"}:
            raise ValueError("operation must be MAX, MIN, SUM or AVG")
        return self.dao.show_reservation_metric(operation.upper().strip())

    def split_users(self):
        return self.dao.split_users_with_cursor()

    def list_hotel_notes(self, hotel_id):
        if hotel_id <= 0:
            raise ValueError("hotel_id must be a positive integer")
        return self.dao.list_hotel_notes(hotel_id)

    def update_hotel_note(self, note_id, payload):
        if note_id <= 0:
            raise ValueError("note_id must be a positive integer")
        title = self._required_text(payload.get("title"), "title", 100)
        note_text = self._required_text(payload.get("note_text"), "note_text")
        result = self.dao.update_hotel_note(note_id, title, note_text)
        if result is None:
            raise LookupError(f"hotel note {note_id} was not found")
        return result

    def create_reservation(self, payload):
        required = ("user_id", "room_id", "check_in_date", "check_out_date", "total_price")
        missing = [name for name in required if name not in payload]
        if missing:
            raise ValueError("Missing required fields: " + ", ".join(missing))
        for field in ("user_id", "room_id"):
            if not isinstance(payload[field], int) or payload[field] <= 0:
                raise ValueError(f"{field} must be a positive integer")
        try:
            check_in = date.fromisoformat(payload["check_in_date"])
            check_out = date.fromisoformat(payload["check_out_date"])
        except (TypeError, ValueError):
            raise ValueError("check_in_date and check_out_date must use YYYY-MM-DD format")
        try:
            total_price = Decimal(str(payload["total_price"]))
        except (InvalidOperation, TypeError):
            raise ValueError("total_price must be numeric")
        if not total_price.is_finite():
            raise ValueError("total_price must be a finite numeric value")
        status = payload.get("status", "Pending")
        if not isinstance(status, str) or not status.strip() or len(status) > 20:
            raise ValueError("status must be a non-empty string of at most 20 characters")
        return self.dao.create_reservation({
            "user_id": payload["user_id"], "room_id": payload["room_id"],
            "check_in_date": check_in.isoformat(), "check_out_date": check_out.isoformat(),
            "total_price": float(total_price), "status": status.strip(),
        })

    def delete_reservation(self, reservation_id):
        if reservation_id <= 0:
            raise ValueError("reservation_id must be a positive integer")
        if not self.dao.delete_reservation(reservation_id):
            raise LookupError(f"reservation {reservation_id} was not found")
        return {"reservation_id": reservation_id, "deleted": True}

    def list_reservation_deletion_logs(self, limit=100):
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        return self.dao.list_reservation_deletion_logs(limit)
