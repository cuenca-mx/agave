from dataclasses import dataclass
from typing import Optional


@dataclass
class AgaveError(Exception):
    error: str
    status_code: int


@dataclass
class BadRequestError(AgaveError):
    status_code: int = 400


@dataclass
class UnauthorizedError(AgaveError):
    status_code: int = 401


@dataclass
class ForbiddenError(AgaveError):
    status_code: int = 403


@dataclass
class NotFoundError(AgaveError):
    status_code: int = 404


@dataclass
class MethodNotAllowedError(AgaveError):
    status_code: int = 405


@dataclass
class ConflictError(AgaveError):
    status_code: int = 409


@dataclass
class UnprocessableEntity(AgaveError):
    status_code: int = 422


@dataclass
class TooManyRequests(AgaveError):
    status_code: int = 429


@dataclass
class AgaveViewError(AgaveError):
    status_code: int = 500


@dataclass
class ServiceUnavailableError(AgaveError):
    status_code: int = 503


@dataclass
class RetryTask(Exception):
    countdown: Optional[int] = None
