__all__ = []


try:
    import mongoengine
except ImportError:
    ...
else:
    from .mongo import MongoModel

    __all__.append('MongoModel')


try:
    import rom
except ImportError:
    ...
else:
    from .redis import RedisModel

    __all__.append('RedisModel')
