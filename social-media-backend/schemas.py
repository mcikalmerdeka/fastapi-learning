# Pydantic schemas - these define the shape of data for API requests/responses
# Unlike SQLAlchemy models (database), these validate and serialize API data
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ============ User Schemas ============

# UserBase: Common fields shared by all user schemas
class UserBase(BaseModel):
    username: str
    email: str

# UserCreate: Schema for creating a new user (includes password)
# Used when registering - extends UserBase and adds password field
class UserCreate(UserBase):
    password: str  # Plain text password (will be hashed before storing)

# User: Schema for returning user data from API
# Used in API responses - includes fields from database
class User(UserBase):
    id: int  # Database ID
    created_at: datetime  # When account was created
    
    # Config tells Pydantic to work with SQLAlchemy ORM objects
    # from_attributes=True allows: User.model_validate(db_user_object)
    # Without this, you'd need to manually convert db objects to dicts
    class Config:
        from_attributes = True

# ============ Token Schemas ============

# Token: Returned when user logs in successfully
class Token(BaseModel):
    access_token: str  # JWT token string
    token_type: str    # Always "bearer" for JWT authentication

# TokenData: Data extracted from a decoded JWT token
class TokenData(BaseModel):
    username: Optional[str] = None  # Username stored in token payload

# ============ Post Schemas ============

# PostBase: Common fields for posts
class PostBase(BaseModel):
    content: str  # The post text content

# PostCreate: Schema for creating a new post
# Just uses PostBase as-is (no additional fields needed)
class PostCreate(PostBase):
    pass

# Post: Schema for returning a post from API
class Post(PostBase):
    id: int              # Database ID
    timestamp: datetime  # When post was created
    owner_id: int        # ID of user who created the post

# PostWithCounts: Extended post schema with engagement metrics
# Used in feed endpoints to show likes/retweets counts
class PostWithCounts(Post):
    likes_count: int      # Number of likes on this post
    retweets_count: int   # Number of retweets on this post
    owner_username: str   # Username of post owner (for display)
    
# PostUpdate: Schema for updating an existing post
class PostUpdate(BaseModel):
    content: str  # New content to replace old content

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy objects

# ============ Like Schemas ============
# (Optional - not heavily used in current API but available if needed)

class Like(BaseModel):
    user_id: int  # ID of user who liked
    post_id: int  # ID of post that was liked

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy objects

# ============ Retweet Schemas ============
# (Optional - not heavily used in current API but available if needed)

class Retweet(BaseModel):
    user_id: int       # ID of user who retweeted
    post_id: int       # ID of post that was retweeted
    timestamp: datetime  # When the retweet happened

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy objects