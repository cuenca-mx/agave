from collections import defaultdict
from functools import wraps
from typing import Callable, Dict, List, Optional

from chalice import Blueprint


class AuthedBlueprint(Blueprint):
    """
    This dummy class is an example of Authentication/Authorization blueprint.

    """
    def route(
        self, path: str, authorizations: Optional[List[str]] = None, **kwargs
    ):
        def decorator(user_handler: Callable):
            @wraps(user_handler)
            def authed_handler(*args, **kwargs):
                self.current_request.user_id = '123445'
                return user_handler(*args, **kwargs)

            self._register_handler(
                'route',
                user_handler.__name__,
                authed_handler,
                authed_handler,
                dict(path=path, kwargs=kwargs),
            )

        return decorator

    def user_id_filter_required(self):
        """
        This method is required to be implemented with your own business logic.
        You have to determine when `user_id` filter is required. For example:

        `Account`s created by by one user should not be queryable/retrievable
        by others user.

        For testing purpose we return `False` as default behavior.
        But if we need to change to `True` in tests we could monkey patch it
        when needed.

        :return:
        """
        return False
