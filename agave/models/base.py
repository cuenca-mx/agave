from typing import Callable, ClassVar

from cuenca_validations.typing import DictStrAny


class BaseModel:
    _excluded: ClassVar = []
    _hidden: ClassVar = []

    def __init__(self, *args, **values):
        return super().__init__(*args, **values)

    def _dict(self, dict_func: Callable) -> DictStrAny:
        private_fields = [f for f in dir(self) if f.startswith('_')]
        excluded = self._excluded + private_fields
        model_dict = dict_func(self, excluded)

        for field in self._hidden:
            model_dict[field] = '********'
        return model_dict

    def __repr__(self) -> str:
        return str(self.dict())  # type: ignore # pragma: no cover
