import importlib
import sys

import pytest


def test_tasks_import_error(monkeypatch):
    for module in ['types_aiobotocore_sqs', 'agave.tasks.sqs_client']:
        if module in sys.modules:
            del sys.modules[module]

    monkeypatch.setitem(sys.modules, 'types_aiobotocore_sqs', None)

    with pytest.raises(ImportError) as exc_info:
        importlib.import_module('agave.tasks.sqs_client')

    assert "You must install agave with [fastapi, tasks] option" in str(
        exc_info.value
    )
    assert "pip install agave[fastapi, tasks]" in str(exc_info.value)
