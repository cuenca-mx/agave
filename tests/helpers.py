import base64
import functools
import json as jsonlib
from typing import Callable, Dict, Generator, List

from mongoengine import Document

FuncDecorator = Callable[..., Generator]


def auth_header(username: str, password: str) -> Dict:
    creds = base64.b64encode(f'{username}:{password}'.encode('ascii')).decode(
        'utf-8'
    )
    return {
        'Authorization': f'Basic {creds}',
        'Content-Type': 'application/json',
    }


def collection_fixture(model: Document) -> Callable[..., FuncDecorator]:
    def collection_decorator(func: Callable) -> FuncDecorator:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Generator[List, None, None]:
            items = func(*args, **kwargs)
            for item in items:
                item.save()
            yield items
            model.objects.delete()

        return wrapper

    return collection_decorator


def accept_json(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(path, json=None, **kwargs):
        body = jsonlib.dumps(json) if json else None
        headers = {'Content-Type': 'application/json'}
        return func(path, body=body, headers=headers, **kwargs)

    return wrapper
