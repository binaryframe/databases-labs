from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ResourceSchema:
    resource: str
    table: str
    primary_key: str
    fields: tuple[str, ...]
    required_on_create: tuple[str, ...]

    @property
    def selected_columns(self) -> tuple[str, ...]:
        return (self.primary_key, *self.fields)


SCHEMAS: Mapping[str, ResourceSchema] = {
    "users": ResourceSchema("users", "users", "user_id", (
        "first_name", "last_name", "email", "phone_number", "registration_date"),
        ("first_name", "last_name", "email", "registration_date")),
    "hotel_chains": ResourceSchema("hotel_chains", "hotel_chains", "chain_id", (
        "name", "description"), ("name",)),
    "locations": ResourceSchema("locations", "locations", "location_id", (
        "country", "city", "zip_code"), ("country", "city")),
    "hotels": ResourceSchema("hotels", "hotels", "hotel_id", (
        "name", "chain_id", "location_id", "star_rating", "address"),
        ("name", "location_id", "address")),
    "room_types": ResourceSchema("room_types", "room_types", "room_type_id", (
        "hotel_id", "type_name", "base_price", "max_guests"),
        ("hotel_id", "type_name", "base_price", "max_guests")),
    "rooms": ResourceSchema("rooms", "rooms", "room_id", (
        "hotel_id", "room_type_id", "room_number", "is_available"),
        ("hotel_id", "room_type_id", "room_number")),
    "reservations": ResourceSchema("reservations", "reservations", "reservation_id", (
        "user_id", "room_id", "check_in_date", "check_out_date", "total_price", "status"),
        ("user_id", "room_id", "check_in_date", "check_out_date", "total_price")),
    "email_confirmations": ResourceSchema("email_confirmations", "email_confirmations", "email_id", (
        "user_id", "reservation_id", "email_type", "sent_date"),
        ("user_id", "email_type", "sent_date")),
    "payment_holds": ResourceSchema("payment_holds", "payment_holds", "hold_id", (
        "reservation_id", "amount", "hold_status", "hold_date"),
        ("reservation_id", "amount", "hold_status", "hold_date")),
    "reviews": ResourceSchema("reviews", "reviews", "review_id", (
        "user_id", "hotel_id", "rating", "comment", "review_date"),
        ("user_id", "hotel_id", "rating", "review_date")),
}


def get_schema(resource: str) -> ResourceSchema:
    try:
        return SCHEMAS[resource]
    except KeyError as exc:
        raise KeyError(f"Невідомий ресурс '{resource}'. Доступні: {', '.join(SCHEMAS)}") from exc
