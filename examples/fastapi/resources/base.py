from typing import NoReturn

from cuenca_validations.errors import NoPasswordFoundError, WrongCredsError

from agave.core.exc import UnauthorizedError
from agave.fastapi import RestApiBlueprint
from agave.fastapi.middlewares.utils import get_source_ip
from fastapi import HTTPException, Request

app = RestApiBlueprint()


@app.get('/healthy_auth')
def health_auth_check() -> dict:
    return {'greeting': "I'm authenticated and healthy !!!"}


@app.get('/raise_cuenca_errors')
def raise_cuenca_errors() -> None:
    raise WrongCredsError('you are not lucky enough!')


@app.get('/raise_fast_agave_errors')
def raise_fast_agave_errors() -> None:
    raise UnauthorizedError('nice try!')


@app.get('/you_shall_not_pass')
def you_shall_not_pass() -> None:
    # Este endpoint nunca será ejecutado
    # La prueba de este endpoint hace un mock a nivel middleware
    # para responder con un `UnauthorizedError`
    ...


@app.post('/simulate_400', response_model=None)
def simulate_bad_request() -> NoReturn:
    """Simulated endpoint that raises a bad request error (400)."""
    raise HTTPException(status_code=400, detail='Intentional bad request')


@app.post('/simulate_500', response_model=None)
def simulate_internal_error() -> NoReturn:
    """Simulated endpoint that raises an internal server error (500)."""
    raise Exception('Intentional server error')


@app.post('/simulate_401', response_model=None)
def simulate_unauthorized() -> NoReturn:
    """Simulated endpoint that raises an unauthorized error (401)."""
    raise NoPasswordFoundError('Password not set')


@app.get('/get_ip')
def get_ip(request: Request) -> str:
    return get_source_ip(request)
