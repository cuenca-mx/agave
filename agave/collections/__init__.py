__all__ = ['BaseCollection', 'QueryResult']


from .base import BaseCollection
from .mongo.mongo_collection import MongoCollection
from .query_result import QueryResult
from .redis.redis_collection import RedisCollection
