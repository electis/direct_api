"""Сервисный слой - логика работы эндпоинтов"""
from fastapi import BackgroundTasks

import managers
import serializers
import social
from tasks import youtube_download_task


async def youtube_info(y_id: str, video_format: str = None) -> dict:
    """получение информации о видео"""
    youtube = managers.YouTube(y_id, video_format)
    result = await youtube.get_info()
    result['filtered_formats'] = youtube.filter_formats()
    if video_format:
        result['status'], result['url'] = await youtube.check_status()
    return result


async def youtube_download(y_id: str, video_format: str, background_tasks: BackgroundTasks) -> tuple:
    """скачивание видео"""
    youtube = managers.YouTube(y_id, video_format)
    status, url = await youtube.check_status()
    if not url and status is None:
        background_tasks.add_task(youtube_download_task, y_id, video_format)
    return status, url


async def social_post(social_model: serializers.Social) -> str:
    """Отправка сообщения в соцсеть"""
    service: social.Service = getattr(social, social_model.service)()
    service = social.Logger(service)
    return await service.post_message(social_model.message, social_model.data)
