import base64
from uuid import UUID

from fastapi import Path, status
from fastapi.exceptions import HTTPException


async def minitoken_encode(id: UUID) -> str:
    bytes = str(id).encode('ascii')
    b64 = base64.b64encode(bytes)
    tk = b64.decode('ascii')
    return tk


async def minitoken_decode(token: str = Path(...)) -> UUID:
    try:
        bytes = token.encode('ascii')
        b64 = base64.b64decode(bytes)
        id = b64.decode('ascii')
        try:
            _ = UUID(id, version=4)
        except:
            pass
    except:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail='Error en la llave primaria.')
    return id