from mongoengine import StringField

from tests.testapp.chalicelib.resources.users import User


class Deposit(User):
    type = StringField
