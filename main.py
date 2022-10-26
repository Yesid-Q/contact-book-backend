from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from src.config.system_config import system_app
from src.config.database_config import TORTOISE_ORM

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

@app.get('/')
async def hello():
    return {
        'greeting': 'Hola gente bella!!!'
    }