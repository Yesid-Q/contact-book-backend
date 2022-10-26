import ssl

from src.config.system_config import system_app

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'database': system_app.DATABASE_DATABASE,
                'host': system_app.DATABASE_URL,
                'password': system_app.DATABASE_PASSWORD,
                'port': system_app.DATABASE_PORT,
                'user': system_app.DATABASE_USER,
                'ssl': 'disable' if system_app.DEBUG else ctx
            }
        }
    },
    'apps': {
        'models': {
            'models': system_app.MODELS,
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'UTC'
}