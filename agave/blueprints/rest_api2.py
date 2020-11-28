import functools
from inspect import signature
from typing import Any, Callable, Dict, Type, Tuple

from chalice import BadRequestError, Blueprint, NotFoundError, Response
from chalice.app import MethodNotAllowedError
from cuenca_validations.types import QueryParams
from cuenca_validations.typing import DictStrAny
from pydantic import BaseModel, ValidationError

from ..exc import ModelDoesNotExist

RespTuple = Tuple[Any, int]


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
        def resource_class_wrapper(resource: Type) -> None:
            try:
                formatter = resource.formatter
            except AttributeError:
                formatter = DefaultFormatter

            @self.get(path + '/{resource_id}')
            @format_with(formatter)
            def retrieve(resource_id: str) -> RespTuple:
                if not hasattr(resource, 'retrieve'):
                    result = default_retrieve_handler(resource_id)
                else:
                    result = resource().retrieve(resource_id)
                return response(result)

            @self.get(path)
            @format_with(formatter)
            def query() -> RespTuple:
                query_params = self.current_request.query_params
                if not hasattr(resource, 'query'):
                    request = validate_request(
                        resource.query_validator, query_params
                    )
                    result = default_query_handler(request)
                else:
                    params = transform_request(
                        resource.query, 'query_params', query_params
                    )
                    result = resource().query(query_params=params)
                return response(result)

            @self.post(path)
            @if_handler_exist_in(resource)
            @format_with(formatter)
            def create() -> RespTuple:
                request = transform_request(
                    resource.create, 'request', self.current_request.json_body
                )
                result = resource().create(request)
                return response(result, 201)

            @self.patch(path + '/{resource_id}')
            @if_handler_exist_in(resource)
            @format_with(formatter)
            def update(resource_id: str) -> RespTuple:
                request = transform_request(
                    resource.create, 'request', self.current_request.json_body
                )
                model = get_resource_or_raise_not_found(resource_id)
                result = resource().update(model, request)
                return response(result)

            @self.delete(path + '/{resource_id}')
            @if_handler_exist_in(resource)
            @format_with(formatter)
            def delete(resource_id: str) -> RespTuple:
                model = get_resource_or_raise_not_found(resource_id)
                result = resource().delete(model)
                return response(result)

            def default_retrieve_handler(resource_id: str) -> Any:
                return get_resource_or_raise_not_found(resource_id)

            def default_query_handler(request: QueryParams) -> Any:
                filters = resource.get_query_filter(request)
                if request.count:
                    count = resource.repository.count(filters)
                    return dict(count=count)
                else:
                    return resource.repository.all(filters)

            def response(result: Any, status_code: int = 200) -> RespTuple:
                if type(result) is tuple:
                    return result
                else:
                    return result, status_code

            def get_resource_or_raise_not_found(resource_id: str) -> Any:
                try:
                    model = resource.repository.get_by_id(resource_id)
                except ModelDoesNotExist:
                    raise NotFoundError('Not valid id')
                return model


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


def format_with(formatter: Any):
    def wrap_builder(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Dict:
            results, status_code = func(*args, **kwargs)
            if isinstance(results, list):
                formatted = [formatter(item) for item in results]
            elif isinstance(results, dict):
                formatted = results
            else:
                formatted = formatter(results)
            return Response(formatted, status_code=status_code)

        return wrapper

    return wrap_builder


class DefaultFormatter:
    def __call__(self, instance: Any) -> Dict:
        return instance.to_dict()
