import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from ..dao.base_dao import BaseDAO
from ..dao.relationship_dao import RelationshipDAO
from ..domain.dto import RecordDTO
from ..domain.schemas import SCHEMAS, ResourceSchema, get_schema
from ..utils.errors import NotFoundError, ValidationError

DATE_FIELDS = {"registration_date", "check_in_date", "check_out_date", "review_date"}
DATETIME_FIELDS = {"sent_date", "hold_date"}
INTEGER_FIELDS = {"chain_id", "location_id", "hotel_id", "room_type_id", "user_id", "room_id",
                  "reservation_id", "star_rating", "max_guests", "rating"}
DECIMAL_FIELDS = {"base_price", "total_price", "amount"}
STRING_FIELDS = {"first_name", "last_name", "email", "phone_number", "name", "description", "country",
                 "city", "zip_code", "address", "type_name", "room_number", "status", "email_type",
                 "hold_status", "comment"}
NULLABLE_FIELDS = {"phone_number", "description", "chain_id", "star_rating", "zip_code", "reservation_id", "comment"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class BookingService:
    def __init__(self, dao: BaseDAO | None = None, relationship_dao: RelationshipDAO | None = None):
        self.dao = dao or BaseDAO()
        self.relationship_dao = relationship_dao or RelationshipDAO()

    def list_records(self, resource: str, limit: int = 50, offset: int = 0) -> list[RecordDTO]:
        schema = self._schema(resource)
        if not 1 <= limit <= 100:
            raise ValidationError("Параметр limit має бути в межах від 1 до 100")
        if offset < 0:
            raise ValidationError("Параметр offset не може бути від’ємним")
        return [RecordDTO.from_row(resource, row) for row in self.dao.list(schema, limit, offset)]

    def get_record(self, resource: str, record_id: int) -> RecordDTO:
        schema = self._schema(resource)
        row = self.dao.get(schema, record_id)
        if row is None:
            raise NotFoundError(f"Запис {resource}/{record_id} не знайдено")
        return RecordDTO.from_row(resource, row)

    def create_record(self, resource: str, payload: Any) -> RecordDTO:
        schema = self._schema(resource)
        data = self._normalize_payload(schema, payload, creating=True)
        self._validate_cross_fields(resource, data)
        row = self.dao.create(schema, data)
        return RecordDTO.from_row(resource, row)

    def update_record(self, resource: str, record_id: int, payload: Any) -> RecordDTO:
        schema = self._schema(resource)
        current = self.dao.get(schema, record_id)
        if current is None:
            raise NotFoundError(f"Запис {resource}/{record_id} не знайдено")
        data = self._normalize_payload(schema, payload, creating=False)
        merged = dict(current)
        merged.update(data)
        self._validate_cross_fields(resource, merged)
        updated = self.dao.update(schema, record_id, data)
        if updated is None:
            raise NotFoundError(f"Запис {resource}/{record_id} не знайдено")
        return RecordDTO.from_row(resource, updated)

    def delete_record(self, resource: str, record_id: int) -> None:
        schema = self._schema(resource)
        if self.dao.get(schema, record_id) is None:
            raise NotFoundError(f"Запис {resource}/{record_id} не знайдено")
        if not self.dao.delete(schema, record_id):
            raise NotFoundError(f"Запис {resource}/{record_id} не знайдено")

    def hotels_with_location(self) -> list[RecordDTO]:
        rows = self.relationship_dao.hotels_with_location()
        return [RecordDTO.from_row("hotel_with_location", row) for row in rows]

    def hotels_for_location(self, location_id: int) -> list[RecordDTO]:
        if not self.relationship_dao.location_exists(location_id):
            raise NotFoundError(f"Локацію з ID {location_id} не знайдено.")
        rows = self.relationship_dao.location_hotels(location_id)
        return [RecordDTO.from_row("location_hotel", row) for row in rows]

    def reviewers_for_hotel(self, hotel_id: int) -> list[RecordDTO]:
        if not self.relationship_dao.hotel_exists(hotel_id):
            raise NotFoundError(f"Готель з ID {hotel_id} не знайдено.")
        rows = self.relationship_dao.hotel_reviewers(hotel_id)
        return [RecordDTO.from_row("hotel_reviewer", row) for row in rows]

    def hotels_reviewed_by_user(self, user_id: int) -> list[RecordDTO]:
        if not self.relationship_dao.user_exists(user_id):
            raise NotFoundError(f"Користувача з ID {user_id} не знайдено.")
        rows = self.relationship_dao.user_reviewed_hotels(user_id)
        return [RecordDTO.from_row("user_reviewed_hotel", row) for row in rows]

    def reservation_details(self) -> list[RecordDTO]:
        rows = self.relationship_dao.reservation_details()
        return [RecordDTO.from_row("reservation_detail", row) for row in rows]

    @staticmethod
    def _schema(resource: str) -> ResourceSchema:
        try:
            return get_schema(resource)
        except KeyError as exc:
            raise ValidationError(str(exc).strip("'")) from exc

    def _normalize_payload(self, schema: ResourceSchema, payload: Any, creating: bool) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValidationError("Тіло запиту має бути JSON-об’єктом")
        if not payload:
            raise ValidationError("Тіло запиту не може бути порожнім")
        unknown = sorted(set(payload) - set(schema.fields))
        if unknown:
            allowed = ", ".join(schema.fields)
            raise ValidationError(f"невідомі або незмінювані поля: {', '.join(unknown)}. Дозволені поля: {allowed}")
        if creating:
            missing = [field for field in schema.required_on_create if field not in payload]
            if missing:
                raise ValidationError(f"Не передано обов’язкові поля: {', '.join(missing)}")
        data: dict[str, Any] = {}
        for field, value in payload.items():
            if value is None:
                if field not in NULLABLE_FIELDS:
                    raise ValidationError(f"поле '{field}' не може бути null")
                data[field] = None
                continue
            try:
                if field in DATE_FIELDS:
                    data[field] = date.fromisoformat(str(value))
                elif field in DATETIME_FIELDS:
                    normalized = str(value).replace("Z", "+00:00")
                    data[field] = datetime.fromisoformat(normalized)
                elif field in INTEGER_FIELDS:
                    if isinstance(value, bool):
                        raise ValueError
                    parsed = int(value)
                    if str(value).strip() != str(parsed) and not isinstance(value, int):
                        raise ValueError
                    data[field] = parsed
                elif field in DECIMAL_FIELDS:
                    parsed_decimal = Decimal(str(value))
                    if not parsed_decimal.is_finite():
                        raise ValueError
                    data[field] = parsed_decimal
                elif field == "is_available":
                    if value in (True, 1, "1", "true", "True"):
                        data[field] = True
                    elif value in (False, 0, "0", "false", "False"):
                        data[field] = False
                    else:
                        raise ValueError
                elif field in STRING_FIELDS:
                    if not isinstance(value, str):
                        raise ValueError
                    if field != "comment" and not value.strip():
                        raise ValueError
                    data[field] = value.strip() if field != "comment" else value
                else:
                    data[field] = value
            except (ValueError, TypeError, InvalidOperation) as exc:
                raise ValidationError(f"Некоректне значення для поля '{field}': {value!r}") from exc

        if "email" in data and not EMAIL_RE.match(data["email"]):
            raise ValidationError("Поле email має містити коректну адресу електронної пошти")
        for field in ("star_rating", "rating"):
            if field in data and data[field] is not None and not 1 <= data[field] <= 5:
                raise ValidationError(f"Поле '{field}' має бути в межах від 1 до 5")
        if "max_guests" in data and data["max_guests"] < 1:
            raise ValidationError("Поле max_guests має бути не менше 1")
        for field in DECIMAL_FIELDS:
            if field in data and data[field] < 0:
                raise ValidationError(f"Поле '{field}' не може бути від’ємним")
        if "email" in data and len(data["email"]) > 100:
            raise ValidationError("довжина email не може перевищувати 100 символів")
        return data

    @staticmethod
    def _validate_cross_fields(resource: str, data: dict[str, Any]) -> None:
        if resource == "reservations":
            check_in = data.get("check_in_date")
            check_out = data.get("check_out_date")
            if check_in is not None and check_out is not None and check_out <= check_in:
                raise ValidationError("check_out_date має бути пізніше за check_in_date")
