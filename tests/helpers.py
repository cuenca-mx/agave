import base64
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
