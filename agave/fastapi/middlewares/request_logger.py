import json
import logging
import sys
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
    """
    Obfuscates the values of sensitive headers.
    """
    result = headers.copy()
    for header in sensitive_headers:
        if header.lower() in result:
            value = result[header.lower()]
            if len(value) > 4:
                result[header.lower()] = '*' * 5 + value[-4:]
    return result


def obfuscate_sensitive_body(
    body: dict[str, Any],
    sensitive_fields: list[str],
    prefix_length: int = 5,
) -> dict[str, Any]:
    result = body.copy()
    for field in sensitive_fields:
        if field in result:
            value = result[field]
            if isinstance(value, str) and len(value) > 4:
                result[field] = '*' * prefix_length + value[-4:]
    return result


def parse_body(body: bytes) -> dict | None:
    """
    Attempts to decode the request body.
    """
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None


class FastAgaveRequestLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = dict(request.headers)

        try:

            body = await request.body()
            body_decoded = parse_body(body)
            obfuscated_request_body = None
            if body_decoded:
                obfuscated_request_body = obfuscate_sensitive_body(
                    body_decoded, SENSITIVE_REQUEST_MODEL_FIELDS
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

            parsed_body = parse_body(response_body)
            obfuscated_response_body = None
            if parsed_body and isinstance(parsed_body, dict):
                obfuscated_response_body = obfuscate_sensitive_body(
                    parsed_body, SENSITIVE_RESPONSE_MODEL_FIELDS
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
