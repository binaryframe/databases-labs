import os


def get_connection():
    import mysql.connector
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE", "booking_system"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        autocommit=False,
    )


class StoredProgramsDAO:
    def _finish_proc(self, cursor):
        rows = []
        try:
            for result in cursor.stored_results():
                current = result.fetchall()
                if current:
                    rows.extend(current)
                result.close()
        except Exception:
            pass
        return rows

    def _call_for_row(self, procedure, args):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc(procedure, args)
            rows = self._finish_proc(cursor)
            conn.commit()
            return rows[0] if rows else None
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def add_hotel_note(self, hotel_id, title, note_text):
        return self._call_for_row("sp_add_hotel_note", [hotel_id, title, note_text])

    def add_review_by_names(self, first_name, last_name, hotel_name, rating, comment, review_date):
        return self._call_for_row("sp_add_review_by_names", [
            first_name, last_name, hotel_name, rating, comment, review_date
        ])

    def insert_ten_noname(self, start_number):
        return self._call_for_row("sp_insert_ten_noname", [start_number])

    def show_reservation_metric(self, operation):
        return self._call_for_row("sp_show_reservation_metric", [operation])

    def split_users_with_cursor(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            args = cursor.callproc(
                "sp_split_users_with_cursor",
                [None, None]
            )

            rows = self._finish_proc(cursor)

            table_a = None
            table_b = None

            if rows:
                result = rows[-1]

                if isinstance(result, dict):
                    table_a = result.get("table_a")
                    table_b = result.get("table_b")

            if not table_a or not table_b:
                if isinstance(args, dict):
                    table_a = (
                        table_a
                        or args.get("p_table_a")
                        or args.get("table_a")
                    )
                    table_b = (
                        table_b
                        or args.get("p_table_b")
                        or args.get("table_b")
                    )

                elif isinstance(args, (list, tuple)) and len(args) >= 2:
                    table_a = table_a or args[0]
                    table_b = table_b or args[1]

            if not table_a or not table_b:
                raise RuntimeError(
                    "The procedure did not return both table names. "
                    "Check sp_split_users_with_cursor in MySQL."
                )

            conn.commit()

            return {
                "table_a": table_a,
                "table_b": table_b
            }

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    def list_hotel_notes(self, hotel_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT note_id, hotel_id, title, note_text, created_at "
                "FROM hotel_notes WHERE hotel_id = %s ORDER BY note_id",
                (hotel_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def update_hotel_note(self, note_id, title, note_text):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT note_id FROM hotel_notes WHERE note_id = %s",
                (note_id,),
            )
            if cursor.fetchone() is None:
                conn.rollback()
                return None
            cursor.execute(
                "UPDATE hotel_notes SET title = %s, note_text = %s WHERE note_id = %s",
                (title, note_text, note_id),
            )
            cursor.execute(
                "SELECT note_id, hotel_id, title, note_text, created_at "
                "FROM hotel_notes WHERE note_id = %s",
                (note_id,),
            )
            row = cursor.fetchone()
            conn.commit()
            return row
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def create_reservation(self, payload):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO reservations "
                "(user_id, room_id, check_in_date, check_out_date, total_price, status) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (payload["user_id"], payload["room_id"], payload["check_in_date"],
                 payload["check_out_date"], payload["total_price"], payload.get("status", "Pending")),
            )
            new_id = cursor.lastrowid
            conn.commit()
            return {"reservation_id": new_id, **payload}
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_reservation(self, reservation_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,))
            deleted = cursor.rowcount
            conn.commit()
            return deleted > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def list_reservation_deletion_logs(self, limit=100):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT log_id, deleted_reservation_id, user_id, room_id, check_in_date, "
                "check_out_date, total_price, reservation_status, deleted_at "
                "FROM reservation_delete_log ORDER BY log_id DESC LIMIT %s",
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
