from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response
from starlette_context import _request_scope_context_storage
from starlette_context.middleware import ContextMiddleware

from ..config import TEST_DEFAULT_PLATFORM_ID, TEST_DEFAULT_USER_ID


class AuthedMiddleware(ContextMiddleware):
    def __init__(
        self, app, plugins=None, default_error_response=None, *args, **kwargs
    ):
        super().__init__(
            app=app,
            plugins=plugins,
            default_error_response=default_error_response,
            *args,
            **kwargs,
        )

    def required_user_id(self) -> bool:
        """
        Example method so we can easily mock it in tests environment
        :return:
        """
        return False

    def required_platform_id(self) -> bool:
        """
        Example method so we can easily mock it in tests environment
        :return:
        """
        return False

    async def authenticate(self):
        self.token = _request_scope_context_storage.set(
            dict(
                user_id=TEST_DEFAULT_USER_ID,
                platform_id=TEST_DEFAULT_PLATFORM_ID,
            )
        )

    async def authorize(self):
        context = _request_scope_context_storage.get()
        context['user_id_filter_required'] = self.required_user_id()
        context['platform_id_filter_required'] = self.required_platform_id()
        self.token = _request_scope_context_storage.set(context)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            # Authentication and authorization goes here!
            await self.authenticate()
            await self.authorize()
            response = await call_next(request)
            for plugin in self.plugins:
                await plugin.enrich_response(response)

        finally:
            _request_scope_context_storage.reset(self.token)

        return response
