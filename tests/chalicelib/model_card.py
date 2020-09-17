import datetime as dt
from typing import Dict

from cuenca_validations.types import CardStatus
from mongoengine import DateTimeField, Document, StringField

from agave.models.helpers import EnumField, uuid_field


class Card(Document):

    id = StringField(primary_key=True, default=uuid_field('CA'))
    created_at = DateTimeField(default=dt.datetime.utcnow)
    updated_at = DateTimeField(default=dt.datetime.utcnow)
    status: CardStatus = EnumField(
        CardStatus, required=True, default=CardStatus.active
    )

    def to_dict(self) -> Dict:
        """Returns a dictionary with data that represents a transfer request
        for Cuenca core

        Note:
            Since `reference_number` is an optional value
             `None` values are allowed
        """
        return dict(id=self.id, status=self.status,)
