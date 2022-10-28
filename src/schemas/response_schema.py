from enum import Enum
from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar('T')

class Status(str, Enum):
    ok = 'Ok'
    error = 'Error'

class OkResponse(GenericModel, Generic[T]):
    data: T
    message: str
    status: Status

class ErrorResponse(GenericModel, Generic[T]):
    errors: T
    message: str
    status: Status
