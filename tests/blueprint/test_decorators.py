from functools import wraps

from agave.blueprints.decorators import copy_attributes


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
    retrieve = copy_attributes(TestResource)(retrieve)
    assert hasattr(retrieve, 'i_am_test')
