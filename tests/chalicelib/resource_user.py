from chalice import NotFoundError, Response
from mongoengine import DoesNotExist, ValidationError

from tests.chalicelib._generic_query import generic_query
from tests.chalicelib.model_user import User as UserModel

from .base import app
from .queries import USerQuery
from .request import NameRequest


@app.resource('/foo')
class User:
    model = UserModel
    query_validator = USerQuery
    get_query_filter = generic_query

    _no_user_filter = True

    @staticmethod
    @app.validate(NameRequest)
    def create(name: NameRequest) -> Response:
        user = UserModel()
        user.create(name)
        try:
            user.save()
            status_code = 201
        except ValidationError as e:
            status_code = e
        return Response(user.to_dict(), status_code=status_code)

    @staticmethod
    def delete(id: str) -> Response:
        try:
            id_user = UserModel.objects.get(id=id)
        except DoesNotExist:
            raise NotFoundError('Not valid id')
        code = app.current_request.json_body.get('code')
        id_user.deactivate(code)
        return Response(id_user.deactivated, status_code=200)
