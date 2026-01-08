from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from auth import create_token, get_current_user
from rate_limit import rate_limit

router = APIRouter(prefix="/users", tags=["users"])

# Get all users
@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Create a new user
@router.post("/", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(email=payload.email, password=payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"token": create_token(user.id)}


# Get current logged-in user's profile
@router.get("/me")
def get_my_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }


# Limited endpoint for rate limiting
@router.get("/limited")
def limited_endpoint(client_id: str):
    rate_limit(client_id)
    return {"message": "OK"}


# Get a user by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Delete a user by ID
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404)

    db.delete(user)
    db.commit()
    return
