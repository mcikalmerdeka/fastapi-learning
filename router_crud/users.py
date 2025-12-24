# routers/users.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Pydantic models
class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True

class UserCreate(BaseModel):
    name: str
    email: str

# Mock database
fake_users_db = {}
user_id_counter = 1

@router.get("/", response_model=List[User])
async def get_users():
    """Get all users"""
    return list(fake_users_db.values())

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID"""
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_users_db[user_id]

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user"""
    global user_id_counter
    new_user = User(id=user_id_counter, **user.dict())
    fake_users_db[user_id_counter] = new_user
    user_id_counter += 1
    return new_user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserCreate):
    """Update an existing user"""
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = User(id=user_id, **user.dict())
    fake_users_db[user_id] = updated_user
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user"""
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del fake_users_db[user_id]