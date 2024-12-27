from cuenca_validations.errors import CuencaError
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.routing import Match

from ..exc import FastAgaveError, MethodNotAllowedError, NotFoundError


class FastAgaveErrorHandler(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            request.scope['route_handler'] = get_current_route_handler(request)
            return await call_next(request)
        except CuencaError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content=dict(
                    code=exc.code,
                    error=str(exc),
                ),
            )
        except FastAgaveError as exc:
            return JSONResponse(
                status_code=exc.status_code, content=dict(error=exc.error)
            )


def get_current_route_handler(request: Request) -> APIRoute:
    """
    Helper method for getting the route handler of the current request.

    If there is not route handler it raises appropriate status code error
    consistent with the `Route.__call__` behavior
    https://github.com/encode/starlette/blob/5d768322d6d7adc31df54b1ad306f417e3da2c81/starlette/routing.py#L656-L666
    Args:
        request: fastapi request object

    Returns:
        APIRoute instance for the current request
    """
    partial = None
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return route
        if match == Match.PARTIAL and partial is None:
            partial = route

    if partial is not None:
        raise MethodNotAllowedError('Method Not Allowed')
    else:
        raise NotFoundError('Not Found')
