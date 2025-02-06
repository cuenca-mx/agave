import json
import logging
from json import JSONDecodeError
from typing import Any, Callable

from cuenca_validations.errors import CuencaError
from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from ...core.exc import AgaveError
from ...core.loggers import HEADERS_LOG_CONFIG, obfuscate_sensitive_data

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_status_code_exception(exc: Exception) -> int:
    if isinstance(exc, HTTPException):
        return exc.status_code
    if isinstance(exc, RequestValidationError):
        return 422
    if isinstance(exc, AgaveError):
        return exc.status_code
    if isinstance(exc, CuencaError):
        return exc.status_code
    return 500


class LoggingRoute(APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:

            req_handler = request.scope['route_handler']

            try:
                ofuscated_request_body = obfuscate_sensitive_data(
                    await request.json(),
                    req_handler.endpoint.request_log_config_fields,
                )
            except AttributeError:
                ofuscated_request_body = await request.json()
            except JSONDecodeError:
                ofuscated_request_body = None

            log_data: dict[str, Any] = {
                'request': {
                    'method': request.method,
                    'url': str(request.url),
                    'query_params': request.query_params,
                    'headers': obfuscate_sensitive_data(
                        dict(request.headers),
                        HEADERS_LOG_CONFIG,
                    ),
                    'body': ofuscated_request_body,
                }
            }

            response: Response

            try:
                response = await original_route_handler(request)
            except Exception as exc:
                log_data['response'] = {
                    'status_code': get_status_code_exception(exc)
                }
                raise
            else:

                if hasattr(response, 'body'):
                    try:
                        ofuscated_response_body = obfuscate_sensitive_data(
                            json.loads(response.body),
                            req_handler.endpoint.response_log_config_fields,
                        )
                    except AttributeError:
                        ofuscated_response_body = json.loads(response.body)
                else:
                    ofuscated_response_body = None

                log_data['response'] = {
                    'status_code': response.status_code,
                    'headers': obfuscate_sensitive_data(
                        dict(response.headers),
                        HEADERS_LOG_CONFIG,
                    ),
                    'body': ofuscated_response_body,
                }

            finally:
                logger.info(json.dumps(log_data, default=str))

            return response

        return logging_route_handler
