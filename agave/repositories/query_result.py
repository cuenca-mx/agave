import datetime as dt
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class QueryResult:
    items: List[Any]
    has_more: Optional[bool]
    last_created_at: Optional[dt.datetime]
    next_page: Optional[str]
