from tortoise.fields import CharField
from tortoise.fields.relational import ForeignKeyField

from src.models.base_model import BaseModel

class SessionModel(BaseModel):
    device = CharField(max_length=100)
    token = CharField(max_length=255)
    refresh = CharField(max_length=255)

    user = ForeignKeyField('models.UserModel', related_name='session_user_fk')

    class Meta:
        table = 'sessions'
