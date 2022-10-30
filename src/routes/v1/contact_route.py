from uuid import UUID

from fastapi import APIRouter, Depends, status, Query, File, UploadFile
from fastapi.exceptions import HTTPException
from tortoise.queryset import Q
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Prefetch

from src.utils import current_user, save_image
from src.models import UserModel, ContactModel, PhoneModel
from src.schemas import ContactRequest, ContactNumberRequest, ContactResponse, ListContactResponse, ContactPhonesResponse

contact_router = APIRouter(
    prefix= '/contact',
    tags= ['contact']
)


@contact_router.get(
    '',
    name= 'List Contacts',
    status_code= status.HTTP_200_OK,
    response_model= ListContactResponse
)
async def contacts_route(
    delete: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    auth: UserModel = Depends(current_user)
):
    result = await ContactModel.paginate(
        Q(user=auth, deleted_at__not_isnull=delete, join_type='AND'),
        prefetch=Prefetch('phones', queryset= PhoneModel.filter(deleted_at__not_isnull=False).limit(2), to_attr='contact_id'),
        page= page, limit= limit
    )
    return result

@contact_router.get(
    '/{id}',
    name= 'Delete/Restore Contact',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= ContactResponse
)
async def get_one_route(id: UUID, delete: bool = Query(False), auth: UserModel = Depends(current_user)):
    if not await ContactModel.exists(pk= id, user=auth):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact not found by id {id}')

    contact = await ContactModel.filter(pk=id).first()

    return contact


@contact_router.post(
    '',
    name= 'Create Contact',
    status_code= status.HTTP_201_CREATED,
    response_model= ContactPhonesResponse
)
async def create_route(
    auth: UserModel = Depends(current_user),
    form: ContactNumberRequest = Depends()
):
    name, lastname, email, birthday, photo, number  = form.__dict__.values()
    try:
        contact = await ContactModel.create(name=name, lastname=lastname, email=email, birthday=birthday, user=auth)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{e}')
    
    if number is not None:
        phone = await PhoneModel.create(number=number, contact=contact)
    
    if photo is not None:
        path = await save_image(photo, contact.id)
        await ContactModel.filter(pk=contact.id).update(photo=path)
        contact.photo = path

    await contact.fetch_related(Prefetch('phones', queryset= PhoneModel.filter(deleted_at__not_isnull=False).limit(2), to_attr='contact_id'))
    
    return contact


@contact_router.put(
    '/{id}',
    name= 'Update Contact',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= ContactResponse
)
async def update_route(
    id: UUID,
    request: ContactRequest,
    auth: UserModel = Depends(current_user)
):
    if not await ContactModel.exists(pk= id, user=auth):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact not found by id {id}')
    try:
        await ContactModel.filter(pk= id).update(**request.dict(exclude_none=True))
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{e}')
    
    contact = await ContactModel.filter(pk= id).first()

    return contact


@contact_router.patch(
    '/{id}',
    name= 'Change Photo Contact',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= ContactResponse
)
async def change_photo_contact(
    id: UUID,
    photo: UploadFile = File(...),
    auth: UserModel = Depends(current_user)
):
    if not await ContactModel.exists(pk= id, user=auth):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact not found by id {id}')

    path = await save_image(photo, id)
    await ContactModel.filter(pk=id).update(photo=path)
    contact = await ContactModel.filter(pk=id).first()
    return contact


@contact_router.delete(
    '/{id}',
    name= 'Delete/Restore Contact',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= ContactResponse
)
async def delete_route(id: UUID, auth: UserModel = Depends(current_user)):
    if not await ContactModel.exists(pk= id, user=auth):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Contact not found by id {id}')

    contact = await ContactModel.get(pk=id)
    await contact.delete()

    return contact

