from typing import Union
import youtube_dl as ydl
from youtube_search import YoutubeSearch as yts
from fastapi import FastAPI,Request,Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,StreamingResponse
import requests as rq

app = FastAPI()
app.mount('/static',StaticFiles(directory = 'static'), name='static')

templates = Jinja2Templates(directory="templates")

@app.get('/home',response_class = HTMLResponse )
async def home(request:Request):
    return templates.TemplateResponse("index.html",{'request':request })

def filter_formats(list_of_formats) -> list[dict]:
    _formats = []
    keep = ('filesize', 'format_id', 'quality', 'url', 'format','ext' )
    for format in list_of_formats:
        if format.get('format_id') in ('249','250','251'): 
            _formats.append(       
                { k:v for k,v in format.items() if k in keep }
            )
        else:
            continue
    return _formats

@app.get('/search/{query}')
async def search_music( query:str ) -> list[dict]:
    result = []
    keep = ('id', 
                'formats', 
                'thumbnails', 
                'thumbnails',
                'title',
                'like_count',
                'duration',
                'view_count',
                'url_suffix')
    raw = yts(query).to_dict()
    for info in raw:
        _ = { k:v for k,v in info.items() if k in keep }
        result.append( _ )
    return result

@app.get('/audio/{video_id}')
async def get_audio( video_id ):
    url = f'https://www.youtube.com/watch?v={video_id}'
    with ydl.YoutubeDL() as yt:
        _ = yt.extract_info(url=url, download=False)

    audio_src = filter_formats( _['formats'] )[0]['url']

    return audio_src

@app.get('/audio/stream/{video_id}')
async def get_audio( video_id ):
    url = f'https://www.youtube.com/watch?v={video_id}'
    with ydl.YoutubeDL() as yt:
        _ = yt.extract_info(url=url, download=False)

    audio_src = filter_formats( _['formats'] )[0]['url']
    audio_iter =  rq.get(audio_src,stream=True).iter_content()

    return StreamingResponse(audio_iter,media_type='audio/webm')


@app.get(" /test")
async def test():
    return [{'a':1,'b':2}]