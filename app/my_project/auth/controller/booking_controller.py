from ...service.booking_service import BookingService


class BookingController:
    def __init__(self, service: BookingService | None = None):
        self.service = service or BookingService()

    def list(self, resource: str, limit: int, offset: int):
        return self.service.list_records(resource, limit, offset)

    def get(self, resource: str, record_id: int):
        return self.service.get_record(resource, record_id)

    def create(self, resource: str, payload):
        return self.service.create_record(resource, payload)

    def update(self, resource: str, record_id: int, payload):
        return self.service.update_record(resource, record_id, payload)

    def delete(self, resource: str, record_id: int):
        self.service.delete_record(resource, record_id)
        return {"deleted": True, "resource": resource, "id": record_id}

    def hotels_with_location(self):
        return self.service.hotels_with_location()

    def hotels_for_location(self, location_id: int):
        return self.service.hotels_for_location(location_id)

    def reviewers_for_hotel(self, hotel_id: int):
        return self.service.reviewers_for_hotel(hotel_id)

    def hotels_reviewed_by_user(self, user_id: int):
        return self.service.hotels_reviewed_by_user(user_id)

    def reservation_details(self):
        return self.service.reservation_details()
