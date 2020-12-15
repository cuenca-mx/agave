__all__ = []

try:
    import mongoengine  # noqa
except ImportError:
    ...
else:
    from .mongo import MongoModel  # noqa

    __all__.append('MongoModel')


try:
    import rom  # noqa
except ImportError:
    ...
else:
    from .redis import RedisModel  # noqa

    __all__.append('RedisModel')
