from uuid import UUID
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import Depends, status
from fastapi.exceptions import HTTPException

from src.config.system_config import system_app
from src.config.oauth_config import oauth2_schema
from src.models import UserModel
from src.schemas import LoginResponse

async def create_tokens(id: UUID) -> LoginResponse:
    expire_auth = datetime.utcnow() + timedelta(hours=system_app.LIFETIME_AUTH)
    expire_refresh = datetime.utcnow() + timedelta(days=system_app.LIFETIME_REFRESH)

    access_token = jwt.encode({ 'exp': expire_auth, 'sub': str(id)}, system_app.SECRET_KEY, algorithm=system_app.TOKEN_ALGORITHM)
    refresh_token = jwt.encode({ 'exp': expire_refresh, 'sub': str(id)}, system_app.SECRET_KEY, algorithm=system_app.TOKEN_ALGORITHM)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'type_token': 'Bearer '
    }


async def validate_token(
    token: str,
    status_error = status.HTTP_401_UNAUTHORIZED,
    message = ''
) -> UserModel:
    exception = HTTPException(
        status_code=status_error,
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= 'User inactivate')

    return user


async def current_user(token: str = Depends(oauth2_schema)) -> UserModel:
    auth: UserModel = await validate_token(token)
    return auth