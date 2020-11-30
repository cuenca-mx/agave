import datetime as dt
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class QueryResult:
    items: List[Any]
    has_more: Optional[bool] = None
    wants_more: Optional[bool] = None
    last_created_at: Optional[dt.datetime] = None
    next_page: Optional[str] = None
