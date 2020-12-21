from typing import Any, Dict

from cuenca_validations.types import QueryParams


def exclude_fields(query: QueryParams) -> Dict[str, Any]:
    exclude_fields = {
        'created_before',
        'created_after',
        'active',
        'limit',
        'page_size',
        'key',
    }
    fields = query.dict(exclude=exclude_fields)
    if 'count' in fields:
        del fields['count']
    return fields
