import youtube_dl

import social
from models import Result, Social, Youtube

from fastapi import APIRouter

api_router = APIRouter()


@api_router.post("/youtube", response_model=Result)
def youtube(request: Youtube):
    result = Result()
    # check id
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
    with ydl:
        try:
            result = ydl.extract_info(f'http://www.youtube.com/watch?v={request.y_id}',
                                      download=False)  # We just want to extract the info
        except youtube_dl.utils.DownloadError as exc:
            result.error = str(exc)
            return result
    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        # Just a video
        video = result

    print(video)
    video_url = video['url']
    print(video_url)


@api_router.post("/social", response_model=Result)
def social_view(request: Social):
    service = getattr(social, request.service)()
    result = Result()
    try:
        result.result = service.post(request.message, request.data)
    except Exception as exc:
        result.error = str(exc)
    return result


@api_router.get("/items/")
async def read_items(token: str):
    return {"token": token}
