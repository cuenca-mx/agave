import datetime as dt
import uuid
from base64 import urlsafe_b64encode
from typing import Any

from rom import Column


def uuid_field(prefix: str = ''):
    def base64_uuid_func() -> str:
        return prefix + urlsafe_b64encode(uuid.uuid4().bytes).decode()[:-2]

    return base64_uuid_func


class String(Column):
    """
    No utilizo la clase String de rom porque todo lo maneja en bytes
    codificado en latin-1.
    """

    _allowed = str

    def _to_redis(self, value):
        return value.encode('utf-8')

    def _from_redis(self, value):
        return value.decode('utf-8')


def sanitize_item(item: Any) -> Any:
    if isinstance(item, dt.date):
        rv = item.isoformat()
    elif hasattr(item, 'dict'):
        rv = item.dict()
    else:
        rv = item
    return rv


def redis_to_dit(obj, exclude_fields: list = None) -> dict:
    excluded = ['o_id']
    response = {
        key: sanitize_item(value)
        for key, value in obj._data.items()
        if key not in excluded
    }
    return response
