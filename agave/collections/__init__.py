__all__ = ['BaseCollection', 'QueryResult']


from .base import BaseCollection
from .query_result import QueryResult
from .mongo.mongo_collection import MongoCollection
from .redis.redis_collection import RedisCollection
