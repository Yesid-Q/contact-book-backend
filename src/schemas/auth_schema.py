from pydantic import BaseModel, constr, EmailStr, Field, validator

from src.types import PasswordType
from src.schemas import BaseResponse

class RestoreRequest(BaseModel):
    username: str = Field(...)

class RegisterRequest(BaseModel):
    username: constr(strip_whitespace=True, to_lower=True, strict=True, max_length=100, min_length=3) = Field(...)
    email: EmailStr = Field(...)
    password: PasswordType = Field(...)
    confirm_password: PasswordType = Field(..., alias='confirmPassword')

    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Contraseña no coinciden.')
        return v

class RecoveryRequest(BaseModel):
    new_password: PasswordType = Field(..., alias='newPassword')
    confirm_password: PasswordType = Field(..., alias='confirmPassword')

    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Contraseña no coinciden.')
        return v

class LoginResponse(BaseModel):
    access_token: str
    type_token: str
    refresh_token: str
    
    class Config:
        allow_population_by_field_name = True
        fields = {
            #'access_token': 'accessToken',
            'type_token': 'typeToken',
            'refresh_token': 'refreshToken'
        }

class CurrentUserResponse(BaseResponse):
    email: str
    username: str