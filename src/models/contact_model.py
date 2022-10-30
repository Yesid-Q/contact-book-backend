from tortoise.fields import CharField, DateField, TextField
from tortoise.fields.relational import ForeignKeyField, ReverseRelation

from src.models.base_model import BaseModel

class ContactModel(BaseModel):
    name = CharField(max_length=100)
    lastname = CharField(max_length=100, null=True)
    email = CharField(max_length=150, null=True)
    birthday = DateField(null=True)
    photo = TextField(null=True)

    user = ForeignKeyField('models.UserModel', related_name='contact_user_fk')

    phones: ReverseRelation['PhoneModel']

    class Meta:
        table = 'contacts'

    def __str__(self):
        return f'{self.name}-{self.lastname}'


