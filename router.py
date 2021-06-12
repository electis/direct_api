from fastapi import APIRouter, BackgroundTasks

import serializers
import services
import social

api_router = APIRouter()


@api_router.get("/youtube/", response_model=serializers.YouTubeInfoResult)
async def youtube_get(y_id: str, format: str = None):
    result = serializers.YouTubeInfoResult()
    try:
        all_data = await services.YouTube.info(y_id, format)
    except Exception as exc:
        result.error = str(exc)
    else:
        result.data = serializers.YoutubeData(y_id=y_id, **all_data)
    return result


@api_router.post("/youtube/", response_model=serializers.YoutubeDownloadResult)
async def youtube_post(request: serializers.YoutubeDownload, background_tasks: BackgroundTasks):
    result = serializers.YoutubeDownloadResult()
    try:
        status, url = await services.YouTube.download(request.y_id, request.format, background_tasks)
    except Exception as exc:
        result.error = str(exc)
    else:
        result.data = serializers.YoutubeData(**dict(y_id=request.y_id, status=status, url=url))
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
