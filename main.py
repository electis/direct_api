from pydantic import BaseModel
from typing import Optional, Union

import uvicorn
import youtube_dl
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import social

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

tokens = {'test', 'test2'}


def auth(token: str = Depends(oauth2_scheme)):
    if token in tokens:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


class Youtube(BaseModel):
    y_id: str


class Social(BaseModel):
    service: social.SERVICES
    data: Union[social.OKData, social.VKData]
    message: social.Message


class Result(BaseModel):
    result: Optional[str]
    error: Optional[str]


@app.post("/youtube", response_model=Result)
def youtube(request: Youtube, is_auth: bool = Depends(auth)):
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


@app.post("/social", response_model=Result)
def social_view(request: Social, is_auth: bool = Depends(auth)):
    service = getattr(social, request.service)()
    result = Result()
    try:
        result.result = service.post(request.message, request.data)
    except Exception as exc:
        result.error = str(exc)
    return result


@app.get("/items/")
async def read_items(token: str = Depends(auth)):
    return {"token": token}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
