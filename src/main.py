from fastapi import FastAPI,Depends
from api.api import video_router
from fastapi.staticfiles import StaticFiles
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate
from auth.base_config import current_user
from auth.models import User
from followers.api import follower_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:8000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
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

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8000,  reload=True,)