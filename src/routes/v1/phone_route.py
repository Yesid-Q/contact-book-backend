from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status
from fastapi.exceptions import HTTPException
from tortoise.queryset import Q
from tortoise.exceptions import IntegrityError

from src.models import PhoneModel, UserModel, ContactModel
from src.utils import current_user
from src.schemas import ListPhonesResponse, PhoneResponse, PhoneRequest

phone_router = APIRouter(
    prefix= '/phone',
    tags= ['Phone']
)


@phone_router.get(
    '',
    name= 'List Phones of one Contact',
    status_code= status.HTTP_200_OK,
    response_model= ListPhonesResponse
)
async def list_phone(
    contact: UUID = Header(..., alias='X-Contact-ID'),
    delete: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    auth: UserModel = Depends(current_user)
):
    phones = await PhoneModel.paginate(
        Q(contact__user_id=auth.id, contact_id=contact, deleted_at__not_isnull=delete, join_type='AND'),
        page= page, limit= limit
    )

    return phones


@phone_router.post(
    '',
    name= 'Create Phone',
    status_code= status.HTTP_201_CREATED,
    response_model= PhoneResponse
)
async def create_phone(
    request: PhoneRequest,
    contact: UUID = Header(..., alias='X-Contact-ID'),
    auth: UserModel = Depends(current_user)
):
    if not await ContactModel.exists(Q(user_id=auth.id, pk=contact, join_type='AND')):
        raise HTTPException(status_code= status.HTTP_405_METHOD_NOT_ALLOWED, detail='Can not done operation')

    try:
        phone = await PhoneModel.create(**request.dict(), contact_id=contact)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{e}')

    return phone


@phone_router.put(
    '/{id}',
    name= 'Update Phone',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= PhoneResponse
)
async def update_phone(
    id: UUID,
    request: PhoneRequest,
    contact: UUID = Header(..., alias='X-Contact-ID'),
    auth: UserModel = Depends(current_user)
):
    if not await PhoneModel.exists(Q(contact__user_id=auth.id, contact_id=contact, pk=id, join_type='AND')):
        raise HTTPException(status_code= status.HTTP_405_METHOD_NOT_ALLOWED, detail='Can not done operation')

    try:
        await PhoneModel.filter(pk=id).update(**request.dict())
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{e}')

    phone = await PhoneModel.filter(pk= id).first()

    return phone


@phone_router.get(
    '/{id}',
    name= 'Get one number',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= PhoneResponse
)
async def get_one_phone(
    id: UUID,
    auth: UserModel = Depends(current_user)
):
    if not await PhoneModel.exists(Q(contact__user_id=auth.id, pk=id, join_type='AND')):
        raise HTTPException(status_code= status.HTTP_405_METHOD_NOT_ALLOWED, detail='Can not done operation')
    phone = await PhoneModel.filter(Q(contact__user_id=auth.id, pk=id, join_type='AND')).first()

    return phone


@phone_router.delete(
    '/{id}',
    name= 'Delete/Restore phone',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= PhoneResponse
)
async def delete_phone(
    id: UUID,
    contact: UUID = Header(..., alias='X-Contact-ID'),
    auth: UserModel = Depends(current_user)
):
    if not await PhoneModel.exists(Q(contact__user_id=auth.id, contact_id=contact, pk=id, join_type='AND')):
        raise HTTPException(status_code= status.HTTP_405_METHOD_NOT_ALLOWED, detail='Can not done operation')

    phone = await PhoneModel.get(pk=id)
    await phone.delete()

    return phone