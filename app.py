from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI
from Security.secure import router as authRouter
from Routers.typeform import typeformRouter
from Routers.SecPersona.app import router as SecPersonaRouter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Security/Login")

# FastAPI App
app = FastAPI()

# CORS Configuration 
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers

app.include_router(authRouter)
app.include_router(typeformRouter)
app.include_router(SecPersonaRouter)
