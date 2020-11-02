import base64
import functools
import json as jsonlib
from typing import Callable, Dict, Generator

FuncDecorator = Callable[..., Generator]


def auth_header(username: str, password: str) -> Dict:
    creds = base64.b64encode(f'{username}:{password}'.encode('ascii')).decode(
        'utf-8'
    )
    return {
        'Authorization': f'Basic {creds}',
        'Content-Type': 'application/json',
    }


def accept_json(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(path, json=None, **kwargs):
        if 'body' in kwargs:
            return func(path, **kwargs)
        body = jsonlib.dumps(json) if json else None
        return func(path, body=body, **kwargs)

    return wrapper
