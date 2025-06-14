# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup

```bash
# Create virtual environment (using Python 3.13)
make venv

# Install dependencies
make install  # Install main dependencies
make install-test  # Install main and test dependencies
```

### Testing

```bash
# Run all tests
make test  # This will also run linting

# Run specific test
pytest tests/path/to/test_file.py::TestClass::test_method

# Run tests with coverage
pytest --cov=agave
```

### Linting & Formatting

```bash
# Format code
make format  # Runs isort and black

# Lint code
make lint  # Runs flake8, isort --check-only, black --check, mypy
```

### Releasing

```bash
# Create distribution packages
make release  # Runs tests, creates sdist and wheel, uploads to PyPI
```

## Architecture Overview

Agave is a Python library for building REST APIs using a Blueprint pattern with support for both AWS Chalice and FastAPI frameworks. It provides a consistent way to create JSON-based endpoints for querying, modifying, and creating resources.

### Core Components

1. **Blueprint Pattern**
   - `RestApiBlueprint` classes for both Chalice and FastAPI
   - Standardized resource decorators that create CRUD endpoints

2. **Framework Support**
   - `agave.chalice`: Chalice-specific implementation
   - `agave.fastapi`: FastAPI-specific implementation

3. **Async Tasks**
   - SQS-based task processing system in `agave.tasks`
   - Support for retries, error handling, and concurrency control

### Module Structure

- `agave/core/`: Core functionality shared between frameworks
- `agave/chalice/`: AWS Chalice specific implementation
- `agave/fastapi/`: FastAPI specific implementation
- `agave/tasks/`: Async task processing with SQS
- `agave/tools/`: Utilities for AWS services (sync and async)

### Key Design Patterns

1. **Resource Blueprint**
   - Define a class with model, validation, and CRUD methods
   - Apply `@app.resource('/path')` decorator to generate standard endpoints
   - Customize behavior by implementing specific methods (create, update, delete, etc.)

2. **Validation**
   - Uses Pydantic models for request/response validation
   - Automatically handles validation errors and returns appropriate responses

3. **MongoDB Integration**
   - Designed to work with MongoEngine for data persistence
   - Uses `mongoengine_plus.aio.AsyncDocument` for async MongoDB operations in FastAPI
   - Provides standardized query filtering and pagination

4. **Asynchronous Support**
   - FastAPI implementation uses async/await pattern
   - SQS tasks support async processing with concurrency control

## Common Patterns

### Creating a REST API Resource

1. Define a model:
   - For FastAPI: Use `mongoengine_plus.aio.AsyncDocument` for async MongoDB operations
   - For Chalice: Use standard `mongoengine.Document`
2. Create validation models (Pydantic)
3. Define a Resource class with CRUD operations
4. Apply `@app.resource('/path')` decorator

### Working with SQS Tasks

1. Import task decorator: `from agave.tasks.sqs_tasks import task`
2. Define task function with Pydantic model type hints for automatic validation
3. Apply `@task(queue_url=URL, region_name=REGION)` decorator
4. Implement error handling with `raise RetryTask()` pattern

#### SQS Task Pydantic Validation

Tasks automatically validate and parse incoming JSON messages into Pydantic models if type hints are provided:

```python
from pydantic import BaseModel
from agave.tasks.sqs_tasks import task

class User(BaseModel):
    name: str
    age: int

@task(queue_url=QUEUE_URL, region_name='us-east-1')
async def process_user(user: User) -> None:
    # 'user' is already a validated Pydantic model instance
    print(user.name, user.age)
```

### Error Handling

- Use framework-specific error responses
- For SQS tasks, use `RetryTask` exception to trigger retry logic
- All validation errors are automatically handled and return 400 responses