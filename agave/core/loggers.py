import json
from inspect import Signature, signature
from typing import Any, Optional, Type, Union

from cuenca_validations.types.general import LogConfig
from cuenca_validations.types.helpers import get_log_config
from pydantic import BaseModel

HEADERS_LOG_CONFIG = {
    'authorization': LogConfig(masked=True, unmasked_chars_length=4),
    'x-cuenca-token': LogConfig(masked=True, unmasked_chars_length=4),
    'x-cuenca-loginid': LogConfig(masked=True, unmasked_chars_length=4),
    'x-cuenca-logintoken': LogConfig(masked=True, unmasked_chars_length=4),
    'x-cuenca-sessionid': LogConfig(masked=True, unmasked_chars_length=4),
    'connection': LogConfig(excluded=True),
}


def obfuscate_sensitive_data(
    body: dict[str, Any],
    sensitive_fields: Union[dict[str, LogConfig], None],
) -> dict[str, Any]:
    obfuscated_body = body.copy()

    if not sensitive_fields:
        return obfuscated_body

    for field_name, log_config in sensitive_fields.items():
        if field_name not in obfuscated_body:
            continue

        if log_config.excluded:
            del obfuscated_body[field_name]
        else:
            value = obfuscated_body[field_name]
            log_chars = log_config.unmasked_chars_length
            obfuscated_body[field_name] = (
                '*****' + value[-log_chars:] if log_chars > 0 else '*****'
            )

    return obfuscated_body


def get_request_model(method: Any) -> Optional[Type[BaseModel]]:
    """
    Analyzes a method's parameters to extract request model.
    """
    create_signature: Signature = signature(method)
    parameters = create_signature.parameters.values()

    for param in parameters:
        if param.name == 'request':
            return (
                param.annotation
                if param.annotation is not param.empty
                else None
            )

    return None


def get_sensitive_fields(
    model: Optional[type[Union[BaseModel, Any]]]
) -> dict[str, Any]:
    """
    Analyzes a Pydantic model and returns a set of field names
    marked as sensitive in their metadata.
    """
    sensitive_fields: dict[str, Any] = {}

    if not model or not issubclass(model, BaseModel):
        return sensitive_fields

    for field_name, field in model.model_fields.items():
        log_config = get_log_config(field)

        if not log_config:
            continue

        if log_config.masked or log_config.excluded:
            sensitive_fields[field_name] = log_config

    return sensitive_fields


def parse_body(body: bytes) -> Union[dict, None]:
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None
