from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from database import Base,metadata





class Followers(Base):
    __tablename__="followers"
    id=Column(Integer,primary_key=True)
    user = Column(Integer, ForeignKey('user.id'))
    subscriber=Column(Integer,ForeignKey('user.id'))
