from typing import Any, Dict, Tuple, Type, Union
from urllib.parse import urlencode

from chalice import Blueprint, NotFoundError
from cuenca_validations.types import QueryParams

from agave.repositories.query_result import QueryResult

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

    def query_delimiter(self, **__) -> Any:
        return {}

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

            def default_query_handler(
                query_params: QueryParams,
            ) -> Union[Dict, QueryResult]:
                delimiter = self.query_delimiter()
                if query_params.count:
                    count = resource.repository.count(
                        query_params, **delimiter
                    )
                    return dict(count=count)

                query_result = resource.repository.all(
                    query_params, **delimiter
                )
                if query_result.has_more and query_result.wants_more:
                    query_params.created_before = (
                        query_result.last_created_at.isoformat()
                    )
                    path = self.current_request.context['resourcePath']
                    params = query_params.dict()
                    # TODO: lógica para remover el filtro `user_id`
                    query_result.next_page = f'{path}?{urlencode(params)}'

                return query_result

            def get_model_or_raise_not_found(resource_id: str) -> Any:
                # TODO: lógica para restringir el `user_id`
                delimiters = self.query_delimiter()
                try:
                    model = resource.repository.get_by_id(
                        resource_id, **delimiters
                    )
                except ModelDoesNotExist:
                    raise NotFoundError('Not valid id')
                return model

        return resource_class_wrapper
