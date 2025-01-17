import importlib
import sys

import pytest


def test_chalice_import_error(monkeypatch):
    for module in ['chalice', 'agave.chalice.rest_api']:
        if module in sys.modules:
            del sys.modules[module]

    monkeypatch.setitem(sys.modules, 'chalice', None)

    with pytest.raises(ImportError) as exc_info:
        importlib.import_module('agave.chalice.rest_api')

    assert "You must install agave with [chalice] option" in str(
        exc_info.value
    )
    assert "pip install agave[chalice]" in str(exc_info.value)
