"""
Main FastAPI Application Entry Point
This file initializes the FastAPI app and connects all the routes
"""
from fastapi import FastAPI
import uvicorn

from .database import engine  # Database engine for SQLAlchemy
from .models import Base       # Base class for all database models
from .routes import users, posts, auth  # Import route modules

# Create all database tables based on the models (User, Post, Like, Retweet)
# This runs once when the app starts and creates tables if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI()

# Include routers - this connects all the endpoint handlers to the app
# Each router handles different parts of the API:
app.include_router(users.router)  # /users endpoints (register, follow, unfollow)
app.include_router(auth.router)   # /token endpoint (login)
app.include_router(posts.router)  # /posts endpoints (create, read, like, retweet, etc.)

# Run the app with uvicorn server (ASGI server for async Python apps)
# This only runs if you execute this file directly: python main.py
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all network interfaces (allows external access)
        port=8000         # Run on port 8000
    )