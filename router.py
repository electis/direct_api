"""эндпоинты проекта"""
from fastapi import APIRouter, BackgroundTasks, HTTPException

from exceptions import YouTubeDownloadError, AuthError, UrlError
import serializers
import services

api_router = APIRouter()


@api_router.get("/youtube/", response_model=serializers.YoutubeData)
async def youtube_get(y_id: str, video_format: str = None):
    """получение данных о видео YouTube"""
    try:
        all_data = await services.youtube_info(y_id, video_format)
    except YouTubeDownloadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return serializers.YoutubeData(y_id=y_id, **all_data)


@api_router.post("/youtube/", response_model=serializers.YoutubeDownloadData)
async def youtube_post(request: serializers.YoutubeDownload, background_tasks: BackgroundTasks):
    """скачивание видео с YouTube"""
    try:
        status, url = await services.youtube_download(request.y_id, request.format, background_tasks)
    except YouTubeDownloadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return serializers.YoutubeDownloadData(**dict(y_id=request.y_id, status=status, url=url))


@api_router.post("/social", response_model=serializers.SocialResult)
async def social_post(request: serializers.Social):
    """отправка сообщения в соцсеть"""
    try:
        assert request.message.text or request.message.pict, "Message can't be empty"
        result = await services.social_post(request)
    except (AuthError, UrlError, AssertionError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return serializers.SocialResult(result=result)
