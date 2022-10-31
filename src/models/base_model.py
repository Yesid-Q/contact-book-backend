from math import ceil
from datetime import datetime
from typing import Type

from tortoise import Model
from tortoise.models import MODEL
from tortoise.fields import DatetimeField, UUIDField
from tortoise.queryset import Q
from tortoise.query_utils import Prefetch


class BaseModel(Model):
    id = UUIDField(pk=True)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
    deleted_at = DatetimeField(null=True)

    class Meta:
        abstract = True
        ordering = ['created_at']

    async def delete(self) -> None:
        self.deleted_at = datetime.now() if self.deleted_at is None else None
        await self.save()

    @classmethod
    async def paginate(
        cls: Type[MODEL],
        queryset: Q,
        prefetch: Prefetch|None = None,
        page: int = 1, limit: int = 10
    ):
        counts: int = await cls.filter(queryset).count()
        if prefetch is None:
            result = await cls.filter(queryset).limit(limit).offset((limit * (page - 1)))
        else:
            result = await cls.filter(queryset).prefetch_related(prefetch).limit(limit).offset((limit * (page - 1)))
        pages = ceil(counts / limit)

        return {
            'count': limit,
            'count_total': counts,
            'page': page,
            'page_total': pages,
            'items_per_page': limit,
            'results': result
        }