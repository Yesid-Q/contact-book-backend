import re

pattern = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*(\W|_)).{5,}$')

class PasswordType(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples='Pass145$'
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Contraseña es requerido.')
        if len(v) < 8:
            raise TypeError('Contraseña requiere minimo de 8 caracteres.')
        if len(v) > 16:
            raise TypeError('Contraseña requiere un maximo de 16 caracteres.')
        if not pattern.match(v):
            raise ValueError('Contraseña debe tener 1 mayuscula, 1 minuscula, un numero y un carecter especial.')
        return v

    def __repr__(self):
        return super().__repr__()

