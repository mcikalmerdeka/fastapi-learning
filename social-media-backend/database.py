# SQLAlchemy imports for database setup
from sqlalchemy import create_engine  # Creates connection to database
from sqlalchemy.ext.declarative import declarative_base  # Base class for models
from sqlalchemy.orm import sessionmaker  # Factory for creating database sessions

# Database connection string - using SQLite (a file-based database)
# The .db file will be created in the current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./microblog.db"

# Create the database engine - the core interface to the database
# check_same_thread=False allows SQLite to work with FastAPI's async nature
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal is a factory that creates database sessions
# autocommit=False: Changes aren't automatically saved (we control when to commit)
# autoflush=False: Changes aren't automatically sent to DB before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our database models (User, Post, etc.) will inherit from
# This allows SQLAlchemy to track our models and create tables
Base = declarative_base()

# Dependency function that provides a database session to route handlers
# This is used with FastAPI's Depends() to inject DB sessions into endpoints
def get_db():
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Provide the session to the endpoint
    finally:
        db.close()  # Always close the session when done (cleanup)