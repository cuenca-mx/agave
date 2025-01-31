import json
import logging
import sys
from typing import Union

from fastapi import Request
from fastapi.routing import APIRoute
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from agave.core.utilis.loggers import (
    EXCLUDED_HEADERS,
    SENSITIVE_HEADERS,
    SENSITIVE_REQUEST_MODEL_FIELDS,
    SENSITIVE_RESPONSE_MODEL_FIELDS,
    obfuscate_sensitive_body,
    obfuscate_sensitive_headers,
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

SENSITIVE_HEADERS.update(
    {
        'authorization',
        'X-Cuenca-Token',
        'X-Cuenca-LoginId',
        'X-Cuenca-LoginToken',
        'X-Cuenca-SessionId',
    }
)

EXCLUDED_HEADERS.update(
    {
        'connection',
    }
)


def parse_body(body: bytes) -> Union[dict, None]:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


class AgaveRequestLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = dict(request.headers)

        body = await request.body()
        response = await call_next(request)

        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        # Create new response with the same content
        # This is necessary because we consumed the original response
        new_response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        # Get request and response models
        route = request.scope.get("route")

        response_model = (
            route.response_model.__name__
            if isinstance(route, APIRoute)
            and hasattr(route.response_model, "__name__")
            else ""
        )

        request_model = (
            next(
                (
                    dep.type_.__name__
                    for dep in route.dependant.body_params
                    if isinstance(dep.type_, type)
                    and issubclass(dep.type_, BaseModel)
                ),
                "",
            )
            if isinstance(route, APIRoute)
            else ""
        )

        body_decoded = parse_body(body) if body else None

        obfuscated_request_body = (
            obfuscate_sensitive_body(
                body_decoded, request_model, SENSITIVE_REQUEST_MODEL_FIELDS
            )
            if body_decoded
            else None
        )

        obfuscated_headers = obfuscate_sensitive_headers(headers)

        request_info = {
            "method": request.method,
            "url": str(request.url),
            "query_params": request.query_params,
            "headers": obfuscated_headers,
            "body": obfuscated_request_body,
        }

        parsed_body = parse_body(response_body) if response_body else None

        obfuscated_response_body = (
            obfuscate_sensitive_body(
                parsed_body,
                response_model,
                SENSITIVE_RESPONSE_MODEL_FIELDS,
            )
            if parsed_body and isinstance(parsed_body, dict)
            else None
        )

        response_info = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": obfuscated_response_body,
        }

        completed_request_info = {
            "request": request_info,
            "response": response_info,
        }

        logger.info(f"Info: {json.dumps(completed_request_info, default=str)}")

        return new_response
