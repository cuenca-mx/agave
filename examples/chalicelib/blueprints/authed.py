from functools import wraps
from typing import Callable

from chalice import Blueprint

from ...config import TEST_DEFAULT_PLATFORM_ID, TEST_DEFAULT_USER_ID


class AuthedBlueprint(Blueprint):
    """
    This dummy class is an example of Authentication/Authorization blueprint.

    """

    def route(self, path: str, **kwargs):
        """
        Builds route decorator with custom authentication.
        It is only a function wrapper for `Blueprint._register_handler` methods

        For this example we do not validate any credentials but
        your authentication logic could be implemented here.

        :param path:
        :param kwargs:
        :return:
        """

        def decorator(user_handler: Callable):
            @wraps(user_handler)
            def authed_handler(*args, **kwargs):
                # your authentication logic goes here
                # before execute `user_handler` function.
                self.current_request.user_id = TEST_DEFAULT_USER_ID
                self.current_request.platform_id = TEST_DEFAULT_PLATFORM_ID
                return user_handler(*args, **kwargs)

            self._register_handler(  # type: ignore
                'route',
                user_handler.__name__,
                authed_handler,
                authed_handler,
                dict(path=path, kwargs=kwargs),
            )

        return decorator

    def user_id_filter_required(self):
        """
        It overrides `RestApiBlueprint.user_id_filter_required()` method.

        This method is required to be implemented with your own business logic.
        You have to determine when `user_id` filter is required. For example:

        - `Account`s created by one user should not be queryable/retrievable
        by others users. In that case return `True`.

        - "Admin" users are allowed to query/retrieve any `Account` from any
        user. In that case return `False`.

        For testing purpose we return `False` as default behavior.
        But if we need to change it to `True` in tests we could monkey patch it
        when needed.

        :return:
        """
        return False

    def platform_id_filter_required(self):
        """
        It overrides `RestApiBlueprint.platform_id_filter_required()` method.
        :return:
        """
        return False
