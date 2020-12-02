from inspect import signature
from typing import Any, Callable, Dict, Tuple, Type

from chalice import BadRequestError
from cuenca_validations.types import QueryParams
from cuenca_validations.typing import DictStrAny
from pydantic import ValidationError


def get_params_annotations(method: Callable) -> Dict[str, Type]:
    """
    gets param annotations from method/function signature.
    example:

    if you have

    def query(query_params: QueryRequest) -> Any:
        ...

    then you can do:

    result = get_params_annotations(query)
    assert result == dict(query_params=QueryRequest)

    """
    sig = signature(method)
    annotations_dict = {
        key: param.annotation for key, param in sig.parameters.items()
    }
    return annotations_dict


def validate_request(
    validator: Type[QueryParams], data: DictStrAny
) -> QueryParams:
    try:
        request = validator(**data)
    except ValidationError as exc:
        raise BadRequestError(exc.json())
    return request


def transform_request(
    handler: Callable, validator_name: str, data: DictStrAny
) -> QueryParams:
    """
    transform `data` dictionary into a validator associated
    to `validator_name` param.

    `validator_name` should exist in the function signature.

    Example:

    @app.resource('/my_resource')
    class MyResource:

      def query(query_param: QueryRequest):
        ...


     request = dict(user_id='US123', ...)

     # then you can transform `request` into `QueryRequest`
     # if request values are valid it returns `QueryRequest` object
     # else it raises BadRequestError

     query_params = transform_request(MyResource.query, 'query_param', request)
    """
    annotations = get_params_annotations(handler)
    validator = annotations[validator_name]
    return validate_request(validator, data)


def response(result: Any, status_code: int = 200) -> Tuple[Any, int]:
    if type(result) is tuple:
        return result
    else:
        return result, status_code


def default_formatter(instance: Any) -> Dict:
    """
    Transforms `instance` object in a dict.

    It assumes that `instance` class hass `to_dict` method. But if your class
    does not implement `to_dict` you can create a custom formatter function
    or class so you can validate or implement specific formatting logic.
    :param instance:
    :return:
    """
    return instance.to_dict()
