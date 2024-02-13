import os
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from Security.db import CRUDAdapter


def convertir_a_diccionario(user):
    # Convertir los datos relevantes a un diccionario
    return {
        "_id": user._id,
        "nombre": user.nombre,
        "correo": user.correo,
        "contrasena": user.contrasena,
        "codigo": user.codigo,
        "config": user.config,
        "token": user.token,
    }


def generarToken(user):
    jwt_secret_key = os.getenv("JWT_SECRET_KEY") or "secret_key"
    jwt_algorithm = os.getenv("JWT_ALGORITHM") or "HS256"
    jwt_expiration = os.getenv("JWT_EXPIRATION") or "2"

    if not (jwt_secret_key and jwt_algorithm and jwt_expiration):
        raise HTTPException(
            status_code=500, detail="Invalid JWT configuration")

    expiration = datetime.utcnow() + timedelta(hours=int(jwt_expiration))

    jwt_token = jwt.encode({
        # Convertir a cadena para evitar problemas con la serialización
        "sub": str(user._id),
        "exp": expiration
    }, jwt_secret_key, algorithm=jwt_algorithm)

    return jwt_token


def Login(email: str, password: str):
    adapter = CRUDAdapter()
    adapter.temporalData('login')
    try:
        
        user = adapter.read_by_email(email)
    except:
        raise HTTPException(status_code=401, detail="Credenciales inválidas 1")
    if user:
        stored_password = user.contrasena

        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            print("Credenciales correctas")
            token = generarToken(user)
            adapter.update(user._id, {'token': token})
            return {"access_token": token, "token_type": "bearer"}


    raise HTTPException(status_code=401, detail="Credenciales inválidas")
