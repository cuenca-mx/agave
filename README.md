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

### SQS task support (only FastApi based app):
```bash
pip install agave[fastapi,tasks]
```

## Models

### AsyncDocument for FastAPI

When using FastAPI, models should inherit from `mongoengine_plus.aio.AsyncDocument` to enable async MongoDB operations:

```python
from mongoengine import StringField, DateTimeField
from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import BaseModel

class Account(BaseModel, AsyncDocument):
    name = StringField(required=True)
    user_id = StringField(required=True)
    # ...other fields
    
    # Use async methods:
    # await account.async_save()
    # await Account.objects.async_get(id=id)
    # await Account.objects.filter(...).async_to_list()
```

### Document for Chalice

For Chalice, use standard MongoEngine Document:

```python
from mongoengine import Document, StringField, DateTimeField

class Account(Document):
    name = StringField(required=True)
    user_id = StringField(required=True)
    # ...other fields
    
    # Use sync methods:
    # account.save()
    # Account.objects.get(id=id)
```

## Usage

### Chalice Example

Create a REST API blueprint as follows:
```python
import datetime as dt
from chalice import Response
from agave.chalice import RestApiBlueprint

app = RestApiBlueprint()

# The @app.resource decorator automatically creates these endpoints:
# - GET /accounts             => Query with filters
# - GET /accounts/{id}        => Get account by ID
# 
# Additional endpoints are created only if you define the corresponding methods:
# - POST /accounts            => created if 'create' method is defined
# - PATCH /accounts/{id}      => created if 'update' method is defined
# - DELETE /accounts/{id}     => created if 'delete' method is defined
@app.resource('/accounts')
class Account:
    model = AccountModel
    query_validator = AccountQuery
    update_validator = AccountUpdateRequest
    get_query_filter = generic_query

    # Optional: Define create method to enable POST endpoint
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

    # Optional: Define update method to enable PATCH endpoint
    @staticmethod
    def update(
        account: AccountModel, request: AccountUpdateRequest
    ) -> Response:
        account.name = request.name
        account.save()
        return Response(account.to_dict(), status_code=200)

    # Optional: Define delete method to enable DELETE endpoint
    @staticmethod
    def delete(account: AccountModel) -> Response:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        account.save()
        return Response(account.to_dict(), status_code=200)
```

### FastAPI Example

```python
import datetime as dt
from fastapi import Request
from fastapi.responses import JSONResponse as Response
from agave.fastapi import RestApiBlueprint

app = RestApiBlueprint()

# The @app.resource decorator automatically creates these endpoints:
# - GET /accounts             => Query with filters
# - GET /accounts/{id}        => Get account by ID
# 
# Additional endpoints are created only if you define the corresponding methods:
# - POST /accounts            => created if 'create' method is defined
# - PATCH /accounts/{id}      => created if 'update' method is defined
# - DELETE /accounts/{id}     => created if 'delete' method is defined
@app.resource('/accounts')
class Account:
    model = AccountModel  # AsyncDocument model
    query_validator = AccountQuery
    update_validator = AccountUpdateRequest
    get_query_filter = generic_query
    response_model = AccountResponse  # FastAPI specific

    # Optional: Define create method to enable POST endpoint
    @staticmethod
    async def create(request: AccountRequest) -> Response:
        """This is the description for OpenAPI documentation"""
        account = AccountModel(
            name=request.name,
            user_id=app.current_user_id,
            platform_id=app.current_platform_id,
        )
        await account.async_save()
        return Response(content=account.to_dict(), status_code=201)

    # Optional: Define update method to enable PATCH endpoint
    @staticmethod
    async def update(
        account: AccountModel,
        request: AccountUpdateRequest,
    ) -> Response:
        account.name = request.name
        await account.async_save()
        return Response(content=account.to_dict(), status_code=200)

    # Optional: Define delete method to enable DELETE endpoint
    @staticmethod
    async def delete(account: AccountModel, _: Request) -> Response:
        account.deactivated_at = dt.datetime.utcnow().replace(microsecond=0)
        await account.async_save()
        return Response(content=account.to_dict(), status_code=200)
```

### Async Tasks

Agave's SQS tasks support Pydantic model validation. When you send a JSON message to an SQS queue, the task will automatically parse and convert it to the specified Pydantic model:

```python
from pydantic import BaseModel
from agave.tasks.sqs_tasks import task

# Define Pydantic model for request validation
class UserData(BaseModel):
    name: str
    age: int
    email: str

QUEUE_URL = 'https://sqs.region.amazonaws.com/account/queue'
AWS_DEFAULT_REGION = 'us-east-1'

# Task with Pydantic model type hint
@task(
    queue_url=QUEUE_URL,
    region_name=AWS_DEFAULT_REGION,
    visibility_timeout=30,
    max_retries=10,
)
async def process_user(user: UserData):
    # user is already a validated UserData instance, not a dict
    print(f"Processing user {user.name} with email {user.email}")
    # Your processing logic here
    return {"success": True, "user_name": user.name}
```

Use `RetryTask` exception to implement retry logic:

```python
from agave.core.exc import RetryTask
from agave.tasks.sqs_tasks import task

@task(queue_url=QUEUE_URL, region_name=AWS_DEFAULT_REGION, max_retries=3)
async def process_with_retry(data: dict):
    try:
        # Your processing logic
        result = await some_operation(data)
    except TemporaryError:
        # Will retry automatically
        raise RetryTask
    
    return result
```

## Running Tests

Run the tests using the following command:

```bash
make test
```