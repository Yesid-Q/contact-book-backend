from fastapi import APIRouter

from .auth_route import auth_router
from .contact_route import contact_router
from .phone_route import phone_router

v1_router = APIRouter(
    prefix='/v1'
)

v1_router.include_router(router=auth_router, prefix='')
v1_router.include_router(router=contact_router, prefix='')
v1_router.include_router(router=phone_router, prefix='')