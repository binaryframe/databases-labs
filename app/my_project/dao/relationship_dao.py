from typing import Any
from .sql_helpers import cursor_connection


class RelationshipDAO:
    def hotels_with_location(self) -> list[dict[str, Any]]:
        sql = """
            SELECT h.hotel_id, h.name, h.star_rating, h.address,
                   h.chain_id, hc.name AS chain_name,
                   h.location_id, l.country AS location_country,
                   l.city AS location_city, l.zip_code AS location_zip_code
            FROM hotels h
            JOIN locations l ON l.location_id = h.location_id
            LEFT JOIN hotel_chains hc ON hc.chain_id = h.chain_id
            ORDER BY h.hotel_id
        """
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute(sql)
            return list(cursor.fetchall())

    def location_hotels(self, location_id: int) -> list[dict[str, Any]]:
        sql = """
            SELECT h.hotel_id, h.name, h.star_rating, h.address,
                   h.location_id, l.city, l.country
            FROM hotels h JOIN locations l ON l.location_id = h.location_id
            WHERE l.location_id = %s ORDER BY h.hotel_id
        """
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute(sql, (location_id,))
            return list(cursor.fetchall())

    def location_exists(self, location_id: int) -> bool:
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute("SELECT 1 FROM locations WHERE location_id = %s", (location_id,))
            return cursor.fetchone() is not None

    def hotel_reviewers(self, hotel_id: int) -> list[dict[str, Any]]:
        sql = """
            SELECT r.review_id, r.rating, r.comment, r.review_date,
                   u.user_id AS reviewer_user_id, u.first_name AS reviewer_first_name,
                   u.last_name AS reviewer_last_name, u.email AS reviewer_email,
                   h.hotel_id, h.name AS hotel_name
            FROM reviews r
            JOIN users u ON u.user_id = r.user_id
            JOIN hotels h ON h.hotel_id = r.hotel_id
            WHERE h.hotel_id = %s
            ORDER BY r.review_date DESC, r.review_id DESC
        """
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute(sql, (hotel_id,))
            return list(cursor.fetchall())

    def hotel_exists(self, hotel_id: int) -> bool:
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute("SELECT 1 FROM hotels WHERE hotel_id = %s", (hotel_id,))
            return cursor.fetchone() is not None

    def user_reviewed_hotels(self, user_id: int) -> list[dict[str, Any]]:
        sql = """
            SELECT r.review_id, r.rating, r.comment, r.review_date,
                   u.user_id, u.first_name, u.last_name,
                   h.hotel_id, h.name AS hotel_name, h.star_rating,
                   l.city, l.country
            FROM reviews r
            JOIN users u ON u.user_id = r.user_id
            JOIN hotels h ON h.hotel_id = r.hotel_id
            JOIN locations l ON l.location_id = h.location_id
            WHERE u.user_id = %s
            ORDER BY r.review_date DESC, h.hotel_id
        """
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute(sql, (user_id,))
            return list(cursor.fetchall())

    def user_exists(self, user_id: int) -> bool:
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
            return cursor.fetchone() is not None

    def reservation_details(self) -> list[dict[str, Any]]:
        sql = """
            SELECT r.reservation_id, r.check_in_date, r.check_out_date,
                   r.total_price, r.status,
                   u.user_id, u.first_name AS user_first_name,
                   u.last_name AS user_last_name, u.email AS user_email,
                   rm.room_id, rm.room_number,
                   h.hotel_id, h.name AS hotel_name,
                   l.city AS hotel_city, l.country AS hotel_country
            FROM reservations r
            JOIN users u ON u.user_id = r.user_id
            JOIN rooms rm ON rm.room_id = r.room_id
            JOIN hotels h ON h.hotel_id = rm.hotel_id
            JOIN locations l ON l.location_id = h.location_id
            ORDER BY r.reservation_id
        """
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute(sql)
            return list(cursor.fetchall())


