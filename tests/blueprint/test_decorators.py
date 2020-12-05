from functools import wraps

from agave.blueprints.decorators import copy_properties_from


def i_am_test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.i_am_test = True
    return wrapper


class TestResource:
    @i_am_test
    def retrieve(self) -> str:
        return 'hello'


def test_copy_properties_from() -> None:
    def retrieve():
        ...

    assert not hasattr(retrieve, 'i_am_test')
    retrieve = copy_properties_from(TestResource)(retrieve)
    assert hasattr(retrieve, 'i_am_test')
