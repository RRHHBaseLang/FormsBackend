
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from Security.auth import autenticar_token
from Models.codigos import UserName, CodigosDb, UserComentario
import uuid
from jose import jwt
from fastapi import HTTPException
from Security.db import CRUDAdapter
from sqlalchemy import exc
from typing import Type, Any
import functools
from adapters.db import session
import datetime
import os
from Security.model import LoginDB


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
                session.rollback()
            except exc.OperationalError as e:
                raise HTTPException(
                    status_code=500, detail=f"Error de reconexión: {str(e)}"
                )
            return func(self, *args, **kwargs)
    return wrapper


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Security/Login")

@handle_database_errors
async def get_authenticated_user(token: str = Depends(oauth2_scheme)):
    auth = await autenticar_token(token)
    if not auth:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return auth

@handle_database_errors
def _verify_token(token, decoded_token):
    if not decoded_token or not decoded_token.get('sub') or not decoded_token.get('exp'):
        raise HTTPException(
            status_code=401, detail="Token inválido no tiene sub o exp")
    if decoded_token.get('exp') < datetime.datetime.now().timestamp():
        raise HTTPException(status_code=401, detail="Token expirado")
    # need to verify signature
    return decoded_token


typeformRouter = APIRouter(prefix="/typeform", tags=["Typeform"])
security_adapter = CRUDAdapter()


@typeformRouter.post("/Crear")
@handle_database_errors
async def Crear(data: UserName, authenticated_user=Depends(get_authenticated_user), token: str = Depends(oauth2_scheme)):
    jwt_secret_key = os.getenv("JWT_SECRET_KEY") or "secret_key"
    jwt_algorithm = os.getenv("JWT_ALGORITHM") or "HS256"

    decoded_token = jwt.decode(token, jwt_secret_key,
                               algorithms=[jwt_algorithm])
    idcreador = _verify_token(token, decoded_token)['sub']

    newdata = data.copy().__dict__
    newdata['_id'] = str(uuid.uuid4())
    
    mailCreador = session.query(LoginDB).filter_by(
        _id=idcreador).first().correo
    newdata['Creadopor'] = mailCreador
    newdata['respComent'] = {}
    modelo_sqlalchemy = convertir_pydantic_a_sqlalchemy(
        newdata, CodigosDb
    )
    session.add(modelo_sqlalchemy)
    session.commit()
    session.refresh(modelo_sqlalchemy)
    return(newdata)

@typeformRouter.get("/Listar")
@handle_database_errors
async def Listar(authenticated_user=Depends(get_authenticated_user), token: str = Depends(oauth2_scheme)):

    return session.query(CodigosDb).all()

@typeformRouter.get("/Listar/{id}")
@handle_database_errors
async def Listar(id, authenticated_user=Depends(get_authenticated_user), token: str = Depends(oauth2_scheme)):
    return session.query(CodigosDb).filter_by(_id=id).first()

@typeformRouter.delete("/Eliminar/{id}")
@handle_database_errors
async def Eliminar(id, authenticated_user=Depends(get_authenticated_user), token: str = Depends(oauth2_scheme)):
    session.query(CodigosDb).filter_by(_id=id).delete()
    session.commit()
    
@typeformRouter.put("/Refrescar/{id}")
@handle_database_errors
async def Refrescar(id, data: UserComentario, authenticated_user=Depends(get_authenticated_user)):
    lastcoments = session.query(CodigosDb).filter_by(_id=id).first().respComent
    newcoments = lastcoments[data.testid]= {}
    session.query(CodigosDb).filter_by(_id=id).update({'respComent': lastcoments})
    session.commit()