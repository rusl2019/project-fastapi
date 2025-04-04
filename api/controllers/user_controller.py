from fastapi import APIRouter, HTTPException, Header
from models.user import UserDB, UserCreate, UserResponse
from database import SessionLocal
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
VALID_API_KEY = os.getenv("API_KEY")

router = APIRouter()


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if not VALID_API_KEY:
        raise HTTPException(status_code=500, detail="API Key not configured")
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


@router.get("/users/", response_model=list[UserResponse])
async def read_all_users(x_api_key: str = Header(..., alias="X-API-Key")):
    await verify_api_key(x_api_key)
    db = SessionLocal()
    try:
        users = db.query(UserDB).all()
        return users
    finally:
        db.close()


@router.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate, x_api_key: str = Header(..., alias="X-API-Key")
):
    await verify_api_key(x_api_key)
    db = SessionLocal()
    try:
        if db.query(UserDB).filter(UserDB.username == user.username).first():
            raise HTTPException(
                status_code=400, detail="Username already exists"
            )
        if db.query(UserDB).filter(UserDB.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")

        db_user = UserDB(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    finally:
        db.close()


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int, x_api_key: str = Header(..., alias="X-API-Key")
):
    await verify_api_key(x_api_key)
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserCreate,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    await verify_api_key(x_api_key)
    db = SessionLocal()
    try:
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if (
            db.query(UserDB)
            .filter(UserDB.username == user.username, UserDB.id != user_id)
            .first()
        ):
            raise HTTPException(
                status_code=400, detail="Username already exists"
            )
        if (
            db.query(UserDB)
            .filter(UserDB.email == user.email, UserDB.id != user_id)
            .first()
        ):
            raise HTTPException(status_code=400, detail="Email already exists")

        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    finally:
        db.close()


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int, x_api_key: str = Header(..., alias="X-API-Key")
):
    await verify_api_key(x_api_key)
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
