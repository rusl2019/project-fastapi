from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model for database
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

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        if db.query(UserDB).filter(UserDB.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        if db.query(UserDB).filter(UserDB.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        db_user = UserDB(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    finally:
        db.close()

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()

@app.get("/users/", response_model=list[UserResponse])
async def read_all_users():
    db = SessionLocal()
    try:
        users = db.query(UserDB).all()
        return users
    finally:
        db.close()

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate):
    db = SessionLocal()
    try:
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        if (db.query(UserDB)
            .filter(UserDB.username == user.username, UserDB.id != user_id)
            .first()):
            raise HTTPException(status_code=400, detail="Username already exists")
        if (db.query(UserDB)
            .filter(UserDB.email == user.email, UserDB.id != user_id)
            .first()):
            raise HTTPException(status_code=400, detail="Email already exists")
        
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    finally:
        db.close()

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    db = SessionLocal()
    try:
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)