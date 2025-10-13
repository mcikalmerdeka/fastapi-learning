"""
User Routes
Handles user registration, follow/unfollow functionality
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from .. import models, schemas, auth
from ..database import get_db
from ..exceptions import (
    raise_not_found_exception,
    raise_bad_request_exception,
    raise_conflict_exception,
)

# Setup Router with prefix - all endpoints here start with /users
router = APIRouter(
    prefix="/users",  # All routes in this router will be prefixed with /users
    tags=["users"],   # Groups these endpoints in API docs
)

# Type alias for database dependency injection
db_dependency = Annotated[Session, Depends(get_db)]

# ============ User Registration Endpoint ============
# POST /users/ - Create a new user account
@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: db_dependency):
    """
    Register a new user
    
    Flow:
    1. Receive username, email, and password from request
    2. Check if username already exists (must be unique)
    3. Hash the password (never store plain text!)
    4. Create new user in database
    5. Return the created user info (without password)
    """
    # Check if username is already taken
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise_conflict_exception("Username already registered")
    
    # Hash the password using bcrypt (one-way encryption)
    hashed_password = auth.get_password_hash(user.password)
    
    # Create new User instance
    new_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password
    )
    
    # Add to database session (staging area)
    db.add(new_user)
    
    # Commit transaction (actually write to database)
    db.commit()
    
    # Refresh to get the auto-generated ID and created_at timestamp
    db.refresh(new_user)
    
    # Return user object (password not included due to response_model)
    return new_user

# ============ Follow User Endpoint ============
# POST /users/{user_id}/follow - Follow another user
@router.post("/{user_id}/follow", status_code=204)
def follow_user(
    user_id: int,  # ID from URL path parameter
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),  # Authenticated user (from JWT)
):
    """
    Follow another user
    
    Requires authentication (JWT token in Authorization header)
    
    Flow:
    1. Extract user_id from URL (who to follow)
    2. Verify that user exists
    3. Check business rules (can't follow yourself, can't follow twice)
    4. Add to following relationship
    """
    # Find the user to follow in database
    user_to_follow = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_follow:
        raise_not_found_exception("User not found")
    
    # Business logic validation: can't follow yourself
    if user_to_follow == current_user:
        raise_bad_request_exception("Cannot follow yourself")
    
    # Check if already following (prevent duplicate follows)
    if user_to_follow in current_user.following:
        raise_bad_request_exception("Already following this user")
    
    # Add to following list (SQLAlchemy handles the Follow junction table automatically)
    current_user.following.append(user_to_follow)
    
    # Save changes to database
    db.commit()
    
    # 204 No Content - success but no response body needed
    return

# ============ Unfollow User Endpoint ============
# POST /users/{user_id}/unfollow - Unfollow a user
@router.post("/{user_id}/unfollow", status_code=204)
def unfollow_user(
    user_id: int,  # ID from URL path parameter
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user),  # Authenticated user
):
    """
    Unfollow a user you're currently following
    
    Requires authentication
    
    Similar to follow but removes the relationship
    """
    # Find the user to unfollow
    user_to_unfollow = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_unfollow:
        raise_not_found_exception("User not found")
    
    # Validation: can't unfollow yourself
    if user_to_unfollow == current_user:
        raise_bad_request_exception("Cannot unfollow yourself")
    
    # Check if actually following this user
    if user_to_unfollow not in current_user.following:
        raise_bad_request_exception("Not following this user")
    
    # Remove from following list (removes entry from Follow junction table)
    current_user.following.remove(user_to_unfollow)
    
    # Save changes
    db.commit()
    
    # 204 No Content - success
    return