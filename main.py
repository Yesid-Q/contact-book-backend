from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from src.config.system_config import system_app
from src.config.database_config import TORTOISE_ORM

from src.routes.v1 import v1_router
from src.schemas import Status

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


@app.exception_handler(RequestValidationError)
async def validate_exception_handler(request: Request, exe: RequestValidationError):
    response = []
    for detail in exe.errors():
        response.append({
            detail['loc'][1]: detail['msg']
        })

    errors = {
        'status': Status.error,
        'message': 'Datos invalidos',
        'errors': response
    }

    return JSONResponse(
        content=jsonable_encoder(errors),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

app.include_router(router=v1_router, prefix='')
app.mount('/static', StaticFiles(directory='./src/images'), name='static')
