from tortoise.fields import CharField
from tortoise.fields.relational import ReverseRelation

from src.models.base_model import BaseModel

class UserModel(BaseModel):
    username = CharField(max_length=100, unique=True)
    email = CharField(max_length=150, unique=True)
    password = CharField(max_length=255)

    contacts: ReverseRelation['ContactModel']

    class Meta:
        table = 'users'
