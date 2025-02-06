from inspect import Parameter, Signature, signature
from typing import Any, Optional, Type, Union

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


def get_request_model(method: Any) -> Optional[Type[BaseModel]]:
    """
    Analyzes a method's parameters to extract the first parameter
    that inherits from pydantic.BaseModel.
    If none inherits from pydantic.BaseModel, returns None.
    """
    create_signature: Signature = signature(method)
    parameters = create_signature.parameters.values()

    try:
        return next(
            param.annotation
            for param in parameters
            if param.annotation is not Parameter.empty
            and issubclass(param.annotation, BaseModel)
        )
    except StopIteration:
        return None


def get_sensitive_fields(
    model: Optional[type[Union[BaseModel, Any]]]
) -> dict[str, Any]:
    """
    Analyzes a Pydantic model and returns a set of field names
    marked as sensitive in their metadata.
    """
    sensitive_fields: dict[str, Any] = {}

    if (
        not model
        or model is Any
        or not isinstance(model, type)
        or not issubclass(model, BaseModel)
    ):
        return {}

    for field_name, field in model.model_fields.items():
        log_config = get_log_config(field)

        if not log_config:
            continue

        if log_config.masked or log_config.excluded:
            sensitive_fields[field_name] = log_config

    return sensitive_fields
