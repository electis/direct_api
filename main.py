from uvicorn import run  # type: ignore
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import settings
from router import api_router
from models import cache

docs_kwargs = {}
if settings.ENVIRONMENT == 'production':
    docs_kwargs = dict(docs_url=None, redoc_url=None)

app = FastAPI(**docs_kwargs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def auth(token: str = Depends(oauth2_scheme)):
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
        for key in cache.scan_iter(f"{cache.prefix}{cache.delimiter}*"):
            cache.delete(key)
    run(app, host="0.0.0.0", port=settings.PORT)
