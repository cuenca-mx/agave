from enum import Enum
from typing import Type

from mongoengine.base import BaseField


class EnumField(BaseField):
    """
    https://github.com/MongoEngine/extras-mongoengine/blob/master/
    extras_mongoengine/fields.py
    A class to register Enum type (from the package enum34) into mongo
    :param choices: must be of :class:`enum.Enum`: type
        and will be used as possible choices
    """

    def __init__(self, enum: Type[Enum], *args, **kwargs):
        self.enum = enum
        kwargs['choices'] = [choice for choice in enum]
        super(EnumField, self).__init__(*args, **kwargs)

    def __get_value(self, enum: Enum) -> str:
        return enum.value if hasattr(enum, 'value') else enum

    def to_python(self, value: Enum) -> Enum:  # pragma: no cover
        return self.enum(super(EnumField, self).to_python(value))

    def to_mongo(self, value: Enum) -> str:
        return self.__get_value(value)

    def prepare_query_value(self, op, value: Enum) -> str:
        return super(EnumField, self).prepare_query_value(  # pragma: no cover
            op, self.__get_value(value)
        )

    def validate(self, value: Enum) -> Enum:
        return super(EnumField, self).validate(self.__get_value(value))

    def _validate(self, value: Enum, **kwargs) -> Enum:
        return super(EnumField, self)._validate(
            self.enum(self.__get_value(value)), **kwargs
        )
