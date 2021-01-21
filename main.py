from pydantic import BaseModel
from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import social

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

tokens = {'test', 'test2'}

def auth(token: str = Depends(oauth2_scheme)):
    if token in tokens:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


class Social(BaseModel):
    service: social.SERVICES
    user_data: social.UserData
    service_data: social.ServiceData
    message: social.Message


class Result(BaseModel):
    result: Optional[str]
    error: Optional[str]


@app.post("/social", response_model=Result)
def social_view(request: Social, is_auth: bool = Depends(auth)):
    service = getattr(social, request.service)()
    result = Result()
    try:
        result.result = service.post(request.message, request.user_data, request.service_data)
    except Exception as exc:
        result.error = str(exc)
    return result


@app.get("/items/")
async def read_items(token: str = Depends(auth)):
    return {"token": token}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
