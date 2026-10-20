from contextlib import contextmanager
from typing import Any, Iterator
from ..utils.db import get_connection


@contextmanager
def cursor_connection(dictionary: bool = False, commit: bool = False) -> Iterator[tuple[Any, Any]]:
    connection = get_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor, connection
        if commit:
            connection.commit()
    except Exception:
        if commit:
            connection.rollback()
        raise
    finally:
        try:
            cursor.close()
        finally:
            connection.close()
