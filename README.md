# agave
[![test](https://github.com/cuenca-mx/agave/workflows/test/badge.svg)](https://github.com/cuenca-mx/agave/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/cuenca-mx/agave/branch/main/graph/badge.svg)](https://codecov.io/gh/cuenca-mx/agave)
[![PyPI](https://img.shields.io/pypi/v/agave.svg)](https://pypi.org/project/agave/)

Agave is a library for building REST APIs using a Blueprint pattern, with support for both AWS Chalice and FastAPI frameworks. It simplifies the creation of JSON-based endpoints for querying, modifying, and creating resources.

## Installation

Choose the installation option based on your framework:

### Chalice Installation

```bash
pip install agave[chalice]
```

### FastAPI Installation

```bash
pip install agave[fastapi]
```

### SQS task support:
```bash
pip install agave[fastapi,tasks]
```

## Usage

### Chalice Example

You can then create a REST API blueprint as follows:
```python
from agave.chalice import RestApiBlueprint

app = RestApiBlueprint()

@app.resource('/accounts')
class Account:
    model = AccountModel
    query_validator = AccountQuery
    update_validator = AccountUpdateRequest
    get_query_filter = generic_query

    @staticmethod
    @app.validate(AccountRequest)
    def create(request: AccountRequest) -> Response:
        account = AccountModel(
            name=request.name,
            user_id=app.current_user_id,
            platform_id=app.current_platform_id,
        )
        account.save()
        return Response(account.to_dict(), status_code=201)

    @staticmethod
    def update(
        account: AccountModel, request: AccountUpdateRequest
    ) -> Response:
        account.name = request.name
        account.save()
        return Response(account.to_dict(), status_code=200)

    @staticmethod
    def delete(account: AccountModel) -> Response:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        account.save()
        return Response(account.to_dict(), status_code=200)
```

### FastAPI Example

```python
from agave.fastapi import RestApiBlueprint

app = RestApiBlueprint()

@app.resource('/accounts')
class Account:
    model = AccountModel
    query_validator = AccountQuery
    update_validator = AccountUpdateRequest
    get_query_filter = generic_query
    response_model = AccountResponse

    @staticmethod
    async def create(request: AccountRequest) -> Response:
        """This is the description for openapi"""
        account = AccountModel(
            name=request.name,
            user_id=app.current_user_id,
            platform_id=app.current_platform_id,
        )
        await account.async_save()
        return Response(content=account.to_dict(), status_code=201)

    @staticmethod
    async def update(
        account: AccountModel,
        request: AccountUpdateRequest,
    ) -> Response:
        account.name = request.name
        await account.async_save()
        return Response(content=account.to_dict(), status_code=200)

    @staticmethod
    async def delete(account: AccountModel, _: Request) -> Response:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        await account.async_save()
        return Response(content=account.to_dict(), status_code=200)
```

### Async Tasks

```python
from agave.tasks.sqs_tasks import task

QUEUE_URL = 'https://sqs.region.amazonaws.com/account/queue'
AWS_DEFAULT_REGION = 'us-east-1'
@task(
    queue_url=QUEUE_URL,
    region_name=AWS_DEFAULT_REGION,
    visibility_timeout=30,
    max_retries=10,
)
async def process_data(data: dict):
    # Async task processing
    return {'processed': data}
```

## Running Tests

Run the tests using the following command:

```bash
make test
```
