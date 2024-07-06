from fastapi import FastAPI,Depends
from api.api import video_router
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate
from auth.base_config import current_user
from auth.models import User
from followers.api import follower_router
app=FastAPI()



app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

@app.get("/protected_route")
def protected_route(user:User=Depends(current_user)):
    return f"hello {user.username}"


app.include_router(video_router)
app.include_router(follower_router)