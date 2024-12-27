from dataclasses import dataclass
from typing import Optional


@dataclass
class FastAgaveError(Exception):
    error: str
    status_code: int


@dataclass
class BadRequestError(FastAgaveError):
    status_code: int = 400


@dataclass
class UnauthorizedError(FastAgaveError):
    status_code: int = 401


@dataclass
class ForbiddenError(FastAgaveError):
    status_code: int = 403


@dataclass
class NotFoundError(FastAgaveError):
    status_code: int = 404


@dataclass
class MethodNotAllowedError(FastAgaveError):
    status_code: int = 405


@dataclass
class ConflictError(FastAgaveError):
    status_code: int = 409


@dataclass
class UnprocessableEntity(FastAgaveError):
    status_code: int = 422


@dataclass
class TooManyRequests(FastAgaveError):
    status_code: int = 429


@dataclass
class FastAgaveViewError(FastAgaveError):
    status_code: int = 500


@dataclass
class ServiceUnavailableError(FastAgaveError):
    status_code: int = 503


@dataclass
class RetryTask(Exception):
    countdown: Optional[int] = None
