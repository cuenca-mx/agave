from collections import OrderedDict
from typing import ClassVar, Dict

from .helpers import DynamicLazyReferenceField, mongo_to_dict


class BaseModel:
    _excluded: ClassVar = []
    _hidden: ClassVar = []

    def __init__(self, *args, **values):
        values = self.priority_dynamic_field(values)
        return super().__init__(*args, **values)

    def priority_dynamic_field(self, values):
        dynamic_fields = [
            name
            for name, field in self._fields.items()
            if isinstance(field, DynamicLazyReferenceField)
        ]
        if not dynamic_fields:
            return values
        for field_name in dynamic_fields:
            if field_name not in values:
                continue
            values = OrderedDict(values)
            values.move_to_end(field_name)
        return values

    def to_dict(self) -> Dict:
        private_fields = [f for f in dir(self) if f.startswith('_')]
        excluded = self._excluded + private_fields
        mongo_dict: dict = mongo_to_dict(self, excluded)

        for field in self._hidden:
            mongo_dict[field] = '********'
        return mongo_dict

    def __repr__(self) -> str:
        return str(self.to_dict())  # pragma: no cover
