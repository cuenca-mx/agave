# agave
[![test](https://github.com/cuenca-mx/agave/workflows/test/badge.svg)](https://github.com/cuenca-mx/agave/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/cuenca-mx/agave/branch/main/graph/badge.svg)](https://codecov.io/gh/cuenca-mx/agave)
[![PyPI](https://img.shields.io/pypi/v/agave.svg)](https://pypi.org/project/agave/)

Agave is a library for implementing REST APIs using Blueprints, designed to work with Chalice AWS or FastAPI. It provides a convenient way to send and receive JSON data through endpoints for querying, modifying, and creating content.

## Installation


### For Chalice

To use Agave with Chalice, install it using pip:

```bash
pip install agave[chalice]
```

You can then create a REST API blueprint as follows:
```python
from agave.chalice import RestApiBlueprint
```

### For FastAPI
To use Agave with FastAPI, install it with the [fastapi] option:

```bash
pip install agave[fastapi]
```

Create a REST API blueprint for FastAPI like this:

```python
from agave.fastapi import RestApiBlueprint
```

### Tasks for FastAPI

If you want to use tasks with FastAPI, install Agave with the [fastapi,tasks] option:
```bash
pip install agave[fastapi,tasks]
```

Then, you can define tasks like this:
```python
from agave.tasks.sqs_tasks import task
```

## Running Tests

Run the tests using the following command:

```bash
make test
```
