from fastapi import APIRouter, BackgroundTasks

import serializers
import services
import managers
import social
from tasks import youtube_download

api_router = APIRouter()


@api_router.get("/youtube/", response_model=serializers.YouTubeResult)
async def youtube(request: serializers.YoutubeInfo):
    result = serializers.YouTubeResult()
    try:
        all_data = await services.YouTube.info(request.y_id, request.format)
        result.data = serializers.YoutubeData(**all_data)
    except Exception as exc:
        result.error = str(exc)
    return result


@api_router.post("/youtube/", response_model=serializers.YouTubeResult)
async def youtube(request: serializers.Youtube, background_tasks: BackgroundTasks):
    result = serializers.YouTubeResult()
    youtube = managers.YouTube(request.y_id, request.format)
    try:
        if not request.download:
            await youtube.get_info()
        data = serializers.YoutubeData(y_id=request.y_id, filtered_formats=youtube.filter_formats(), **youtube.video)
        if request.format:
            data.status, data.url = youtube.check_status()
            if request.download and data.status is None or data.url is None:
                background_tasks.add_task(youtube_download, request.y_id, request.format)
                # youtube_download(request.y_id, request.format)
                data.status = '0'
        result.data = data
    except Exception as exc:
        result.error = str(exc)
    return result


@api_router.post("/social", response_model=serializers.Result)
def social_view(request: serializers.Social):
    service = getattr(social, request.service)()
    result = serializers.Result()
    try:
        result.result = service.post(request.message, request.data)
    except Exception as exc:
        result.error = str(exc)
    return result


@api_router.get("/items/")
async def read_items(token: str):
    return {"token": token}
