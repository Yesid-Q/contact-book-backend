from typing import Optional, List

from pydantic import BaseModel, constr, Field

from src.schemas import BaseResponse, PaginateResponse

class PhoneRequest(BaseModel):
    number: constr(strip_whitespace=True, max_length=50, min_length=7, regex='[0-9]') = Field(...)
    name: Optional[constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=20)] = Field(None)


class PhoneResponse(BaseResponse):
    number: Optional[str] = Field(None)
    name: Optional[str] = Field(None)


class ListPhonesResponse(PaginateResponse):
    results: List[PhoneResponse]
