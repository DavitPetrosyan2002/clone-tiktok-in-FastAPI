import shutil
from fastapi import UploadFile,BackgroundTasks,HTTPException,Depends,Request
from fastapi.responses import JSONResponse
from uuid import uuid4
from pathlib import Path
from .models import Video
from auth.models import User
from typing import IO, Generator
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from sqlalchemy import Insert,Select
from sqlalchemy import select
from .schemas import UploadVideo






async def save_video(request:Request,user:int,file:UploadFile,title:str,description:str,
    background_tasks:BackgroundTasks,
    session:AsyncSession=Depends(get_async_session)):
    try:
        file_name=f"media/{user}_{uuid4()}.mp4"
        if file.content_type=='video/mp4':
            file_content = await file.read()
            background_tasks.add_task(write_video,file_name,file_content)
        else:
            raise HTTPException(status_code=418,detail="it isnt mp4")    
        info=UploadVideo(title=title,description=description)
        stms=Insert(Video).values(user_id=user,**dict(info),file=file_name) 
        await session.execute(stms)
        await session.commit() 
        return JSONResponse({"status":201,"filename":file.filename})
    except HTTPException as e:
        return JSONResponse({"status":401,"error":e.detail})
       
def write_video(file_name:str,file_content: bytes):
    with open(file_name,"wb") as buffer:
        buffer.write(file_content)

def ranged(
        file: IO[bytes],
        start: int = 0,
        end: int = None,
        block_size: int = 8192,
) -> Generator[bytes, None, None]:
    consumed = 0

    file.seek(start)
    while True:
        data_length = min(block_size, end - start - consumed) if end else block_size
        if data_length <= 0:
            break
        data = file.read(data_length)
        if not data:
            break
        consumed += data_length
        yield data

    if hasattr(file, 'close'):
        file.close()


async def open_file(request:Request,video_pk:int,session:AsyncSession=Depends(get_async_session))-> tuple:
    try:
        video = (await session.execute(select(Video).where(Video.id==video_pk))).scalar_one_or_none()
    except:
        raise HTTPException(status_code=404,detail="Not Found")    
    path = Path(video.file)
    file = path.open('rb')
    file_size = path.stat().st_size

    content_length = file_size
    status_code = 200
    headers = {}
    content_range = request.headers.get('range')

    if content_range is not None:
        content_range = content_range.strip().lower()
        content_ranges = content_range.split('=')[-1]
        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
        content_length = (range_end - range_start) + 1
        file = ranged(file, start=range_start, end=range_end + 1)
        status_code = 206
        headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

    return file, status_code, content_length, headers