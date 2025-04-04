from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from database import Base


# SQLAlchemy model
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)


# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
