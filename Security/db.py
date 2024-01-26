import functools
from Security.model import LoginDB
from typing import Type, Any
import uuid
from fastapi import HTTPException
import os
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from adapters.db import session

def convertir_pydantic_a_sqlalchemy(modelo_pydantic: dict, modelo_sqlalchemy: Type) -> Any:
    modelo_sqlalchemy_instance = modelo_sqlalchemy(**modelo_pydantic)
    return modelo_sqlalchemy_instance


def handle_database_errors(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except exc.OperationalError:
            try:
                self.db.rollback()  
            except exc.OperationalError as e:
                raise HTTPException(
                    status_code=500, detail=f"Error de reconexión: {str(e)}"
                )
            return func(self, *args, **kwargs)
    return wrapper

class CRUDAdapter():
    def __init__(self):
        self.db = session

    @handle_database_errors
    def temporalData(self, tabla):

        self.tabla = tabla
        modelsselector = {
            'login': LoginDB,
        }
        self.model = modelsselector[tabla]

    @handle_database_errors
    def create(self, data: dict):
        try :
            newdata = data.copy().__dict__
        except :
            newdata = data
        newdata['_id'] = str(uuid.uuid4())
        modelo_sqlalchemy = convertir_pydantic_a_sqlalchemy(
            newdata, self.model)
        self.db.add(modelo_sqlalchemy)
        self.db.commit()
        self.db.refresh(modelo_sqlalchemy)

    @handle_database_errors
    def read_all(self):
        return self.db.query(self.model).all()

    @handle_database_errors
    def read(self, id):
        self.db.query(self.model)
        resultado = self.db.query(self.model).filter_by(_id=id).first()
        if not resultado:
            raise HTTPException(status_code=404, detail="Item no encontrado")

        return resultado

    @handle_database_errors
    def read_by_email(self, email):
        resultado = self.db.query(self.model).filter_by(correo=email).first()
        if not resultado:
            raise HTTPException(status_code=404, detail="Item no encontrado")

        return resultado

    @handle_database_errors
    def update(self, id, data):

        self.db.query(self.model).filter_by(_id=id).update(data)
        self.db.commit()

    @handle_database_errors
    def delete(self, id):
        try:
            self.db.query(self.model).filter_by(_id=id).first()
            if not self.db.query(self.model).filter_by(_id=id).first():
                raise HTTPException(
                    status_code=404, detail="Item no encontrado")
            self.db.query(self.model).filter_by(_id=id).delete()
            self.db.commit()
        except Exception:
            raise HTTPException(status_code=404, detail="Item no encontrado")
