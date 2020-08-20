from typing import Callable

from chalice import Blueprint, IAMAuthorizer

IAM_AUTH = IAMAuthorizer()


class AuthedBlueprint(Blueprint):
    def route(self, path: str, **kwargs):
        """
        Chose the authorizer for AWS API Gateway endpoints
        AUTHORIZER is defined in environment variables of chalice stage
        Note: Authorizer is set on deployment and cannot be changed at runtime
        """

        def decorator(user_handler: Callable):
            handler = user_handler

            self._register_handler(
                'route',
                user_handler.__name__,
                handler,
                handler,
                dict(path=path, kwargs=kwargs),
            )

        return decorator
