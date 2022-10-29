from fastapi import APIRouter

from .auth_route import auth_router


v1_router = APIRouter(
    prefix='/v1'
)

v1_router.include_router(router=auth_router, prefix='')
