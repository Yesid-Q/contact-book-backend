from enum import Enum

class AuthEnum(str, Enum):
    LOGIN = ''
    REGISTER = ''
    RESTORE = ''
    UNAUTHORIZED = ''
    FORBIDDEN = ''
    CREDENTIALS = ''