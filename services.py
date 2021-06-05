import managers
from tasks import youtube_download


class YouTube:

    @staticmethod
    async def info(y_id: str, format=None) -> dict:
        youtube = managers.YouTube(y_id, format)
        result = await youtube.get_info()
        result['filtered_formats'] = youtube.filter_formats()
        if format:
            result['status'], result['url'] = await youtube.check_status()
        return result

    @staticmethod
    async def download(y_id: str, format: str, background_tasks) -> tuple:
        youtube = managers.YouTube(y_id, format)
        status, url = await youtube.check_status()
        if not url and status is None:
            background_tasks.add_task(youtube_download, y_id, format)
            # youtube_download(y_id, format)
        return status, url
