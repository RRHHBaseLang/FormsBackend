import datetime
from jose import jwt
import os
from fastapi import HTTPException
from Security.db import CRUDAdapter



def _verify_token(token, decoded_token):
    if not decoded_token or not decoded_token.get('sub') or not decoded_token.get('exp'):
        raise HTTPException(status_code=401, detail="Token inválido no tiene sub o exp")
    if decoded_token.get('exp') < datetime.datetime.now().timestamp():
        raise HTTPException(status_code=401, detail="Token expirado")
    ##need to verify signature
    return decoded_token


async def autenticar_token(token):
    adapter = CRUDAdapter()
    adapter.temporalData('login')
    jwt_secret_key = os.getenv("JWT_SECRET_KEY") or "secret_key"
    jwt_algorithm = os.getenv("JWT_ALGORITHM")  or "HS256"

    if not (jwt_secret_key and jwt_algorithm):
        raise HTTPException(
            status_code=500, detail="Invalid JWT configuration")

    try:
        decoded_token = jwt.decode(token, jwt_secret_key,
                               algorithms=[jwt_algorithm])
        decoded_token = _verify_token(token, decoded_token)
        print(decoded_token)
        user = adapter.read(decoded_token['sub'])
        print(user.token)
        if not user or user.token != token:
            raise HTTPException(status_code=401, detail="Token inválido no coincide")
        return True
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido " + str(e))
