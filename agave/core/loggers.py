from typing import (
    Any,
    Callable,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from cuenca_validations.types.general import LogConfig
from cuenca_validations.types.helpers import get_log_config
from pydantic import BaseModel

HEADERS_LOG_CONFIG = {
    'authorization': LogConfig(masked=True),
    'x-cuenca-token': LogConfig(masked=True, unmasked_chars_length=4),
    'x-cuenca-loginid': LogConfig(masked=True, unmasked_chars_length=4),
    'x-cuenca-logintoken': LogConfig(masked=True, unmasked_chars_length=4),
    'x-cuenca-sessionid': LogConfig(masked=True, unmasked_chars_length=4),
    'connection': LogConfig(excluded=True),
    'content-length': LogConfig(excluded=True),
}


def obfuscate_sensitive_data(
    body: dict[str, Any],
    sensitive_fields: dict[str, LogConfig],
) -> dict[str, Any]:

    ofuscated_body = body.copy()
    for field_name, log_config in sensitive_fields.items():
        if field_name not in ofuscated_body:
            continue

        if log_config.excluded:
            del ofuscated_body[field_name]
        else:
            value = ofuscated_body[field_name]
            log_chars = log_config.unmasked_chars_length
            ofuscated_body[field_name] = (
                '*****' + value[-log_chars:] if log_chars > 0 else '*****'
            )

    return ofuscated_body


def get_request_model(
    function: Callable[..., Any],
) -> Optional[list[Type[BaseModel]]]:
    """
    Extracts the first parameter from a function that is a
    BaseModel or Union of BaseModels.
    """
    type_hints = get_type_hints(function)
    type_hints.pop('return', None)

    extracted_types: list[type] = []
    valid_types: list[type] = []

    for param_type in type_hints.values():
        origin = get_origin(param_type)
        if origin is Union:
            extracted_types.extend(get_args(param_type))
        else:
            extracted_types.append(param_type)

    for model_type in extracted_types:
        try:
            if issubclass(model_type, BaseModel):
                valid_types.append(model_type)
        except TypeError:
            continue

    return valid_types or None


def get_response_model(
    function: Callable[..., Any]
) -> Optional[Type[BaseModel]]:
    """
    Extracts the response model from the function's return type
    if it is a Pydantic BaseModel.
    """
    hints = get_type_hints(function)
    return_annotation = hints.get('return', None)

    if return_annotation is None:
        return None

    try:
        if issubclass(return_annotation, BaseModel):
            return return_annotation
        else:
            return None
    except TypeError:
        return None


def get_sensitive_fields(
    models: Optional[Union[list[type[BaseModel]], type[BaseModel]]],
) -> dict[str, Any]:
    """
    Analyzes a list of Pydantic models and returns
    a set of field names marked as sensitive in their metadata.
    """
    sensitive_fields: dict[str, Any] = {}

    if models is None or models is Any:
        return sensitive_fields

    if not isinstance(models, list):
        models = [models]

    for m in models:
        for field_name, field in m.model_fields.items():
            log_config = get_log_config(field)
            if not log_config:
                continue
            if log_config.masked or log_config.excluded:
                sensitive_fields[field_name] = log_config

    return sensitive_fields
