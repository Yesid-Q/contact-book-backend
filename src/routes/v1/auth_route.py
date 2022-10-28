from fastapi import APIRouter, Depends, Header, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.queryset import Q
from tortoise.exceptions import IntegrityError

from src.models import UserModel
from src.schemas import (
    OkResponse,
    LoginResponse,
    RegisterRequest,
    Status,
    RestoreRequest,
    RestoreResponse,
    RecoveryRequest
)
from src.utils import (
    create_tokens,
    hash_password,
    validate_password,
    validate_token,
    send_email,
    minitoken_encode,
    minitoken_decode
)

from src.enums.auth_enum import AuthEnum
from src.enums.user_enum import ModelEnum

auth_router = APIRouter(
    prefix= '/auth',
    tags= ['auth']
)


@auth_router.post(
    '/login',
    name= 'login',
    status_code= status.HTTP_200_OK,
    response_model= OkResponse[LoginResponse]
)
async def login_route(
    form: OAuth2PasswordRequestForm = Depends(),
    user_agent: str | None = Header(default=None)
):
    user = await UserModel.filter(Q(
        Q(username= form.username), Q(email= form.username), join_type= 'OR'
    )).first()

    error = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail= {
                'message': AuthEnum.CREDENTIALS,
                'detail': 'Credentials invalid.'
            }
        )

    if user is None:
        raise error

    if not validate_password(form.password, user.password):
        raise error

    tokens = await create_tokens(user.id, user_agent)
    
    return OkResponse(
        message= AuthEnum.LOGIN,
        status= Status.ok,
        data= tokens).dict()


@auth_router.post(
    '/register',
    name= 'Register',
    status_code= status.HTTP_201_CREATED,
    response_model= OkResponse[LoginResponse]
)
async def register_route(
    request: RegisterRequest,
    user_agent: str | None = Header(default=None)
):
    request.password = await hash_password(request.password)

    try:
        user = await UserModel.create(**request.dict(exclude={'confirm_password'}))
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'{e}')
    
    tokens = await create_tokens(user.id, user_agent)
    
    return OkResponse(
        message= AuthEnum.REGISTER,
        status= Status.ok,
        data= tokens).dict()


@auth_router.get(
    '/refresh',
    name= 'Refresh',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= OkResponse[LoginResponse]
)
async def refresh_route(
    refresh_token: str = Header(...),
    user_agent: str | None = Header(default=None)
):
    user = await validate_token(refresh_token[7:], status.HTTP_403_FORBIDDEN, AuthEnum.FORBIDDEN)

    tokens = await create_tokens(user.id, user_agent)
    
    return OkResponse(
        message= AuthEnum.RESTORE,
        status= Status.ok,
        data= tokens
        ).dict()


@auth_router.post(
    '/restore',
    name= 'Restore',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= OkResponse[RestoreResponse]
)
async def restore_route(
    request: RestoreRequest,
    #background_task: BackgroundTasks
):
    user = await UserModel.filter(Q(
        Q(username= request.username), Q(email= request.username), join_type= 'OR'
    )).first()

    if user is None:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= {
                'message': ModelEnum.NOT_EXIST,
                'detail': ''
            })
    
    tk = await minitoken_encode(user.id)

    #background_task.add_task(send_email, user.email, message=tk)

    return OkResponse(
        message= AuthEnum.RESTORE,
        status= Status.ok,
        data= {
            'token': tk
        }
    ).dict()


@auth_router.put(
    '/recovery/{token}',
    name= 'Recovery',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= OkResponse[LoginResponse]
)
async def recovery_route(
    request: RecoveryRequest,
    token: str = Depends(minitoken_decode),
    user_agent: str | None = Header(default=None)
):
    user = await UserModel.filter(pk=token).first()

    if user is None:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= {
                'message': ModelEnum.NOT_EXIST,
                'detail': ''
            })
    password = await hash_password(request.new_password)

    await UserModel.filter(pk=token).update(password= password)

    tokens = await create_tokens(token, user_agent)
    
    return OkResponse(
        message= AuthEnum.RESTORE,
        status= Status.ok,
        data= tokens
        ).dict()
