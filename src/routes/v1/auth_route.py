from fastapi import APIRouter, Depends, Header, status, Response
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.queryset import Q
from tortoise.exceptions import IntegrityError

from src.models import UserModel
from src.schemas import (
    LoginResponse,
    RegisterRequest,
    RestoreRequest,
    RecoveryRequest,
    CurrentUserResponse
)
from src.utils import (
    create_tokens,
    current_user,
    hash_password,
    validate_password,
    validate_token,
    send_email,
    minitoken_encode,
    minitoken_decode
)


auth_router = APIRouter(
    prefix= '/auth',
    tags= ['auth']
)


@auth_router.post(
    '/login',
    name= 'login',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= LoginResponse
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
                'message': 'Invalid credentials',
                'detail': 'Invalid credentials.'
            }
        )

    if user is None:
        raise error

    if not validate_password(form.password, user.password):
        raise error

    tokens = await create_tokens(user.id, user_agent)
    
    return tokens


@auth_router.post(
    '/register',
    name= 'Register',
    status_code= status.HTTP_201_CREATED,
    response_model= LoginResponse
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
    
    return tokens


@auth_router.get(
    '/refresh',
    name= 'Refresh',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= LoginResponse
)
async def refresh_route(
    refresh_token: str = Header(...),
    user_agent: str | None = Header(default=None)
):
    user = await validate_token(refresh_token[7:], status.HTTP_403_FORBIDDEN, 'Forbidden')

    tokens = await create_tokens(user.id, user_agent)
    
    return tokens


@auth_router.post(
    '/restore',
    name= 'Restore',
    status_code= status.HTTP_204_NO_CONTENT,
)
async def restore_route(
    request: RestoreRequest,
    #background_task: BackgroundTasks,
    response: Response
):
    user = await UserModel.filter(Q(
        Q(username= request.username), Q(email= request.username), join_type= 'OR'
    )).first()

    if user is None:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= {
                'message': 'User not found',
                'detail': 'User not found'
            })
    
    tk = await minitoken_encode(user.id)

    #background_task.add_task(send_email, user.email, message=tk)

    response.headers['Contact-Token'] = tk

    return 


@auth_router.patch(
    '/recovery',
    name= 'Recovery',
    status_code= status.HTTP_202_ACCEPTED,
    response_model= LoginResponse
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
                'message': 'User not found',
                'detail': 'User not found'
            })
    password = await hash_password(request.new_password)

    await UserModel.filter(pk=token).update(password= password)

    tokens = await create_tokens(token, user_agent)
    
    return tokens


@auth_router.get(
    '',
    name= 'Current info user',
    status_code= status.HTTP_200_OK,
    response_model= CurrentUserResponse
)
async def get_info(
    auth: UserModel = Depends(current_user)
):
    return auth