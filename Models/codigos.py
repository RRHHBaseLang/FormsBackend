# this is a model for the base data to the login

from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from typing import Dict
from sqlalchemy.orm import declarative_base
from sqlalchemy import ARRAY, JSON, Column, String

Base = declarative_base()

class testModel(BaseModel):
    formId: str
    responseId: str
class UserCodigo(BaseModel):
    Token: str


class UserName(BaseModel):
    Nombre: str
    formIds: list


class UserComentario(BaseModel):
    testid: str


class CodigosDb(Base):
    __tablename__ = 'Codigos'
    _id = Column(String, primary_key=True)
    Nombre = Column(String, nullable=False)
    Creadopor = Column(String, nullable=False)
    respComent = Column(JSON, nullable=False)
    formIds = Column(ARRAY(String), nullable=True)