from fastapi import APIRouter,Depends,HTTPException
from auth.base_config import current_user
from sqlalchemy import Insert,Select,Join,Delete
from typing import List
from . import schemas
from auth.models import User
from .models import Followers
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session

follower_router=APIRouter(prefix="/followers",tags=['followers'])

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
    return schema


@follower_router.get('/me')
async def my_list_follower(user:User=Depends(current_user),session:AsyncSession=Depends(get_async_session)):
    try:
        result = await session.execute(
            Select(User.username).join(Followers, Followers.subscriber == User.id).where(Followers.user == user.id)
        )
        followers = result.scalars().all()
        return followers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@follower_router.get('/following')
async def my_list_following(user:User=Depends(current_user),session:AsyncSession=Depends(get_async_session)):
    try:
        result = await session.execute(
            Select(User.username).join(Followers, Followers.user == User.id).where(Followers.subscriber == user.id)
        )
        followers = result.scalars().all()
        return followers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@follower_router.delete('/delete/{username}')
async def delete_follower(username:str,user:User=Depends(current_user),session:AsyncSession=Depends(get_async_session)):
    delete_user = (await session.execute(Select(User).where(User.username==username))).scalar_one_or_none()
    if delete_user:
        await session.execute(Delete(Followers).where((Followers.subscriber==user.id) & (Followers.user==delete_user.id)))
        await session.commit()
        return{"status":"usere sucsesfuly deleted"}
    else:
        raise HTTPException(status_code=401,detail="User not found")
         