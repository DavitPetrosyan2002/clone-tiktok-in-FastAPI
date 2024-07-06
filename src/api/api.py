from fastapi import UploadFile,File,APIRouter,Form,Depends,BackgroundTasks,HTTPException,Request
from fastapi.responses import HTMLResponse
from starlette.responses import StreamingResponse
from starlette.templating import Jinja2Templates
from uuid import uuid4
from typing import List
from .schemas import UploadVideo,GetVideo,User,video,GetlistVideo
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Insert,Select,Delete,func
from sqlalchemy import select
from sqlalchemy.orm import query
from .models import Video,UserLike
from auth.models import User
from .services import save_video,open_file
from auth.base_config import current_user

video_router=APIRouter(tags=['video'])
templates=Jinja2Templates(directory="templates")


@video_router.post("/upload_file")
async def upload_file(background_tasks:BackgroundTasks,title:str=Form(...),
    description:str=Form(...),file:UploadFile=File(...),
    session:AsyncSession=Depends(get_async_session),
    user:User=Depends(current_user)):
    print(user)
    # user = (await session.execute(select(User).limit(1))).scalar_one_or_none()
    return await save_video(user.id,file,title,description,background_tasks,session)
    




# @video_router.get("/video/{video_pk}")
# async def get_video(video_pk:int,session:AsyncSession=Depends(get_async_session)):
#     video = (await session.execute(select(Video).where(Video.id==video_pk))).scalar_one_or_none()
#     file_like=open(video.file,mode="rb")
#     return StreamingResponse(file_like,media_type="video/mp4")

@video_router.get("/user/{user_pk}")
async def get_list_video(user_pk:int,session:AsyncSession=Depends(get_async_session)):
    query=Select(Video).where(Video.user_id==user_pk)
    print(query)
    result = await session.execute(query)
    return result.mappings().all()        



@video_router.get("/index/{video_pk}")
async def get_video(request:Request,video_pk:int):
    return templates.TemplateResponse("index.html",{"request":request,"path":video_pk})




@video_router.get("/video/{video_pk}")
async def get_streaming_video(request: Request, video_pk: int,session:AsyncSession=Depends(get_async_session)) -> StreamingResponse:
    file, status_code, content_length, headers = await open_file(request, video_pk,session)
    response = StreamingResponse(
        file,
        media_type='video/mp4',
        status_code=status_code,
    )

    response.headers.update({
        'Accept-Ranges': 'bytes',
        'Content-Length': str(content_length),
        **headers,
    })
    return response

@video_router.post("/likevideo/{video_pk}",status_code=201)
async def add_like(video_pk:int,user:User=Depends(current_user),session:AsyncSession=Depends(get_async_session)):
    video = (await session.execute(select(Video).where(Video.id==video_pk))).scalar_one_or_none()
    if video:
        user_like=(await session.execute(Select(UserLike).where((UserLike.video_id==video_pk)&(UserLike.user_id==user.id)))).scalar_one_or_none()
        if user_like:
            await session.execute(Delete(UserLike).where((UserLike.video_id==video_pk)&(UserLike.user_id==user.id)))
            await session.commit()
        else:    
            await session.execute(Insert(UserLike).values(user_id=user.id,video_id=video_pk))
            await session.commit()
    else:
        raise HTTPException(status_code=401,detail="video not faound")        
    like_count = (await session.execute(
        select(func.count(UserLike.user_id)).where(UserLike.video_id == video_pk)
    )).scalar()
    return {"status_code": 201, "like_count": like_count}    
    

@video_router.get("/likecount/{video_pk}",status_code=201)
async def like_count(video_pk:int,session:AsyncSession=Depends(get_async_session)):
    like_count = (await session.execute(
        select(func.count(UserLike.user_id)).where(UserLike.video_id == video_pk)
    )).scalar()
    return {"status_code": 201, "like_count": like_count} 