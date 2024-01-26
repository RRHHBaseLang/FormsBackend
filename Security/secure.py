import fastapi
from fastapi.security import OAuth2PasswordRequestForm
from Security.auth import autenticar_token
import Security.model as models
import Security.login as login
import Security.register as register
from pydantic import BaseModel
router = fastapi.APIRouter(prefix="/Security", tags=["Security"])

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(
    tokenUrl="Security/Login")


class tokenmodel(BaseModel):
    token: str


@router.get("/Auth")
async def auth(token: str = fastapi.Depends(oauth2_scheme)):
    return await autenticar_token(token)


@router.post("/Login")
async def Login(data: OAuth2PasswordRequestForm = fastapi.Depends()):
    return login.Login(data.username, data.password)


@router.post("/Register")
async def Register(data: models.Register, token: str = fastapi.Depends(oauth2_scheme)):
    auth = await autenticar_token(token)
    if not auth:
        raise fastapi.HTTPException(
            status_code=401, detail="Credenciales incorrectas")

    return register.Registrar(data)
