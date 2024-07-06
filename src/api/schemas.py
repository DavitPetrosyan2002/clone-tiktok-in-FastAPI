from pydantic import BaseModel
from typing import List
from datetime import datetime

class User(BaseModel):
    id:int
    username:str


class UploadVideo(BaseModel):
    title:str
    description:str
    

class GetlistVideo(BaseModel):
    id:int
    title:str
    description:str 


class GetVideo(GetlistVideo):
    user: User
    

class video(BaseModel):
    id:int
    title:str
    description:str
    file:str
    create_at:datetime
    user_id:int
    