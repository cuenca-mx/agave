from typing import Any, Dict
from examples.chalicelib.blueprints import AuthedRestApiBlueprint
from ..models import Account as Model


class AccountFormatter:
    def __init__(self, app: AuthedRestApiBlueprint):
        self.app = app

    def __call__(self, instance: Model) -> Dict:
        data = instance.to_dict()
        secret = data.get('secret')
        if secret:
            data['secret'] = secret[0:10] + ('*' * 10)
        return data


def redis_formatter(instance: Any) -> Dict:
    return instance.dict()
