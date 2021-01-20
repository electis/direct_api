from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI
from typing import Optional

import social

app = FastAPI()


class Social(BaseModel):
    service: social.SERVICES
    user_data: social.UserData
    service_data: social.ServiceData
    message: social.Message


class Result(BaseModel):
    result: Optional[str]
    error: Optional[str]

# TODO auth
@app.post("/social", response_model=Result)
def social_view(request: Social):
    service = getattr(social, request.service)()
    result = Result()
    try:
        result.result = service.post(request.message, request.user_data, request.service_data)
    except Exception as exc:
        result.error = str(exc)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
