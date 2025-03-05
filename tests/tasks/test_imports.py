import importlib
import sys

import pytest


@pytest.mark.parametrize(
    'module_path,required_types,required_option',
    [
        (
            'agave.tools.asyncio.sqs_client',
            'types_aiobotocore_sqs',
            'asyncio_aws_tools',
        ),
        (
            'agave.tools.sync.sqs_client',
            'types_boto3_sqs',
            'sync_aws_tools',
        ),
    ],
)
def test_tasks_import_error(
    monkeypatch: pytest.MonkeyPatch,
    module_path: str,
    required_types: str,
    required_option: str,
) -> None:
    # Clear modules from sys.modules
    for module in [required_types, module_path]:
        if module in sys.modules:
            del sys.modules[module]

    monkeypatch.setitem(sys.modules, required_types, None)

    with pytest.raises(ImportError) as exc_info:
        importlib.import_module(module_path)

    assert f"You must install agave with [{required_option}] option" in str(
        exc_info.value
    )
    assert f"pip install agave[{required_option}]" in str(exc_info.value)
