import datetime as dt
from typing import Any, ClassVar, Dict

from rom import Model, PrimaryKey


def sanitize_item(item: Any) -> Any:
    if isinstance(item, dt.date):
        rv = item.isoformat()
    elif hasattr(item, 'dict'):
        rv = item.dict()
    else:
        rv = item
    return rv


class BaseModel(Model):
    o_id = PrimaryKey()  # Para que podamos usar `id` en los modelos
    _excluded: ClassVar = []
    _hidden: ClassVar = []

    def dict(self) -> Dict:
        """
        La librería rom ya utiliza el método to_dict para almacenar
        los datos en Redis, por lo que hacer un cambio en esa función
        provoca que los datos se guarden de forma érronea
        """
        private_fields = [f for f in dir(self) if f.startswith('_')]
        excluded = self._excluded + private_fields

        response = {
            key: sanitize_item(value)
            for key, value in self._data.items()
            if key not in excluded
        }

        for field in self._hidden:
            response[field] = '********'
        return response
