from datetime import date
from typing import Optional, List

from fastapi import File, Form, UploadFile, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, constr, Field, EmailStr, validator

from src.schemas import BaseResponse, PhoneResponse, PaginateResponse

class ContactNumberRequest:

    def __init__(
        self,
        name: Optional[str] = Form(None, max_length=100, min_length=3, strip_whitespace=True),
        lastname: Optional[str] = Form(None, max_length=100, min_length=3, strip_whitespace=True),
        email: Optional[EmailStr] = Form(None),
        birthday: Optional[date] = Form(None),
        photo: Optional[UploadFile] = File(None),
        number: Optional[str] = Form(None, max_length=50, min_length=7)
    ):
        self.name = name
        self.lastname = lastname
        self.email = email
        self.birthday = birthday
        self.photo = photo
        self.number = number

        if self.name is None and self.number is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Name or phone number is required')


class ContactRequest(BaseModel):
    name: Optional[constr(max_length=100, min_length=3, strip_whitespace=True)] = Field(None)
    lastname: Optional[constr(max_length=100, min_length=3, strip_whitespace=True)] = Field(None)
    email: Optional[EmailStr] = Field(None)
    birthday: Optional[date] = Field(None)


class ContactResponse(BaseResponse):
    name: Optional[str] = Field(None)
    lastname: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None)
    birthday: Optional[date] = Field(None)
    photo: Optional[str] = Field(None)


class ContactPhonesResponse(ContactResponse):
    phones: List[PhoneResponse] = Field(None)

    @validator('phones', pre=True)
    def _iter_to_list(cls, v):
        if v is not None:
            return list(v)
        return None

class ListContactResponse(PaginateResponse):
    results: List[ContactPhonesResponse]