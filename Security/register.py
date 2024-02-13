import uuid
from fastapi import HTTPException
import bcrypt

from Security.model import Register, LoginDB
from Security.db import CRUDAdapter


def Registrar(Data: Register):
    adapter = CRUDAdapter()
    adapter.temporalData('login')
    try:
        user = adapter.read_by_email(Data.correo)
    except:

        try:
            adapter.read_by_email(Data.correo)
            raise HTTPException(status_code=409, detail="El correo ya existe")
        except:
            # Generar un ID único para el usuario
            
            newdata = dict(Data.copy())

            # Hashear la contraseña antes de almacenarla usando bcrypt
            hashed_password = bcrypt.hashpw(
                newdata['contrasena'].encode('utf-8'), bcrypt.gensalt(10))
            newdata['contrasena'] = hashed_password.decode(
                'utf-8')  # Decodificar el hash a una cadena

            adapter.create(newdata)
