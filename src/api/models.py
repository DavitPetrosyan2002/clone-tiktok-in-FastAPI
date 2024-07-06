from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from database import Base,metadata





class Video(Base):
    __tablename__="video"
    id = Column(Integer, primary_key=True,autoincrement=True)
    title = Column(String, nullable=False) 
    description =Column(String,nullable=False)
    file = Column(String,nullable=False) 
    create_at = Column(TIMESTAMP, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))


class UserLike(Base):
    __tablename__="userlike"
    id=Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    video_id=Column(Integer,ForeignKey('video.id'))