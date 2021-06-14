"""эндпоинты проекта"""
from fastapi import APIRouter, BackgroundTasks

from exceptions import YouTubeDownloadError, AuthError, UrlError
import serializers
import services
import social

api_router = APIRouter()


@api_router.get("/youtube/", response_model=serializers.YouTubeInfoResult)
async def youtube_get(y_id: str, video_format: str = None):
    """получение данных о видео YouTube"""
    result = serializers.YouTubeInfoResult()
    try:
        all_data = await services.YouTube.info(y_id, video_format)
    except YouTubeDownloadError as exc:
        result.error = str(exc)
    else:
        result.data = serializers.YoutubeData(y_id=y_id, **all_data)
    return result


@api_router.post("/youtube/", response_model=serializers.YoutubeDownloadResult)
async def youtube_post(
    request: serializers.YoutubeDownload, background_tasks: BackgroundTasks
):
    """скачивание видео с YouTube"""
    result = serializers.YoutubeDownloadResult()
    try:
        status, url = await services.YouTube.download(
            request.y_id, request.format, background_tasks
        )
    except YouTubeDownloadError as exc:
        result.error = str(exc)
    else:
        result.data = serializers.YoutubeDownloadData(
            **dict(y_id=request.y_id, status=status, url=url)
        )
    return result


@api_router.post("/social", response_model=serializers.Result)
def social_view(request: serializers.Social):
    """отправка сообщения в соцсеть"""
    service = getattr(social, request.service)()
    result = serializers.Result()
    try:
        result.result = service.post(request.message, request.data)
    except (AuthError, UrlError) as exc:
        result.error = str(exc)
    return result
