# Architecture Deep Dive

## 🗄️ Database Schema

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ id (PK)         │
│ username        │◄─────┐
│ email           │      │
│ hashed_password │      │
│ created_at      │      │
└─────────────────┘      │
         │               │
         │ 1:N           │
         ▼               │
┌─────────────────┐      │
│     POSTS       │      │
├─────────────────┤      │
│ id (PK)         │      │
│ content         │      │
│ timestamp       │      │
│ owner_id (FK)   │──────┘
└─────────────────┘
         │
         │ 1:N
         ├──────────┬──────────┐
         ▼          ▼          ▼
    ┌──────┐   ┌──────────┐  ┌────────┐
    │LIKES │   │ RETWEETS │  │FOLLOWS │
    ├──────┤   ├──────────┤  ├────────┤
    │user  │   │ user_id  │  │follower│
    │post  │   │ post_id  │  │followee│
    └──────┘   │timestamp │  └────────┘
               └──────────┘

PK = Primary Key
FK = Foreign Key
```

## 🔄 Request Flow

### 1. Unauthenticated Request (e.g., Get Posts)
```
Client                FastAPI              Database
  │                      │                     │
  │─── GET /posts/ ─────►│                     │
  │                      │                     │
  │                      │── SELECT * FROM ───►│
  │                      │    posts...         │
  │                      │◄─── results ────────│
  │                      │                     │
  │                      │ (converts to        │
  │                      │  Pydantic schemas)  │
  │                      │                     │
  │◄─── JSON response ───│                     │
```

### 2. Authenticated Request (e.g., Create Post)
```
Client                FastAPI              Auth Module         Database
  │                      │                     │                  │
  │─ POST /posts/ ──────►│                     │                  │
  │  + Bearer token      │                     │                  │
  │  + JSON body         │                     │                  │
  │                      │                     │                  │
  │                      │─── verify token ───►│                  │
  │                      │                     │── query user ───►│
  │                      │◄─── User object ────│◄─────────────────│
  │                      │                     │                  │
  │                      │── INSERT post ──────────────────────────►│
  │                      │   (with user_id)    │                  │
  │                      │◄─── new post ──────────────────────────│
  │                      │                     │                  │
  │◄─── JSON response ───│                     │                  │
```

## 🔐 Authentication Flow

### Registration
```python
1. Client sends: {"username": "john", "email": "...", "password": "secret123"}
2. Backend: password "secret123" → bcrypt → "$2b$12$xY8z..." (hash)
3. Store: User(username="john", hashed_password="$2b$12$xY8z...")
```

### Login
```python
1. Client sends: {"username": "john", "password": "secret123"}
2. Backend: Lookup user by username
3. Compare: bcrypt.verify("secret123", "$2b$12$xY8z...") → True
4. Create JWT: {"sub": "john", "exp": 1234567890} + sign with SECRET_KEY
5. Return: {"access_token": "eyJhbG...", "token_type": "bearer"}
```

### Protected Endpoints
```python
1. Client sends: Authorization: Bearer eyJhbG...
2. Extract token from header (OAuth2PasswordBearer)
3. Decode JWT with SECRET_KEY
4. Extract username from "sub" claim
5. Query database for user
6. Inject User object into endpoint function
```

## 📊 Complex Query Breakdown

### `/posts/with_counts/` Endpoint

This demonstrates advanced SQL aggregation:

```sql
-- Step 1: Subquery for likes count
SELECT post_id, COUNT(user_id) as likes_count
FROM likes
GROUP BY post_id
-- Result: {1: 5, 2: 3, 3: 0, ...}

-- Step 2: Subquery for retweets count  
SELECT post_id, COUNT(user_id) as retweets_count
FROM retweets
GROUP BY post_id
-- Result: {1: 2, 2: 1, 3: 0, ...}

-- Step 3: Main query with joins
SELECT 
    posts.*,
    users.username,
    COALESCE(likes_subq.likes_count, 0),
    COALESCE(retweets_subq.retweets_count, 0)
FROM posts
JOIN users ON posts.owner_id = users.id
LEFT JOIN likes_subq ON posts.id = likes_subq.post_id
LEFT JOIN retweets_subq ON posts.id = retweets_subq.post_id
ORDER BY posts.timestamp DESC
```

**Why this is efficient:**
- Single database query instead of N+1 queries
- Database does aggregation (faster than Python loops)
- COALESCE handles missing data (posts with 0 likes)
- LEFT JOIN ensures all posts appear even with 0 engagement

## 🎯 Key Patterns

### 1. Dependency Injection
```python
# Instead of:
def create_post():
    db = SessionLocal()
    token = request.headers["Authorization"]
    user = authenticate(token, db)
    # ... do stuff
    db.close()

# FastAPI way:
def create_post(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # db and user automatically provided!
    # cleanup happens automatically!
```

### 2. Pydantic Validation
```python
# Request body automatically validated:
class PostCreate(BaseModel):
    content: str

@app.post("/posts/")
def create_post(post: PostCreate):  # ← validation happens here
    # If content is missing or not a string,
    # FastAPI returns 422 error automatically
```

### 3. SQLAlchemy Relationships
```python
# Instead of manual joins:
post = session.query(Post).filter(Post.id == 1).first()
user = session.query(User).filter(User.id == post.owner_id).first()

# With relationships:
post = session.query(Post).filter(Post.id == 1).first()
user = post.owner  # ← SQLAlchemy handles the join!
```

## 🔍 Data Science → Backend Translation

| Data Science Concept | Backend Equivalent | Notes |
|---------------------|-------------------|-------|
| pandas DataFrame | SQLAlchemy Model | Persistent table structure |
| df.to_sql() | db.add() + db.commit() | Write data |
| pd.read_sql() | db.query(Model).all() | Read data |
| df.merge() | SQLAlchemy join() | Combine tables |
| df.groupby().agg() | func.count() with group_by | Aggregation |
| Schema validation | Pydantic models | Data contracts |
| Jupyter notebook | FastAPI endpoint | Interactive → Production |

## 🚀 Performance Considerations

### Good Practices ✅
- Use relationships for 1:N queries (automatic join optimization)
- Pagination for large datasets (`limit`/`offset`)
- Indexes on foreign keys and frequently queried columns
- Single complex query over multiple simple queries
- Connection pooling (handled by SessionLocal)

### Bad Practices ❌
- N+1 queries (querying in a loop)
- Loading all records without pagination
- Not closing database sessions
- Exposing sensitive data (passwords) in API responses
- Not validating input data

## 📚 Further Reading

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Tutorial**: https://docs.sqlalchemy.org/en/20/tutorial/
- **JWT Introduction**: https://jwt.io/introduction
- **REST API Design**: RESTful Web APIs by Leonard Richardson
- **Security Best Practices**: OWASP Top 10

