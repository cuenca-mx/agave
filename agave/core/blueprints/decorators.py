from typing import Any, Callable, Type


def copy_attributes(resource: Type[Any]):
    """
    Copy every attached property from resource methods definition to the
    real function handler.
    :param resource: Class representing the resource definition
    :return: wrapper function
    """

    def wrapper(func: Callable):
        try:
            original_func = getattr(resource, func.__name__)
        except AttributeError:
            return func

        for key, val in original_func.__dict__.items():
            setattr(func, key, val)

        return func

    return wrapper
