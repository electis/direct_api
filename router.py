from fastapi import APIRouter

import models
import social
from youtube import YouTube

api_router = APIRouter()


@api_router.post("/youtube/", response_model=models.Result)
def youtube(request: models.Youtube):
    service = YouTube(request.y_id)
    result = models.Result()
    try:
        if request.download:
            pass
        else:
            result.data = service.info()
    except Exception as exc:
        result.error = str(exc)
    else:
        result.result = 'OK'
    return result


@api_router.post("/social", response_model=models.Result)
def social_view(request: models.Social):
    service = getattr(social, request.service)()
    result = models.Result()
    try:
        result.result = service.post(request.message, request.data)
    except Exception as exc:
        result.error = str(exc)
    return result


@api_router.get("/items/")
async def read_items(token: str):
    return {"token": token}
