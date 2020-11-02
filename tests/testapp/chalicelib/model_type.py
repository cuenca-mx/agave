from mongoengine import StringField

from .resource_user import User


class Type(User):
    type = StringField
