"""Запускает сервер FastAPI"""
from uvicorn import run
from uvicorn.config import LOGGING_CONFIG
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

import settings
from router import api_router, clean_router
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
app.include_router(clean_router)


if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = \
        '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

    if settings.ENVIRONMENT != 'production':
        for name in DB().scan():
            DB().delete(name)
    run(app, host=settings.HOST, port=settings.PORT)
