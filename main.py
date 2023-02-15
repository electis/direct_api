"""Запускает сервер FastAPI"""
from uvicorn import run
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

import settings
from router import api_router
from models import DB

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def auth(token: str = Depends(oauth2_scheme)):
    """Реализует аутентификацию по токену для всех методов"""
    if token == settings.SECRET_TOKEN:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


app.include_router(api_router, dependencies=[Depends(auth)])


if __name__ == "__main__":
    if settings.ENVIRONMENT != 'production':
        for name in DB().scan():
            DB().delete(name)
    run(app, host=settings.HOST, port=settings.PORT)
