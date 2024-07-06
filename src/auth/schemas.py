from fastapi_users import schemas
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    avatar: str


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username:str
    role_id:int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    

class UserCreate(schemas.CreateUpdateDictModel):
    username:str
    email: str
    password: str
    # role_id:int
    # is_active: Optional[bool] = True
    # is_superuser: Optional[bool] = False
    # is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    pass
