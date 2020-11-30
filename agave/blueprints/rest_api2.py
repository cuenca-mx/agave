from typing import Any, Tuple, Type

from chalice import Blueprint, NotFoundError
from cuenca_validations.types import QueryParams

from ..exc import ModelDoesNotExist
from .decorators import format_with, if_handler_exist_in
from .tools import (
    default_formatter,
    response,
    transform_request,
    validate_request,
)


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
        def resource_class_wrapper(resource: Type[Any]) -> None:
            try:
                formatter = resource.formatter
            except AttributeError:
                formatter = default_formatter

            @self.get(path + '/{resource_id}')
            @format_with(formatter)
            def retrieve(resource_id: str) -> Tuple[Any, int]:
                if not hasattr(resource, 'retrieve'):
                    result = default_retrieve_handler(resource_id)
                else:
                    result = resource().retrieve(resource_id)
                return response(result)

            @self.get(path)
            @format_with(formatter)
            def query() -> Tuple[Any, int]:
                query = self.current_request.query_params
                if not hasattr(resource, 'query'):
                    request = validate_request(resource.query_validator, query)
                    result = default_query_handler(request)
                else:
                    params = transform_request(
                        resource.query, 'query_params', query
                    )
                    result = resource().query(params)
                return response(result)

            @self.post(path)
            @if_handler_exist_in(resource)
            @format_with(formatter)
            def create() -> Tuple[Any, int]:
                request = transform_request(
                    resource.create, 'request', self.current_request.json_body
                )
                result = resource().create(request)
                return response(result, 201)

            @self.patch(path + '/{resource_id}')
            @if_handler_exist_in(resource)
            @format_with(formatter)
            def update(resource_id: str) -> Tuple[Any, int]:
                request = transform_request(
                    resource.create, 'request', self.current_request.json_body
                )
                model = get_model_or_raise_not_found(resource_id)
                result = resource().update(model, request)
                return response(result)

            @self.delete(path + '/{resource_id}')
            @if_handler_exist_in(resource)
            @format_with(formatter)
            def delete(resource_id: str) -> Tuple[Any, int]:
                model = get_model_or_raise_not_found(resource_id)
                result = resource().delete(model)
                return response(result)

            def default_retrieve_handler(resource_id: str) -> Any:
                return get_model_or_raise_not_found(resource_id)

            def default_query_handler(query_params: QueryParams) -> Any:
                if query_params.count:
                    count = resource.repository.count(query_params)
                    return dict(count=count)
                else:
                    return resource.repository.all(query_params)

            def get_model_or_raise_not_found(resource_id: str) -> Any:
                try:
                    model = resource.repository.get_by_id(resource_id)
                except ModelDoesNotExist:
                    raise NotFoundError('Not valid id')
                return model

        return resource_class_wrapper
