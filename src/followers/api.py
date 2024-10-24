from fastapi import APIRouter,Depends,HTTPException,Request,Query
from fastapi.responses import JSONResponse
from starlette.templating import Jinja2Templates
from auth.base_config import current_user
from sqlalchemy import Insert,Select,Join,Delete,select
from typing import List
from . import schemas
from auth.models import User
from .models import Followers
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from pydantic import BaseModel
from typing import List, Optional
from .services import serialize_user


follower_router=APIRouter(prefix="/followers",tags=['followers'])
templates=Jinja2Templates(directory="templates")

@follower_router.post('/',response_model=schemas.FollowerCreate)
async def add_follower(schema:schemas.FollowerCreate,
                       subscriber:User=Depends(current_user),
                       session:AsyncSession=Depends(get_async_session)):
    user = (await session.execute(Select(User).where(User.username==schema.user))).scalar_one_or_none()
    if user:
        stms=Insert(Followers).values(subscriber=subscriber.id,user=user.id) 
        await session.execute(stms)
        await session.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")     
    return JSONResponse({"success": True, "user": schema.user})



# @follower_router.get('/me')
# async def my_list_follower(user:User=Depends(current_user),session:AsyncSession=Depends(get_async_session)):
#     try:
#         result = await session.execute(
#             Select(User.username).join(Followers, Followers.subscriber == User.id).where(Followers.user == user.id)
#         )
#         followers = result.scalars().all()
#         return followers
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @follower_router.get('/following')
# async def my_list_following(user:User=Depends(current_user),session:AsyncSession=Depends(get_async_session)):
#     try:
#         result = await session.execute(
#             Select(User.username).join(Followers, Followers.user == User.id).where(Followers.subscriber == user.id)
#         )
#         followers = result.scalars().all()
#         return followers
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

@follower_router.delete('/delete/{username}')
async def delete_follower(username:str,user:User=Depends(current_user),session:AsyncSession=Depends(get_async_session)):
    delete_user = (await session.execute(Select(User).where(User.username==username))).scalar_one_or_none()
    if delete_user:
        await session.execute(Delete(Followers).where((Followers.subscriber==user.id) & (Followers.user==delete_user.id)))
        await session.commit()
        return{"success":True}
    else:
        raise HTTPException(status_code=401,detail="User not found")
         

@follower_router.get('/search_user/{username}')
async def search_user(username: str, session: AsyncSession = Depends(get_async_session), subscriber: User = Depends(current_user)):
    exact_user = (await session.execute(Select(User).where(User.username == username))).scalar_one_or_none()
    if exact_user:
        followed = (await session.execute(Select(Followers).where((Followers.user == exact_user.id) & (Followers.subscriber == subscriber.id)))).scalar_one_or_none()
        
        return {
            "users": [{
                "username": exact_user.username,
                "follow": followed is not None  
            }]
        }
    stmt = Select(User).where(User.username.ilike(f'%{username}%'))
    results = (await session.execute(stmt)).scalars().all()
    
    

    users_data = []
    for user in results:
        followed = (await session.execute(Select(Followers).where((Followers.user == user.id) & (Followers.subscriber == subscriber.id)))).scalar_one_or_none()
        user_data = {
            "username": user.username,
            "follow": followed is not None  
        }
        users_data.append(user_data)

    return {"users": users_data}



@follower_router.get('/followers_search') 
async def followers_page (request:Request):
    return templates.TemplateResponse('usersearch.html',{"request":request,"title":"Поиск пользователей"})

@follower_router.get('/subscribers')
async def subscriber_page(request:Request):
    return templates.TemplateResponse('subscribers.html',{"request":request,"title":"Список подписчиков"})

@follower_router.get('/profile')
async def profile_user(request:Request,user:User=Depends(current_user)):
    return templates.TemplateResponse('profileuser.html',{"request":request,"user":user.username})

@follower_router.get('/following')
async def following_page(request:Request):
    return templates.TemplateResponse('following.html',{"request":request,"title":"Список подписки"})

@follower_router.get('/register')
async def register_user(request:Request):
    return templates.TemplateResponse('register.html',{"request":request,"title":"страница  регистрация"})

@follower_router.get('/auth')
async def auth_user(request:Request):
    return templates.TemplateResponse('auth.html',{"request":request,"title":"страница  афторизация"})


@follower_router.get("/get_subscribers")
async def get_subscribers(
    user:User=Depends(current_user),
    page: int = Query(1, ge=1), 
    session: AsyncSession = Depends(get_async_session),
    
) -> dict:
    try:
       
        per_page = 3
        start = (page - 1) * per_page
        # query = select(User).offset(start).limit(per_page)
        query = (
            Select(User)
            .join(Followers, Followers.subscriber == User.id)
            .where(Followers.user == user.id)
            .limit(per_page)
            .offset(start)
        )
        result = await session.execute(query)
        subscribers = result.scalars().all()
        
        has_more = len(subscribers) == per_page

        data = {
            'subscribers': [serialize_user(subscriber) for subscriber in subscribers],
            'hasMore': has_more
        }
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@follower_router.get("/get_following")
async def get_subscribers(
    user:User=Depends(current_user),
    page: int = Query(1, ge=1), 
    session: AsyncSession = Depends(get_async_session),
    
) -> dict:
    try:
        per_page = 3
        start = (page - 1) * per_page

        
        # query = select(User).offset(start).limit(per_page)
        query = (
            Select(User)
            .join(Followers, Followers.user == User.id)
            .where(Followers.subscriber == user.id)
            .limit(per_page)
            .offset(start)
        )

        result = await session.execute(query)
        following = result.scalars().all()
        
        has_more = len(following) == per_page

        data = {
            'subscribers': [serialize_user(follow) for follow in following],
            'hasMore': has_more
        }
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    