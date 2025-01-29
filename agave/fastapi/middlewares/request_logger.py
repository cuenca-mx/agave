import json
import logging
import sys
from typing import Any, Union

from fastapi import Request
from fastapi.routing import APIRoute
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

AUTH_HEADER = 'authorization'
JWT_HEADER = 'X-Cuenca-Token'
LOGIN_HEADER = 'X-Cuenca-LoginId'
LOGIN_TOKEN_HEADER = 'X-Cuenca-LoginToken'
SESSION_HEADER = 'X-Cuenca-SessionId'

SENSITIVE_HEADERS = [
    AUTH_HEADER,
    JWT_HEADER,
    LOGIN_HEADER,
    LOGIN_TOKEN_HEADER,
    SESSION_HEADER,
]

EXCLUDED_HEADERS: list[str] = ['connection']
SENSITIVE_RESPONSE_MODEL_FIELDS: list[str] = []
SENSITIVE_REQUEST_MODEL_FIELDS: list[str] = []


def obfuscate_sensitive_headers(
    headers: dict[str, Any], sensitive_headers: list[str]
) -> dict[str, Any]:
    obfuscated = {
        k: v for k, v in headers.items() if k.lower() not in EXCLUDED_HEADERS
    }

    for header in sensitive_headers:
        if (value := obfuscated.get(header.lower())) and len(value) > 4:
            obfuscated[header.lower()] = f"{'*' * 5}{value[-4:]}"

    return obfuscated


def obfuscate_sensitive_body(
    body: dict[str, Any],
    model_name: str,
    sensitive_fields: list[str],
) -> dict[str, Any]:
    obfuscated = body.copy()

    for field_spec in sensitive_fields:

        _, field_name, log_chars_str = field_spec.split('.')
        full_field_name = f"{model_name}.{field_name}.{log_chars_str}"

        if (
            full_field_name not in sensitive_fields
            or field_name not in obfuscated
        ):
            continue

        value = obfuscated[field_name]
        log_chars = int(log_chars_str)

        obfuscated[field_name] = (
            '*' * 5 + value[-log_chars:] if log_chars > 0 else '*' * 5
        )

    return obfuscated


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

        obfuscated_headers = obfuscate_sensitive_headers(
            headers, SENSITIVE_HEADERS
        )

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
