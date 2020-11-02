from typing import Optional

from cuenca_validations.types import QueryParams


class USerQuery(QueryParams):
    key: Optional[str] = None
