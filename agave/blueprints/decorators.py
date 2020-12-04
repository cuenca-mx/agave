import functools
from typing import Any, Callable, Optional, Type

from chalice import Response
from chalice.app import MethodNotAllowedError

from ..collections import QueryResult


def if_handler_exist_in(resource: Any) -> Callable:
    """
    It only validates that function handler exist in the resource
    class definition with the same name as the decorated handler.

    If it not exist then raises `MethodNotAllowedError`
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
    """
    Formats the `results` object with `formatter`.

    `formatter` could be a function or Callable object. The default formatter
    is a function that converts the results instance to Dict representation.


    :param formatter: function or Callable object
    :return function wrapper:
    """

    def wrap_builder(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Response:
            results, status_code = func(*args, **kwargs)
            if isinstance(results, QueryResult):
                formatted = dict(
                    items=[formatter(item) for item in results.items],
                    next_page_uri=results.next_page,
                )
            elif isinstance(results, list):
                formatted = [
                    formatter(item) for item in results
                ]  # type: ignore
            elif isinstance(results, dict):
                formatted = results  # type: ignore
            else:
                formatted = formatter(results)
            return Response(formatted, status_code=status_code)

        return wrapper

    return wrap_builder


def configure(
    resource: Type[Any],
    retrieve: Optional[Callable] = None,
    query: Optional[Callable] = None,
):
    """
    Setup missing resource handlers and create an instance of `resource`
    so we can avoid decorate every resource handler with @staticmethod

    :param resource: Class representing the resource definition
    :param retrieve: Default retrieve handler
    :param query: Default query handler
    :return: wrapper function
    """
    if retrieve:
        if not hasattr(resource, 'retrieve'):
            resource.retrieve = retrieve
            resource.retrieve.is_default = True  # type: ignore
        else:
            resource.retrieve.is_default = False

    if query:
        if not hasattr(resource, 'query'):
            resource.query = query
            resource.query.is_default = True  # type: ignore
        else:
            resource.query.is_default = False

    def wrap_builder(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            instance = resource()
            return func(instance, *args, **kwargs)

        return wrapper

    return wrap_builder


def copy_properties_from(resource: Type[Any]):
    """
    Copy every attached property from resource methods definition to the
    real function handler.

    :param resource: Class representing the resource definition
    :return: wrapper function
    """

    def wrapper(func: Callable):
        try:
            original_func = getattr(resource, func.__name__)
        except AttributeError:
            return func

        if not getattr(original_func, 'is_default', False):
            for key, val in original_func.__dict__.items():
                setattr(func, key, val)

        return func

    return wrapper
