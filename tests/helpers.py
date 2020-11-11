import functools
import json as jsonlib
from typing import Callable, Dict, Generator

FuncDecorator = Callable[..., Generator]


def auth_header(username: str, password: str) -> Dict:
    creds = username + password
    return {
        'Authorization': f'Basic {creds}',
    }


def accept_json(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(path, json=None, **kwargs):
        body = jsonlib.dumps(json) if json else None
        headers = {'Content-Type': 'application/json'}
        return func(path, body=body, headers=headers, **kwargs)

    return wrapper
