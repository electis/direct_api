import redis
import youtube_dl
from celery import Celery

import settings

app = Celery('direct_api', broker=settings.broker)


@app.task(ignore_result=True)
def youtube_download(y_id, format):
    filename = f"{y_id}_{format}"
    redis_name = f'youtube_download_{filename}'
    r = redis.Redis()
    status = r.get(redis_name)
    if status:
        # check for task?
        return

    r.set(redis_name, 0)
    url = f'http://www.youtube.com/watch?v={y_id}'
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
    with ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError as exc:
            raise
    r.set(redis_name, 100)
