import json
import logging
import sys
from typing import Callable

from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from agave.core.exc import AgaveError
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
    @property
    def request_model_name(self) -> str:
        return getattr(getattr(self.body_field, 'type_', None), '__name__', '')

    @property
    def response_model_name(self) -> str:
        return getattr(self.response_model, '__name__', '')

    def _generate_request_info(
        self, request: Request, request_body: bytes
    ) -> dict:
        request_json_body = parse_body(request_body)
        return {
            'method': request.method,
            'url': str(request.url),
            'query_params': dict(request.query_params),
            'headers': obfuscate_sensitive_headers(dict(request.headers)),
            'body': (
                obfuscate_sensitive_body(
                    request_json_body,
                    self.request_model_name,
                    SENSITIVE_REQUEST_MODEL_FIELDS,
                )
                if request_json_body
                else None
            ),
        }

    def _generate_response_info(self, response: Response) -> dict:
        response_body = (
            parse_body(response.body) if hasattr(response, 'body') else None
        )
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': (
                obfuscate_sensitive_body(
                    response_body,
                    self.response_model_name,
                    SENSITIVE_RESPONSE_MODEL_FIELDS,
                )
                if response_body and isinstance(response_body, dict)
                else None
            ),
        }

    def _get_error_details(self, exc: Exception) -> tuple[int, str]:
        if isinstance(exc, HTTPException):
            return exc.status_code, str(exc.detail)
        if isinstance(exc, RequestValidationError):
            return 422, str(exc.errors())
        if isinstance(exc, AgaveError):
            return exc.status_code, str(exc.error)
        return 500, 'Internal Server Error'

    def _log_request_response(
        self, request_info: dict, response_info: dict
    ) -> None:
        logger.info(
            'Info: %s',
            json.dumps(
                {'request': request_info, 'response': response_info},
                default=str,
            ),
        )

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:
            request_body = await request.body()
            request_info = self._generate_request_info(request, request_body)
            response: Response

            try:
                response = await original_route_handler(request)
                response_info = self._generate_response_info(response)
            except Exception as exc:
                status_code, detail = self._get_error_details(exc)

                response_info = {
                    'status_code': status_code,
                    'detail': detail,
                }

                response = JSONResponse(
                    content={'detail': detail},
                    status_code=status_code,
                )

            self._log_request_response(request_info, response_info)
            return response

        return logging_route_handler
