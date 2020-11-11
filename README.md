# agave
[![test](https://github.com/cuenca-mx/agave/workflows/test/badge.svg)](https://github.com/cuenca-mx/agave/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/cuenca-mx/agave/branch/main/graph/badge.svg)](https://codecov.io/gh/cuenca-mx/agave)
[![PyPI](https://img.shields.io/pypi/v/agave.svg)](https://pypi.org/project/agave/)

Agave is a library that implement rest_api across the use of Blueprints based on Chalice Aws.

this library allow send and receive JSON data to these endpoints to query, modify and create content.

Install agave using pip:

```bash
pip install agave==0.0.2.dev0
```

You can use agave for blueprint like this:
```python

from agave.blueprints.rest_api import RestApiBlueprint

```

agave include helpers for mongoengine, for example:
```python

from agave.models.helpers import (uuid_field, mongo_to_dict, EnumField, updated_at, list_field_to_dict)

```

Correr tests
```bash
make test
```
