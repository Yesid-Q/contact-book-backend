from os import getcwd
from uuid import UUID

from fastapi import UploadFile

PATH_IMAGES = f'{getcwd()}/src/images'

async def save_image(file: UploadFile, id: UUID) -> str:
    with open(f'{PATH_IMAGES}/{id}.png', 'wb') as my_file:
        content = await file.read()
        my_file.write(content)
        my_file.close()

    return f'/static/{id}.png'

def optimization_image(id: UUID):
    pass