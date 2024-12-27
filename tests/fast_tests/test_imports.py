import importlib
import sys

import pytest


def test_fast_import_error(monkeypatch):
    for module in ['fastapi', 'agave.fastapi_support.rest_api']:
        if module in sys.modules:
            del sys.modules[module]

    monkeypatch.setitem(sys.modules, 'fastapi', None)

    with pytest.raises(ImportError) as exc_info:
        importlib.import_module('agave.fastapi_support.rest_api')

    assert "You must install agave with [fastapi_support] option" in str(
        exc_info.value
    )
    assert "pip install agave[fastapi_support]" in str(exc_info.value)
