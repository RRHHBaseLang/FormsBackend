# this is a model for the base data to the login

from pydantic import BaseModel, EmailStr, validator
from pydantic import BaseModel
from typing import Dict
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()


class Register(BaseModel):
    correo: EmailStr
    contrasena: str

    @validator('contrasena')
    def validate_contrasena(cls, value):
        if len(value) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if len(value) > 16:
            raise ValueError(
                'La contraseña no puede tener más de 16 caracteres')
        # Puedes ajustar la validación de caracteres permitidos en la contraseña
        if not any(char.isdigit() or char.isalpha() or char in "!@#$%^&*()-_=+[]{};:,.<>?`~" for char in value):
            raise ValueError(
                'La contraseña debe contener al menos un carácter especial')
        return value

class Login(BaseModel):
    correo: str
    contrasena: str


class LoginDB(Base):
    __tablename__ = 'sec'
    __table_args__ = {'schema': 'schema_auth'}
    _id = Column(String, primary_key=True)
    correo = Column(String , nullable=False)
    contrasena = Column(String, nullable=False)
    token = Column(String, nullable=True)
    