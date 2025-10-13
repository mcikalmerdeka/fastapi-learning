# Social Media Backend API

A Twitter-like social media backend built with FastAPI, demonstrating production-grade patterns for REST APIs.

## 📚 What You'll Learn

This project demonstrates:
- **FastAPI fundamentals**: routing, dependency injection, request/response models
- **Database ORM**: SQLAlchemy models, relationships, and complex queries
- **Authentication**: JWT tokens, password hashing, protected endpoints
- **API design**: RESTful patterns, status codes, error handling
- **Data validation**: Pydantic schemas for request/response validation
- **SQL concepts**: joins, subqueries, aggregations, foreign keys

## 🏗️ Architecture Overview

```
social-media-backend/
├── main.py              # App entry point - FastAPI initialization
├── database.py          # Database connection & session management
├── models.py            # SQLAlchemy ORM models (database tables)
├── schemas.py           # Pydantic schemas (API request/response validation)
├── auth.py             # Authentication utilities (JWT, password hashing)
├── exceptions.py        # Centralized exception handlers
└── routes/             # API endpoints organized by feature
    ├── auth.py         # Login endpoint
    ├── users.py        # User registration, follow/unfollow
    └── posts.py        # Post CRUD, likes, retweets
```

## 🔑 Key Concepts Explained

### 1. **Models vs Schemas**
- **Models** (`models.py`): Define database structure - what goes in the DB
- **Schemas** (`schemas.py`): Define API data structure - what clients send/receive
- Example: User model has `hashed_password`, but User schema doesn't expose it

### 2. **Dependency Injection**
```python
db: Annotated[Session, Depends(get_db)]
current_user: User = Depends(auth.get_current_user)
```
FastAPI automatically:
- Creates database sessions for each request
- Validates JWT tokens and retrieves the current user
- Cleans up resources after the request

### 3. **Database Relationships**
- **One-to-Many**: One user has many posts (`User.posts` ← `Post.owner`)
- **Many-to-Many**: Users follow users (via `Follow` junction table)
- **Composite Keys**: Like table uses `(user_id, post_id)` to prevent duplicate likes

### 4. **Authentication Flow**
1. User registers: Password → bcrypt hash → stored in DB
2. User logs in: Check password → generate JWT token
3. Protected endpoints: Extract token → verify → get current user

## 📡 API Endpoints

### Authentication
- `POST /token` - Login (get JWT token)

### Users
- `POST /users/` - Register new user
- `POST /users/{id}/follow` - Follow user (requires auth)
- `POST /users/{id}/unfollow` - Unfollow user (requires auth)

### Posts
- `GET /posts/` - List posts (paginated)
- `GET /posts/with_counts/` - List posts with likes/retweets counts
- `POST /posts/` - Create post (requires auth)
- `PUT /posts/{id}` - Edit post (owner only, 10min window)
- `DELETE /posts/{id}` - Delete post (owner only)
- `POST /posts/{id}/like` - Like post (requires auth)
- `POST /posts/{id}/unlike` - Unlike post (requires auth)
- `POST /posts/{id}/retweet` - Retweet post (requires auth)
- `POST /posts/{id}/unretweet` - Unretweet post (requires auth)

## 🚀 Setup & Installation

```bash
# Install dependencies
pip install "fastapi[standard]"
pip install sqlalchemy
pip install "python-jose[cryptography]"  # For JWT token handling
pip install "passlib[bcrypt]"  # For password hashing

# Run the development server
fastapi dev main.py
# Or with uvicorn directly:
# uvicorn main:app --reload

# Access API docs at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## 🔍 Advanced Features to Study

### Complex SQL Query (`/posts/with_counts/`)
This endpoint demonstrates:
- **Subqueries**: Pre-aggregate likes/retweets counts
- **Joins**: Combine posts with users and count data
- **COALESCE**: Handle NULL values (posts with 0 engagement)
- **Efficiency**: Single query instead of N+1 queries

### Time-Based Authorization (`PUT /posts/{id}`)
Business logic: Posts can only be edited within 10 minutes of creation
- Shows how to implement time-based restrictions
- Demonstrates timezone-aware datetime handling

### Composite Primary Keys (Like/Retweet models)
- `(user_id, post_id)` as primary key
- Database-level prevention of duplicate likes
- Common pattern for many-to-many associations

## 📖 Learning Path

**For Data Science background → Backend:**

1. **Start with models.py**: Understand database structure (like pandas DataFrames but persistent)
2. **Then schemas.py**: See how data is validated (like data contracts)
3. **Check out database.py**: Learn about database connections (like connecting to SQL in notebooks)
4. **Study routes/posts.py**: See SQL queries (similar to pandas operations but in SQL)
5. **Finally auth.py**: Understand security basics

**Key differences from data work:**
- Data is persistent (survives restarts)
- Need to handle concurrent users
- Security is critical (authentication, authorization)
- API design matters (clients depend on your structure)

## 💡 Next Steps to Extend

- Add profile endpoints (get user info, posts by user)
- Implement feed endpoint (posts from followed users)
- Add comments on posts
- Implement search functionality
- Add pagination to more endpoints
- Set up database migrations (Alembic)
- Add unit tests (pytest)
- Deploy to production (Docker, cloud platforms)