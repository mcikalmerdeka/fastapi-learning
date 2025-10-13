"""
Authentication Routes
Handles user login and token generation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth  # Import from parent package
from ..database import get_db

from fastapi.security import OAuth2PasswordRequestForm  # Standard OAuth2 login form
from datetime import timedelta

from typing import Annotated

# Setup Router - groups related endpoints together
# tags=["auth"] organizes these endpoints in API docs
router = APIRouter(
    tags=["auth"],
)

# Type alias for database dependency injection
# This is a modern Python typing pattern: Annotated[Type, metadata]
# It means: "Session type with dependency injection of get_db()"
db_dependency = Annotated[Session, Depends(get_db)]

# ============ Login Endpoint ============
# POST /token - User login to get access token
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    db: db_dependency,  # Database session injected automatically
    form_data: OAuth2PasswordRequestForm = Depends()  # Standard OAuth2 form (username + password)
):
    """
    Authenticate user and return JWT access token
    
    Flow:
    1. Receive username and password from form
    2. Look up user in database
    3. Verify password matches hashed password
    4. Generate JWT token with expiration
    5. Return token to client
    """
    # Query database for user with matching username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # Check if user exists AND password is correct
    # verify_password() compares plain password with hashed password
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Set token expiration time (e.g., 30 minutes)
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create JWT token with username in payload ("sub" is standard JWT claim for subject)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Return token - client will include this in future requests as: Authorization: Bearer <token>
    return {"access_token": access_token, "token_type": "bearer"}