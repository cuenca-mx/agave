import json
import logging
import sys
from typing import Any, Callable, Union

from cuenca_validations.errors import CuencaError
from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from agave.core.exc import AgaveError
from agave.core.loggers import (
    HEADERS_LOG_CONFIG,
    obfuscate_sensitive_data,
    parse_body,
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class LoggingRoute(APIRoute):
    def _get_error_details(self, exc: Exception) -> tuple[int, str]:
        if isinstance(exc, HTTPException):
            return exc.status_code, str(exc.detail)
        if isinstance(exc, RequestValidationError):
            return 422, str(exc.errors())
        if isinstance(exc, AgaveError):
            return exc.status_code, str(exc.error)
        if isinstance(exc, CuencaError):
            return exc.status_code, str(exc)
        return 500, 'Internal Server Error'

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:

            request_handler = request.scope['route_handler']
            request_fields_config = getattr(
                request_handler.endpoint, 'request_log_config_fields', None
            )
            response_fields_config = getattr(
                request_handler.endpoint, 'response_log_config_fields', None
            )

            request_body = await request.body()
            request_json_body = parse_body(request_body)

            log_data: dict[
                str, dict[str, Union[int, str, None, dict[str, Any]]]
            ] = {}

            log_data = {
                'request': {
                    'method': request.method,
                    'url': str(request.url),
                    'query_params': dict(request.query_params),
                    'headers': obfuscate_sensitive_data(
                        dict(request.headers),
                        HEADERS_LOG_CONFIG,
                    ),
                    'body': (
                        obfuscate_sensitive_data(
                            request_json_body,
                            request_fields_config,
                        )
                        if request_json_body
                        else None
                    ),
                }
            }

            response: Response

            try:
                response = await original_route_handler(request)
            except Exception as exc:
                status_code, detail = self._get_error_details(exc)

                log_data['response'] = {
                    'status_code': status_code,
                    'detail': detail,
                }
                raise
            else:
                response_body = (
                    parse_body(response.body)
                    if hasattr(response, 'body')
                    else None
                )

                log_data['response'] = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': (
                        obfuscate_sensitive_data(
                            response_body,
                            response_fields_config,
                        )
                        if response_body and isinstance(response_body, dict)
                        else None
                    ),
                }

            finally:
                logger.info(
                    'Info: %s',
                    json.dumps(
                        log_data,
                        default=str,
                    ),
                )

            return response

        return logging_route_handler
