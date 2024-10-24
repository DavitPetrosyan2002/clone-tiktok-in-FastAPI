from fastapi import UploadFile,File,APIRouter,Form,Depends,BackgroundTasks,HTTPException,Request,Query
from fastapi.responses import HTMLResponse
from starlette.responses import StreamingResponse
from starlette.templating import Jinja2Templates
from uuid import uuid4
import random
from typing import List
from .schemas import UploadVideo,GetVideo,User,video,GetlistVideo,video_comments
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Insert,Select,Delete,func,desc
from sqlalchemy import select
from sqlalchemy.orm import query
from .models import Video,UserLike,Comment
from auth.models import User
from .services import save_video,open_file
from auth.base_config import current_user

video_router=APIRouter(tags=['video'])
templates=Jinja2Templates(directory="templates")


@video_router.post("/upload_file")
async def upload_file(request:Request,background_tasks:BackgroundTasks,title:str=Form(...),
    description:str=Form(...),file:UploadFile=File(...),
    session:AsyncSession=Depends(get_async_session),
    user:User=Depends(current_user)):
    print(user)
    # user = (await session.execute(select(User).limit(1))).scalar_one_or_none()
    return await save_video(request,user.id,file,title,description,background_tasks,session)
    
@video_router.get("/upload_page")
async def upload_page(request:Request):
    return templates.TemplateResponse("uploadform.html",{"request":request,"title":"Загрузка видео"})



# @video_router.get("/video/{video_pk}")
# async def get_video(video_pk:int,session:AsyncSession=Depends(get_async_session)):
#     video = (await session.execute(select(Video).where(Video.id==video_pk))).scalar_one_or_none()
#     file_like=open(video.file,mode="rb")
#     return StreamingResponse(file_like,media_type="video/mp4")

@video_router.get("/user_video")
async def get_list_video(page: int = Query(1, ge=1),user: User = Depends(current_user),session:AsyncSession=Depends(get_async_session)):
    per_page = 3
    start = (page - 1) * per_page
    query=Select(Video).where(Video.user_id==user.id).limit(per_page).offset(start)
    result = await session.execute(query)
    results = result.mappings().all() 
    return{"results":results,"hasMore":len(results)==per_page}       



# @video_router.get("/index/{video_pk}")
# async def get_video(request:Request,video_pk:int,session:AsyncSession=Depends(get_async_session)):
#     video = (await session.execute(select(Video).where(Video.id==video_pk))).scalar_one_or_none()
#     video_count = (await session.execute(
#         select(func.count(Video.id))
#     )).scalar()
#     if video:
#         return templates.TemplateResponse("index.html",{"request":request,"path":video_pk,"title":"video"})
#     random_number = random.choice([num for num in range(video_count) if num != video_pk])
#     return templates.TemplateResponse("index.html",{"request":request,"path":random_number,"title":"video"})
    

@video_router.get("/index")
async def test_checkpoint(page: int = Query(1, ge=1), session: AsyncSession = Depends(get_async_session)):
    per_page = 3
    start = (page - 1) * per_page
    videos = (
        await session.execute(
            select(User, Video)
            .join(Video, Video.user_id == User.id)
            .order_by(Video.create_at)
            .limit(per_page)
            .offset(start)
        )
    ).all()
    
    return {"result": [{"user": user.username, "video": video} for user, video in videos],"hasMore":len(videos)==per_page}


@video_router.post("/add_comments")
async def add_comments(comm:video_comments,session:AsyncSession = Depends(get_async_session)):
    await session.execute(Insert(Comment).values(dict(comm)))
    await session.commit()
    return{"result":comm}

@video_router.get("/comments")
async def comments(video_id:int=Query(1,ge=1),session:AsyncSession=Depends(get_async_session)):
    comments = (
        await session.execute(
            select(Comment, User)
            .join(User, User.id == Comment.user_id)
            .where(Comment.video_id==video_id)
        )
    ).all()
    return {"result": [{"comm": com.text, "user": user.username} for com, user in comments]}


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

@video_router.get("/video_changer")
async def video_changer(request:Request,user:User=Depends(current_user)):
    return templates.TemplateResponse("video_changer.html",{"request":request,"user_id":user.id,"username":user.username})