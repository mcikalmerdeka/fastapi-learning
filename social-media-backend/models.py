# SQLAlchemy imports for defining database table structures
from sqlalchemy import (
    Column,      # Defines a column in a table
    Integer,     # Integer data type
    String,      # String/text data type
    DateTime,    # Date and time data type
    ForeignKey,  # Creates relationships between tables
    Table        # Defines a table
)
from sqlalchemy.orm import relationship  # Defines relationships between models
from .database import Base  # Base class all models inherit from
from datetime import datetime, timezone

# Association table for many-to-many relationship (User follows User)
# This is a junction table - it doesn't need its own model class
# It just connects users who follow each other
Follow = Table(
    "follows",  # Table name in the database
    Base.metadata,  # Links to our Base metadata
    # follower_id: the user who is following someone
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    # followee_id: the user who is being followed
    Column("followee_id", Integer, ForeignKey("users.id"), primary_key=True),
)

# User Model - represents the users table in the database
class User(Base):
    __tablename__ = "users"  # Actual table name in the database

    # Primary key - unique identifier for each user
    id = Column(Integer, primary_key=True, index=True)
    
    # Username - unique, indexed for fast lookups, cannot be null
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Email - unique, indexed, cannot be null
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Password is hashed (encrypted) before storing - never store plain text passwords!
    hashed_password = Column(String(255), nullable=False)
    
    # Timestamp of when the user account was created
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationship: One user can have many posts
    # back_populates creates a two-way relationship with Post.owner
    posts = relationship("Post", back_populates="owner")

    # Self-referential many-to-many relationship for follow system
    # secondary=Follow: uses the Follow table to connect users
    # primaryjoin: when this user is being followed (they are the followee)
    # secondaryjoin: when this user is following others (they are the follower)
    # backref="following": creates a reverse relationship automatically
    followers = relationship(
        "User",
        secondary=Follow,
        primaryjoin=id == Follow.c.followee_id,
        secondaryjoin=id == Follow.c.follower_id,
        backref="following",
    )

# Post Model - represents posts/tweets in the database
class Post(Base):
    __tablename__ = "posts"  # Table name in database

    # Primary key - unique identifier for each post
    id = Column(Integer, primary_key=True, index=True)
    
    # Post content - limited to 280 characters (like Twitter), cannot be null
    content = Column(String(280), nullable=False)
    
    # When the post was created
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    
    # Foreign key - links this post to the user who created it
    # References the id column in the users table
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship: each post belongs to one user (the owner)
    owner = relationship("User", back_populates="posts")
    
    # Relationship: one post can have many likes
    likes = relationship("Like", back_populates="post")
    
    # Relationship: one post can have many retweets
    retweets = relationship("Retweet", back_populates="post")

# Like Model - tracks which users liked which posts
class Like(Base):
    __tablename__ = "likes"

    # Composite primary key (combination of user_id and post_id must be unique)
    # This ensures a user can only like a post once
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)

    # Relationships to access the user and post objects
    user = relationship("User")
    post = relationship("Post", back_populates="likes")

# Retweet Model - tracks which users retweeted which posts
class Retweet(Base):
    __tablename__ = "retweets"

    # Composite primary key - ensures a user can only retweet a post once
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    
    # Track when the retweet happened (useful for timeline features)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships to access the user and post objects
    user = relationship("User")
    post = relationship("Post", back_populates="retweets")