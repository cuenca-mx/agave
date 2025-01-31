import json
import logging
import sys
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from agave.core.utilis.loggers import (
    EXCLUDED_HEADERS,
    SENSITIVE_HEADERS,
    SENSITIVE_REQUEST_MODEL_FIELDS,
    SENSITIVE_RESPONSE_MODEL_FIELDS,
    obfuscate_sensitive_body,
    obfuscate_sensitive_headers,
    parse_body,
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


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:
            request_model = (
                self.body_field.type_.__name__
                if self.body_field
                and hasattr(self.body_field.type_, '__name__')
                else ''
            )
            response_model = (
                self.response_model.__name__
                if hasattr(self.response_model, '__name__')
                else ''
            )

            request_body = await request.body()
            request_json_body = parse_body(request_body)
            response: Response = await original_route_handler(request)
            response_body = (
                parse_body(response.body)
                if hasattr(response, 'body')
                else None
            )

            request_info = {
                "method": request.method,
                "url": str(request.url),
                "query_params": request.query_params,
                "headers": obfuscate_sensitive_headers(dict(request.headers)),
                "body": (
                    obfuscate_sensitive_body(
                        request_json_body,
                        request_model,
                        SENSITIVE_REQUEST_MODEL_FIELDS,
                    )
                    if request_json_body
                    else None
                ),
            }

            response_info = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": (
                    obfuscate_sensitive_body(
                        response_body,
                        response_model,
                        SENSITIVE_RESPONSE_MODEL_FIELDS,
                    )
                    if response_body and isinstance(response_body, dict)
                    else None
                ),
            }

            logger.info(
                "Info: %s",
                json.dumps(
                    {"request": request_info, "response": response_info},
                    default=str,
                ),
            )

            return response

        return logging_route_handler
