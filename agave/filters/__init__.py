__all__ = ['generic_query_redis', 'generic_query']

from .filters_mongo import generic_query
from .filters_redis import generic_query_redis
