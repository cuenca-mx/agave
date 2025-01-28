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

SENSITIVE_RESPONSE_MODEL_FIELDS: list[str] = []
SENSITIVE_REQUEST_MODEL_FIELDS: list[str] = []


def obfuscate_sensitive_headers(
    headers: dict[str, Any], sensitive_headers: list[str]
) -> dict[str, Any]:
    result = headers.copy()
    for header in sensitive_headers:
        if header.lower() in result:
            value = result[header.lower()]
            if len(value) > 4:
                result[header.lower()] = '*' * 5 + value[-4:]
    return result


def obfuscate_sensitive_body(
    body: dict[str, Any],
    model_name: str,
    sensitive_fields: list[str],
) -> dict[str, Any]:
    result = body.copy()
    for long_name_field in sensitive_fields:
        log_chars = int(long_name_field.split('.')[-1])
        field = long_name_field.split('.')[1]
        real_name_field = f"{model_name}.{field}.{log_chars}"
        if real_name_field in sensitive_fields and field in result:
            value = result[field]
            if log_chars > 0:
                result[field] = '*' * 5 + value[-log_chars:]
            else:
                result[field] = '*' * 5
    return result


def parse_body(body: bytes) -> Union[dict, None]:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


class AgaveRequestLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = dict(request.headers)

        try:

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
            response_model = ""
            request_model = ""
            if isinstance(route, APIRoute) and hasattr(
                route.response_model, "__name__"
            ):  # pragma: no cover
                response_model = route.response_model.__name__
                for dep in route.dependant.body_params:
                    if isinstance(dep.type_, type) and issubclass(
                        dep.type_, BaseModel
                    ):  # pragma: no cover
                        request_model = dep.type_.__name__

            body_decoded = parse_body(body)
            obfuscated_request_body = None
            if body_decoded:
                obfuscated_request_body = obfuscate_sensitive_body(
                    body_decoded, request_model, SENSITIVE_REQUEST_MODEL_FIELDS
                )
            obfuscated_headers = obfuscate_sensitive_headers(
                headers, SENSITIVE_HEADERS
            )

            request_info = {
                "method": request.method,
                "url": str(request.url),
                "headers": obfuscated_headers,
                "body": obfuscated_request_body,
            }

            logger.info(
                f"Request Info: {json.dumps(request_info, default=str)}"
            )

            parsed_body = parse_body(response_body)
            obfuscated_response_body = None
            if parsed_body and isinstance(parsed_body, dict):
                obfuscated_response_body = obfuscate_sensitive_body(
                    parsed_body,
                    response_model,
                    SENSITIVE_RESPONSE_MODEL_FIELDS,
                )

            response_info = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": obfuscated_response_body,
            }

            logger.info(
                f"Response Info: {json.dumps(response_info, default=str)}"
            )

            return new_response

        except Exception as e:
            logger.error(f"Error in FastAgaveRequestLogger: {str(e)}")
            raise
