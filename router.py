from fastapi import APIRouter, BackgroundTasks

import models
import social
from youtube import YouTube

api_router = APIRouter()


@api_router.post("/youtube/", response_model=models.Result)
async def youtube(request: models.Youtube, background_tasks: BackgroundTasks):
    service = YouTube(request.y_id)
    result = models.Result()
    try:
        if request.download:
            result.data = service.download(request.format, background_tasks)
        else:
            result.data = service.info(request.format)
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
