import datetime as dt
from typing import Any

from blinker import NamedSignal
from mongoengine import signals


def handler(event: NamedSignal):
    """
    http://docs.mongoengine.org/guide/signals.html?highlight=update
    Signal decorator to allow use of callback functions as class
    decorators
    """

    def decorator(fn: Any):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn

    return decorator


@handler(signals.pre_save)
def updated_at(_, document):
    document.updated_at = dt.datetime.utcnow()
