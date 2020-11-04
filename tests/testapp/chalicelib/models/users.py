import datetime as dt

from mongoengine import DateTimeField, Document, StringField

from agave.models.base import BaseModel
from tests.testapp.chalicelib.request import NameRequest


class User(BaseModel, Document):
    id = StringField
    created_at = DateTimeField(default=dt.datetime.utcnow)
    name = StringField
    key = StringField
    deactivated = StringField

    def create(self, data: NameRequest) -> None:
        self.name = data.name
        self.key = data.key

    def deactivate(self, code: int) -> None:
        self.deactivated = code

    def update(self, data: NameRequest) -> None:
        self.name = data.name
