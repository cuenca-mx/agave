from dataclasses import dataclass
from typing import Optional

from mongoengine.base import BaseField


@dataclass
class FundingInstrument:
    id: str
    uri: Optional[str]


class FundingInstrumentField(BaseField):
    mapper = {
        'BA': '/accounts',
        'CA': '/cards',
        'SP': '/service_providers',
    }

    def to_python(self, value: str) -> FundingInstrument:
        fi = FundingInstrument(id=value, uri=None)
        if value[:2] in self.mapper.keys():
            fi.uri = f'{self.mapper[value[:2]]}/{value}'
        return fi

    def to_mongo(self, value: FundingInstrument) -> str:
        return value.id

    def validate(self, value):
        if not value.uri:
            self.error(f"Invalid ID: {value}")
