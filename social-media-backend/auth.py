"""
Authentication Utilities
Handles password hashing, JWT token creation/validation, and user authentication
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # python-jose library for JWT
from passlib.context import CryptContext  # For password hashing
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

# ============ Configuration ============

# Secret key for signing JWT tokens (in production, use environment variable!)
SECRET_KEY = "your-secret-key-keep-this-secure-in-production"  # Change this!
ALGORITHM = "HS256"  # HMAC with SHA-256
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token valid for 30 minutes

# ============ Password Hashing ============

# CryptContext handles password hashing with bcrypt
# bcrypt is a one-way hash - you can't decrypt it
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password
    
    Args:
        plain_password: The password user entered (plain text)
        hashed_password: The hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password for storing in database
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string (safe to store)
    """
    return pwd_context.hash(password)

# ============ JWT Token Management ============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of claims to encode in token (e.g., {"sub": "username"})
        expires_delta: How long until token expires (default: 15 minutes)
    
    Returns:
        Encoded JWT token string
    
    JWT Structure:
    - Header: Algorithm and token type
    - Payload: Data (claims) - username, expiration, etc.
    - Signature: Ensures token hasn't been tampered with
    """
    # Copy data to avoid modifying original
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Add expiration to payload
    to_encode.update({"exp": expire})
    
    # Encode and sign the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ============ OAuth2 Authentication Scheme ============

# OAuth2PasswordBearer extracts token from Authorization header
# tokenUrl="/token" tells FastAPI where to get tokens (for API docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(
    token: str = Depends(oauth2_scheme),  # Extract token from header
    db: Session = Depends(get_db)  # Get database session
) -> models.User:
    """
    Get the current authenticated user from JWT token
    
    This is used as a dependency in protected endpoints:
    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        ...
    
    Args:
        token: JWT token from Authorization header (extracted automatically)
        db: Database session (injected automatically)
    
    Returns:
        User object from database
    
    Raises:
        HTTPException: If token is invalid or user not found
    
    Flow:
    1. Extract token from "Authorization: Bearer <token>" header
    2. Decode and verify JWT token
    3. Extract username from token payload
    4. Look up user in database
    5. Return user object
    """
    # Exception to raise if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # Tell client to use Bearer token
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract username from payload (stored in "sub" claim)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Create TokenData object for validation
        token_data = schemas.TokenData(username=username)
        
    except JWTError:
        # Token is invalid (expired, wrong signature, malformed, etc.)
        raise credentials_exception
    
    # Look up user in database
    user = db.query(models.User).filter(
        models.User.username == token_data.username
    ).first()
    
    if user is None:
        # User in token doesn't exist in database (maybe deleted)
        raise credentials_exception
    
    # Return authenticated user
    return user
