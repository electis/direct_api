"""эндпоинты проекта"""
from urllib.parse import parse_qs

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from starlette import status
from starlette.responses import RedirectResponse

from exceptions import YouTubeDownloadError, AuthError, UrlError
import serializers
import services

api_router = APIRouter()
clean_router = APIRouter()


@api_router.get("/youtube/", response_model=serializers.YoutubeData)
async def youtube_get(y_id: str, video_format: str = None):
    """Получение данных о видео YouTube"""
    try:
        all_data = await services.youtube_info(y_id, video_format)
    except YouTubeDownloadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return serializers.YoutubeData(y_id=y_id, **all_data)


@api_router.post("/youtube/", response_model=serializers.YoutubeDownloadData)
async def youtube_post(request: serializers.YoutubeDownload, background_tasks: BackgroundTasks):
    """Скачивание видео с YouTube"""
    try:
        status, url = await services.youtube_download(request.y_id, request.format, background_tasks)
    except YouTubeDownloadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return serializers.YoutubeDownloadData(**dict(y_id=request.y_id, status=status, url=url))


@api_router.post("/social", response_model=serializers.SocialResult)
async def social_post(request: serializers.Social):
    """Отправка сообщения в соцсеть"""
    try:
        assert request.message.text or request.message.pict, "Message can't be empty"
        result = await services.social_post(request)
    except (AuthError, UrlError, AssertionError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return serializers.SocialResult(result=result)


@api_router.post("/inform", response_model=serializers.SocialResult)
async def inform_post(request: Request):
    """Отправка уведомления (для форм обратной связи с js)"""
    try:
        body = await request.body()
        body = {key: value[0] for key, value in parse_qs(body.decode()).items()}
        # data = serializers.Inform(**{field: body.get(field) for field in serializers.Inform.__fields__.keys()})
        additional = dict(ip=request.client.host, origin=request.headers.get('origin'))
        await services.inform_post(body, additional)
    except Exception as exc:
        print(exc)
        # raise HTTPException(status_code=500, detail=str(exc)) from exc
    return serializers.SocialResult(result='OK')


@clean_router.post("/info", response_model=serializers.SocialResult)
async def info_post(request: Request):
    """
    Отправка уведомления (для форм обратной связи без js)
    <form method="POST" action="https://direct.electis.ru/info">
    <input type="hidden" id="tg_id" name="tg_id" value="1234567" />
    <input type="hidden" id="redirect" name="redirect" value="/contacts" />
    """
    body = await request.body()
    body = {key: value[0] for key, value in parse_qs(body.decode()).items()}
    additional = dict(ip=request.client.host, origin=request.headers.get('origin'))
    try:
        await services.inform_post(body, additional)
    except Exception as exc:
        print(exc)
    redirect_url = body.get('redirect', request.headers.get('origin'))
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
