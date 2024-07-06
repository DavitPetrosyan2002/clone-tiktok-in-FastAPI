from pydantic import BaseModel
from typing import List
from auth.schemas import User

class FollowerCreate(BaseModel):
    user:str


class FollowerList(FollowerCreate):
    user:int
    subscriber:User