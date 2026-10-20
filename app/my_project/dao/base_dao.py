from typing import Any
from .sql_helpers import cursor_connection
from ..domain.schemas import ResourceSchema
from ..utils.errors import NotFoundError


class BaseDAO:
    def list(self, schema: ResourceSchema, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        columns = ", ".join(f"`{column}`" for column in schema.selected_columns)
        sql = f"SELECT {columns} FROM `{schema.table}` ORDER BY `{schema.primary_key}` LIMIT %s OFFSET %s"
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute(sql, (limit, offset))
            return list(cursor.fetchall())

    def get(self, schema: ResourceSchema, record_id: int) -> dict[str, Any] | None:
        columns = ", ".join(f"`{column}`" for column in schema.selected_columns)
        sql = f"SELECT {columns} FROM `{schema.table}` WHERE `{schema.primary_key}` = %s"
        with cursor_connection(dictionary=True) as (cursor, _connection):
            cursor.execute(sql, (record_id,))
            return cursor.fetchone()

    def create(self, schema: ResourceSchema, data: dict[str, Any]) -> dict[str, Any]:
        columns = tuple(data.keys())
        names = ", ".join(f"`{column}`" for column in columns)
        placeholders = ", ".join(["%s"] * len(columns))
        values = tuple(data[column] for column in columns)
        sql = f"INSERT INTO `{schema.table}` ({names}) VALUES ({placeholders})"
        with cursor_connection(dictionary=True, commit=True) as (cursor, _connection):
            cursor.execute(sql, values)
            new_id = cursor.lastrowid
        row = self.get(schema, int(new_id))
        if row is None:
            raise RuntimeError("Запис створено, але його не вдалося прочитати")
        return row

    def update(self, schema: ResourceSchema, record_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        assignments = ", ".join(f"`{column}` = %s" for column in data)
        values = tuple(data.values()) + (record_id,)
        sql = f"UPDATE `{schema.table}` SET {assignments} WHERE `{schema.primary_key}` = %s"
        with cursor_connection(dictionary=True, commit=True) as (cursor, _connection):
            cursor.execute(sql, values)
            affected = cursor.rowcount
        if affected == 0:
            return self.get(schema, record_id)
        return self.get(schema, record_id)

    def delete(self, schema: ResourceSchema, record_id: int) -> bool:
        sql = f"DELETE FROM `{schema.table}` WHERE `{schema.primary_key}` = %s"
        with cursor_connection(dictionary=True, commit=True) as (cursor, _connection):
            cursor.execute(sql, (record_id,))
            return cursor.rowcount > 0


