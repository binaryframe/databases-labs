from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Mapping


def json_safe(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


@dataclass(frozen=True)
class RecordDTO:
    resource: str
    values: Mapping[str, Any]

    @classmethod
    def from_row(cls, resource: str, row: Mapping[str, Any]) -> "RecordDTO":
        return cls(resource=resource, values=json_safe(dict(row)))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.values)


