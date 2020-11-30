import functools
from typing import Any, Callable

from chalice import Response
from chalice.app import MethodNotAllowedError

from agave.repositories.query_result import QueryResult


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
                formatted = [formatter(item) for item in results]
            elif isinstance(results, dict):
                formatted = results  # type: ignore
            else:
                formatted = formatter(results)
            return Response(formatted, status_code=status_code)

        return wrapper

    return wrap_builder
