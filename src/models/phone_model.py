from tortoise.fields import CharField
from tortoise.fields.relational import ForeignKeyField

from src.models.base_model import BaseModel

class PhoneModel(BaseModel):
    number = CharField(max_length=50, null=True)
    name = CharField(max_length=20, null=True)
    
    contact = ForeignKeyField('models.ContactModel', related_name='phones')

    class Meta:
        table = 'phones'

    def __str__(self):
        return f'{self.name} - {self.number}'