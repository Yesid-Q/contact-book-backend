import re

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise import Tortoise

from src.config.system_config import system_app
from src.config.database_config import TORTOISE_ORM

from src.routes.v1 import v1_router
from src.schemas import ErrorResponse, Status

app: FastAPI = FastAPI(
    debug=system_app.DEBUG,
    title=system_app.APP_NAME,
    description=system_app.DESCRIPTION,
    version=system_app.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=system_app.CORS_URL.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup_event():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


@app.on_event("shutdown")
async def shutdown_event():
    await Tortoise.close_connections()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exe):

    if isinstance(exe.detail, str):
        key = re.search(r'\((.*?)\)', exe.detail)
        response = {
            key.group(1): 'Ya esta registrada'
        }
        message = 'Error al guardar los datos'
    else:
        response = exe.detail['detail']
        message = exe.detail['message']

    errors = ErrorResponse(
        status=Status.error,
        message=message,
        errors=response
    ).dict()

    return JSONResponse(
        status_code=exe.status_code,
        content=jsonable_encoder(errors),
        headers=exe.headers
    )


@app.exception_handler(RequestValidationError)
async def validate_exception_handler(request: Request, exe: RequestValidationError):
    response = []
    for detail in exe.errors():
        response.append({
            detail['loc'][1]: detail['msg']
        })

    errors = ErrorResponse(
        status=Status.error,
        message='Datos invalidos',
        errors=response).dict()

    return JSONResponse(
        content=jsonable_encoder(errors),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

app.include_router(router=v1_router, prefix='')
