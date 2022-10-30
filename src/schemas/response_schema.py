from enum import Enum
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Status(str, Enum):
    ok = 'Ok'
    error = 'Error'

class BaseResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        fields = {
            'created_at': 'createdAt',
            'updated_at': 'updatedAt',
            'deleted_at': 'deletedAt'
        }

class PaginateResponse(BaseModel):
    count: int
    count_total: int
    page: int
    page_total: int
    items_per_page: int

    class Config:
        allow_population_by_field_name = True
        fields = {
            'count_total': 'countTotal',
            'page_total': 'pageTotal',
            'items_per_page': 'itemsPerPage'
        }