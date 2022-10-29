from uuid import UUID
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import status
from fastapi.exceptions import HTTPException

from src.config.system_config import system_app
from src.models import SessionModel, UserModel
from src.schemas import LoginResponse
from src.enums.auth_enum import AuthEnum
from src.enums.user_enum import ModelEnum

async def create_tokens(id: UUID, user_agent: str = None) -> LoginResponse:
    expire_auth = datetime.utcnow() + timedelta(minutes=system_app.LIFETIME_AUTH)
    expire_refresh = datetime.utcnow() + timedelta(days=system_app.LIFETIME_REFRESH)

    auth_token = jwt.encode({ 'exp': expire_auth, 'sub': str(id)}, system_app.SECRET_KEY, algorithm=system_app.TOKEN_ALGORITHM)
    refresh_token = jwt.encode({ 'exp': expire_refresh, 'sub': str(id)}, system_app.SECRET_KEY, algorithm=system_app.TOKEN_ALGORITHM)

    await SessionModel.create(
        token= auth_token,
        refresh= refresh_token,
        user_id= id,
        device= '' if user_agent is None else user_agent
        )

    return {
        'auth_token': auth_token,
        'refresh_token': refresh_token,
        'type_token': 'Bearer '
    }


async def validate_token(
    token: str,
    status_error = status.HTTP_401_UNAUTHORIZED,
    message = AuthEnum.UNAUTHORIZED
) -> UserModel:
    exception = HTTPException(
        status_code=status,
        detail= message,
        headers={'WWW-Authenticate': 'Bearer'}
    )
    
    try:
        payload = jwt.decode(token, system_app.SECRET_KEY, algorithms=[system_app.TOKEN_ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise exception
    except:
        raise exception

    user = await UserModel.get_or_none(pk=user_id)

    if user is None:
        exception.status_code = status.HTTP_403_FORBIDDEN
        raise exception

    if user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= ModelEnum.DELETED_AT)

    return user

