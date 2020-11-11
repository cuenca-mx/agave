from typing import ClassVar, Dict

from ..lib.mongoengine.model_helpers import mongo_to_dict


class BaseModel:
    _excluded: ClassVar = []
    _hidden: ClassVar = []

    def __init__(self, *args, **values):
        return super().__init__(*args, **values)

    def to_dict(self) -> Dict:
        private_fields = [f for f in dir(self) if f.startswith('_')]
        excluded = self._excluded + private_fields
        mongo_dict: dict = mongo_to_dict(self, excluded)

        for field in self._hidden:
            mongo_dict[field] = '********'
        return mongo_dict

    def __repr__(self) -> str:
        return str(self.to_dict())  # pragma: no cover
