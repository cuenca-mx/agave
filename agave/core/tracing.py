from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable

import newrelic.agent

# trace headers key
TRACE_HEADERS_KEY = "_nr_trace_headers"


def get_trace_headers() -> dict:
    headers_list: list = []
    newrelic.agent.insert_distributed_trace_headers(headers_list)
    return dict(headers_list)


def accept_trace_headers(
    headers: dict | None, transport_type: str = "HTTP"
) -> None:
    """
    Accept incoming trace headers to continue a distributed trace.

    Args:
        headers: Trace headers from incoming request/message.
        transport_type: "HTTP" for HTTP requests, "Queue" for queue messages.
    """
    if not headers:
        return
    newrelic.agent.accept_distributed_trace_headers(
        headers, transport_type=transport_type
    )


def add_custom_attribute(key: str, value: Any) -> None:
    if value is not None:
        newrelic.agent.add_custom_attribute(key, value)


def accept_trace_from_queue(func: Callable) -> Callable:
    """
    Decorator to accept distributed trace headers from queue messages.

    Extracts '_nr_trace_headers' from kwargs, accepts them, and removes
    them before calling the function.

    Example:
        @celery_sqs.task
        @accept_trace_from_queue
        def process_incoming_spei_transaction_task(
            transaction: dict, session=None
        ):
            ...
    """

    def _accept(kwargs):
        trace_headers = kwargs.pop(TRACE_HEADERS_KEY, None)
        if trace_headers:
            accept_trace_headers(trace_headers, transport_type="Queue")

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _accept(kwargs)
            return await func(*args, **kwargs)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        _accept(kwargs)
        return func(*args, **kwargs)

    return sync_wrapper


def inject_trace_headers(param_name: str = "trace_headers"):
    """
    Decorator to inject trace headers into HTTP calls.

    Args:
        param_name: name of the parameter where headers will be injected.

    Example:
        @inject_trace_headers()
        async def request(self, method, endpoint, trace_headers=None):
            async with session.request(..., headers=trace_headers):
                ...
    """

    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        def _inject(args, kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            headers = dict(bound.arguments.get(param_name) or {})
            headers.update(get_trace_headers())
            bound.arguments[param_name] = headers
            return bound.args, bound.kwargs

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                new_args, new_kwargs = _inject(args, kwargs)
                return await func(*new_args, **new_kwargs)

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            new_args, new_kwargs = _inject(args, kwargs)
            return func(*new_args, **new_kwargs)

        return sync_wrapper

    return decorator


def trace_attributes(**extractors: Callable | str):
    """
    Decorator to add custom attributes to New Relic traces.

    Each kwarg is an attribute to add. The value can be:
    - str: name of the function parameter (e.g., 'folio_abono')
    - str with dot: path to an attribute (e.g., 'orden.clave_emisor')
    - callable: function that receives the kwargs and returns the value

    Example:
        @trace_attributes(
            clave_rastreo=lambda kw: ','.join(kw['orden'].claves_rastreo),
            clave_emisor='orden.clave_emisor',
            folio='folio_abono',
        )
        async def handle_orden(orden, folio_abono):
            ...
    """

    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        def _extract(args, kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            _add_attributes(bound.arguments, extractors)

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                _extract(args, kwargs)
                return await func(*args, **kwargs)

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            _extract(args, kwargs)
            return func(*args, **kwargs)

        return sync_wrapper

    return decorator


def _get_nested_value(obj: Any, path: str) -> Any:
    parts = path.split(".")
    value = (
        obj.get(parts[0])
        if isinstance(obj, dict)
        else getattr(obj, parts[0], None)
    )

    for part in parts[1:]:
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = getattr(value, part, None)
    return value


def _add_attributes(kwargs: dict, extractors: dict) -> None:
    """
    Internal function to extract and add attributes to the current trace.

    Args:
        kwargs: Function arguments.
        extractors: Dict of attribute_name -> extractor (callable or string).
    """
    for attr_name, extractor in extractors.items():
        try:
            if callable(extractor):
                value = extractor(kwargs)
            elif isinstance(extractor, str):
                value = _get_nested_value(kwargs, extractor)
            else:
                value = None

            add_custom_attribute(attr_name, value)
        except Exception:
            pass  # Silent exception
            # we don't want to fail if unable to extract an attribute
