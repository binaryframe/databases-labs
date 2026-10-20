import sys
import unittest
from datetime import date
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from my_project.service.booking_service import BookingService
from my_project.utils.errors import NotFoundError, ValidationError


class FakeDAO:
    def __init__(self):
        self.rows = {
            1: {"user_id": 1, "first_name": "Test", "last_name": "User",
                "email": "test@example.com", "phone_number": None,
                "registration_date": date(2026, 1, 1)}
        }

    def list(self, schema, limit=50, offset=0):
        return list(self.rows.values())[offset:offset + limit]

    def get(self, schema, record_id):
        return self.rows.get(record_id)

    def create(self, schema, data):
        new_id = max(self.rows, default=0) + 1
        row = {schema.primary_key: new_id, **data}
        self.rows[new_id] = row
        return row

    def update(self, schema, record_id, data):
        if record_id not in self.rows:
            return None
        self.rows[record_id].update(data)
        return self.rows[record_id]

    def delete(self, schema, record_id):
        return self.rows.pop(record_id, None) is not None


class FakeRelationshipDAO:
    def hotels_with_location(self):
        return [{"hotel_id": 1, "name": "Example Hotel", "location_city": "Львів"}]

    def location_exists(self, location_id):
        return location_id == 1

    def location_hotels(self, location_id):
        return [{"hotel_id": 1, "name": "Example Hotel"}]

    def hotel_exists(self, hotel_id):
        return hotel_id == 1

    def hotel_reviewers(self, hotel_id):
        return [{"review_id": 1, "reviewer_user_id": 1}]

    def user_exists(self, user_id):
        return user_id == 1

    def user_reviewed_hotels(self, user_id):
        return [{"hotel_id": 1, "review_id": 1}]

    def reservation_details(self):
        return []


class BookingServiceTests(unittest.TestCase):
    def setUp(self):
        self.dao = FakeDAO()
        self.service = BookingService(self.dao, FakeRelationshipDAO())

    def test_create_and_read_user_returns_dto(self):
        created = self.service.create_record("users", {
            "first_name": "Олена", "last_name": "Коваль",
            "email": "olena@example.com", "registration_date": "2026-04-15"
        })
        self.assertEqual(created.to_dict()["user_id"], 2)
        self.assertEqual(created.to_dict()["registration_date"], "2026-04-15")

    def test_update_user(self):
        updated = self.service.update_record("users", 1, {"first_name": "Іван"})
        self.assertEqual(updated.to_dict()["first_name"], "Іван")

    def test_missing_resource_record_raises_404_error(self):
        with self.assertRaises(NotFoundError):
            self.service.get_record("users", 999)

    def test_invalid_email_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.create_record("users", {
                "first_name": "A", "last_name": "B", "email": "not-an-email",
                "registration_date": "2026-04-15"
            })

    def test_invalid_reservation_dates_are_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.create_record("reservations", {
                "user_id": 1, "room_id": 1, "check_in_date": "2026-05-10",
                "check_out_date": "2026-05-10", "total_price": "100.00"
            })

    def test_many_to_many_relationship_returns_dto(self):
        records = self.service.hotels_reviewed_by_user(1)
        self.assertEqual(records[0].to_dict()["hotel_id"], 1)


if __name__ == "__main__":
    unittest.main()
