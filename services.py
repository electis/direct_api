"""Сервисный слой - логика работы эндпоинтов"""
import managers
from tasks import youtube_download


class YouTube:
    """эндпоинты YouTube"""

    @staticmethod
    async def info(y_id: str, video_format=None) -> dict:
        """получение информации о видео"""
        youtube = managers.YouTube(y_id, video_format)
        result = await youtube.get_info()
        result['filtered_formats'] = youtube.filter_formats()
        if video_format:
            result['status'], result['url'] = await youtube.check_status()
        return result

    @staticmethod
    async def download(y_id: str, video_format: str, background_tasks) -> tuple:
        """скачивание видео"""
        youtube = managers.YouTube(y_id, video_format)
        status, url = await youtube.check_status()
        if not url and status is None:
            background_tasks.add_task(youtube_download, y_id, video_format)
            # youtube_download(y_id, format)
        return status, url
