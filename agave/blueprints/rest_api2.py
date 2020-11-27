import functools
from inspect import signature
from typing import Any, Callable, Dict, Type

from chalice import BadRequestError, Blueprint, NotFoundError, Response
from chalice.app import MethodNotAllowedError
from cuenca_validations.types import QueryParams
from cuenca_validations.typing import DictStrAny
from pydantic import BaseModel, ValidationError

from ..exc import ModelDoesNotExist


class RestApiBlueprintV2(Blueprint):
    def get(self, path: str, **kwargs):
        return self.route(path, methods=['GET'], **kwargs)

    def post(self, path: str, **kwargs):
        return self.route(path, methods=['POST'], **kwargs)

    def patch(self, path: str, **kwargs):
        return self.route(path, methods=['PATCH'], **kwargs)

    def delete(self, path: str, **kwargs):
        return self.route(path, methods=['DELETE'], **kwargs)

    @property
    def current_user_id(self):
        return self.current_request.user_id

    def resource(self, path: str):
        def resource_class_wrapper(resource):
            @self.get(path + '/{resource_id}')
            def retrieve(resource_id: str) -> Response:
                if not hasattr(resource, 'retrieve'):
                    return default_retrieve_handler(resource_id)

                # you can inject new attributes or tools inside
                # the class instance for some custom logic
                result = resource().retrieve(resource_id)
                if type(result) is tuple:
                    model, status_code = result
                    return Response(model.to_dict(), status_code=status_code)
                else:
                    return Response(result.to_dict())

            @self.get(path)
            def query():
                query_params = self.current_request.query_params
                if not hasattr(resource, 'query'):
                    request = validate_request(
                        resource.query_validator, query_params
                    )
                    return default_query_handler(request)
                else:
                    params = transform_request(
                        resource.query, 'query_params', query_params
                    )
                    resp = resource().query(query_params=params)
                    return resp

            @self.post(path)
            @if_handler_exist_in(resource)
            def create():
                request = transform_request(
                    resource.create, 'request', self.current_request.json_body
                )
                result = resource().create(request)
                if type(result) is tuple:
                    model, status_code = result
                    return Response(model.to_dict(), status_code=status_code)
                else:
                    return Response(result.to_dict(), status_code=201)

            @self.patch(path + '/{resource_id}')
            @if_handler_exist_in(resource)
            def update(resource_id: str):
                request = transform_request(
                    resource.create, 'request', self.current_request.json_body
                )
                try:
                    model = resource.repository.get_by_id(resource_id)
                except ModelDoesNotExist:
                    raise NotFoundError('Not valid id')

                result = resource().update(model, request)
                if type(result) is tuple:
                    model, status_code = result
                    return Response(model.to_dict(), status_code=status_code)
                else:
                    return Response(result.to_dict())

            @self.delete(path + '/{resource_id}')
            @if_handler_exist_in(resource)
            def delete(resource_id: str):
                try:
                    model = resource.repository.get_by_id(resource_id)
                except ModelDoesNotExist:
                    raise NotFoundError('Not valid id')

                result = resource().delete(model)
                if type(result) is tuple:
                    model, status_code = result
                    return Response(model.to_dict(), status_code=status_code)
                else:
                    return Response(result.to_dict())

            def default_retrieve_handler(resource_id: str) -> Response:
                try:
                    result = resource.repository.get_by_id(resource_id)
                except ModelDoesNotExist:
                    raise NotFoundError('Not valid id')
                return Response(result.to_dict())

            def default_query_handler(request: QueryParams) -> Response:
                filters = resource.get_query_filter(request)
                if request.count:
                    count = resource.repository.count(filters)
                    result = dict(count=count)
                else:
                    result = resource.repository.all(filters)

                return Response([r.to_dict() for r in result])

        return resource_class_wrapper


def get_params_annotations(method: Callable) -> Dict[str, type]:
    """
    gets param annotations from method/function signature.
    example:

    if you have

    def query(query_params: QueryRequest) -> Any:
        ...

    then you can do:

    result = get_params_annotations(query)
    assert result == dict(query_params=QueryRequest)

    """
    sig = signature(method)
    annotations_dict = {
        key: param.annotation for key, param in sig.parameters.items()
    }
    return annotations_dict


def validate_request(
    validator: Type[BaseModel], data: DictStrAny
) -> BaseModel:
    try:
        request = validator(**data)
    except ValidationError as exc:
        raise BadRequestError(exc.json())
    return request


def transform_request(
    handler: Callable, validator_name: str, data: DictStrAny
) -> BaseModel:
    """
    transform `data` dictionary into a validator associated
    to `validator_name` param.

    `validator_name` should exist in the function signature.

    Example:

    @app.resource('/my_resource')
    class MyResource:

      def query(query_param: QueryRequest):
        ...


     request = dict(user_id='US123', ...)

     # then you can transform `request` into `QueryRequest`
     # if request values are valid it returns `QueryRequest` object
     # else it raises BadRequestError

     query_params = transform_request(MyResource.query, 'query_param', request)
    """
    annotations = get_params_annotations(handler)
    validator = annotations[validator_name]
    return validate_request(validator, data)


def if_handler_exist_in(resource: Any) -> Callable:
    """
    It only validates that function handler exist in the
    resource class definitionwith the same name
    as the decorated handler.

    If it not exist then returns `MethodNotAllowedError`
    """

    def wrap_builder(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not hasattr(resource, func.__name__):
                raise MethodNotAllowedError
            return func(*args, **kwargs)

        return wrapper

    return wrap_builder
