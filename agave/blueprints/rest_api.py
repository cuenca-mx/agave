from typing import Any, Tuple, Type
from urllib.parse import urlencode

from chalice import Blueprint, NotFoundError
from cuenca_validations.types import QueryParams

from ..exc import ModelDoesNotExist
from .decorators import (
    configure,
    copy_properties_from,
    format_with,
    if_handler_exist_in,
)
from .tools import (
    default_formatter,
    response,
    transform_request,
    validate_request,
)


class RestApiBlueprint(Blueprint):
    def get(self, path: str, **kwargs):
        return self.route(path, methods=['GET'], **kwargs)

    def post(self, path: str, **kwargs):
        return self.route(path, methods=['POST'], **kwargs)

    def patch(self, path: str, **kwargs):
        return self.route(path, methods=['PATCH'], **kwargs)

    def delete(self, path: str, **kwargs):
        return self.route(path, methods=['DELETE'], **kwargs)

    def query_delimiter(self, **__) -> Any:
        """
        Constraints query filters.

        The default implementation for this `query_delimiter` does not
        constraint anything. You are responsible of overriding this method
        in a child Blueprint implementation
        :param __:
        :return:
        """
        return {}  # pragma: no cover

    def resource(self, path: str):
        def resource_class_wrapper(resource_class: Type[Any]) -> None:
            try:
                formatter = resource_class.formatter
            except AttributeError:
                formatter = default_formatter

            def default_retrieve_handler(_, resource_id: str) -> Any:
                return get_model_or_raise_not_found(resource_id)

            def default_query_handler(_, query_params: QueryParams) -> Any:
                delimiter = self.query_delimiter()
                if query_params.count:
                    count = resource_class.collection.count(
                        query_params, **delimiter
                    )
                    return dict(count=count)

                query_result = resource_class.collection.all(
                    query_params, **delimiter
                )
                if query_result.has_more and query_result.wants_more:
                    query_params.created_before = (
                        query_result.last_created_at.isoformat()
                    )
                    path = self.current_request.context['resourcePath']
                    params = query_params.dict()
                    query_result.next_page = f'{path}?{urlencode(params)}'

                return query_result

            def get_model_or_raise_not_found(resource_id: str) -> Any:
                delimiters = self.query_delimiter()
                try:
                    model = resource_class.collection.retrieve(
                        resource_id, **delimiters
                    )
                except ModelDoesNotExist:
                    raise NotFoundError('Not valid id')
                return model

            @self.get(path + '/{resource_id}')
            @configure(resource_class, retrieve=default_retrieve_handler)
            @copy_properties_from(resource_class)
            @format_with(formatter)
            def retrieve(resource, resource_id: str) -> Tuple[Any, int]:
                result = resource.retrieve(resource_id)
                return response(result)

            @self.get(path)
            @configure(resource_class, query=default_query_handler)
            @copy_properties_from(resource_class)
            @format_with(formatter)
            def query(resource) -> Tuple[Any, int]:
                query_params = self.current_request.query_params
                if resource.query.is_default:
                    params = validate_request(
                        resource_class.query_validator, query_params
                    )
                else:
                    params = transform_request(
                        resource_class.query, 'query_params', query_params
                    )
                result = resource.query(params)
                return response(result)

            @self.post(path)
            @if_handler_exist_in(resource_class)
            @configure(resource_class)
            @copy_properties_from(resource_class)
            @format_with(formatter)
            def create(resource) -> Tuple[Any, int]:
                request = transform_request(
                    resource_class.create,
                    'request',
                    self.current_request.json_body,
                )
                result = resource.create(request)
                return response(result, 201)

            @self.patch(path + '/{resource_id}')
            @if_handler_exist_in(resource_class)
            @configure(resource_class)
            @copy_properties_from(resource_class)
            @format_with(formatter)
            def update(resource, resource_id: str) -> Tuple[Any, int]:
                request = transform_request(
                    resource_class.create,
                    'request',
                    self.current_request.json_body,
                )
                model = get_model_or_raise_not_found(resource_id)
                result = resource.update(model, request)
                return response(result)

            @self.delete(path + '/{resource_id}')
            @if_handler_exist_in(resource_class)
            @configure(resource_class)
            @copy_properties_from(resource_class)
            @format_with(formatter)
            def delete(resource, resource_id: str) -> Tuple[Any, int]:
                model = get_model_or_raise_not_found(resource_id)
                result = resource.delete(model)
                return response(result)

        return resource_class_wrapper
