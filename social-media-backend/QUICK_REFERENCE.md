# Quick Reference Guide

## 🚀 Common Commands

```bash
# Start development server
fastapi dev main.py

# Start production server
uvicorn main:app --host 0.0.0.0 --port 8000

# View API documentation
# http://localhost:8000/docs (Swagger UI - interactive)
# http://localhost:8000/redoc (ReDoc - readable)
```

## 🔧 Testing with curl/httpie

### Register a User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'
```

### Login (Get Token)
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"

# Response: {"access_token": "eyJhbG...", "token_type": "bearer"}
# Save the token for authenticated requests!
```

### Create a Post (Authenticated)
```bash
TOKEN="your-token-here"

curl -X POST "http://localhost:8000/posts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, world! This is my first post."}'
```

### Get All Posts
```bash
curl "http://localhost:8000/posts/"

# With pagination
curl "http://localhost:8000/posts/?skip=0&limit=10"
```

### Like a Post
```bash
curl -X POST "http://localhost:8000/posts/1/like" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Posts with Counts
```bash
curl "http://localhost:8000/posts/with_counts/"
```

## 🐍 Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/users/", json={
    "username": "bob",
    "email": "bob@example.com",
    "password": "password123"
})
print(f"Registered: {response.json()}")

# Login
response = requests.post(f"{BASE_URL}/token", data={
    "username": "bob",
    "password": "password123"
})
token = response.json()["access_token"]
print(f"Token: {token}")

# Create post (authenticated)
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/posts/",
    headers=headers,
    json={"content": "My first post via API!"}
)
post = response.json()
print(f"Created post: {post}")

# Like the post
response = requests.post(
    f"{BASE_URL}/posts/{post['id']}/like",
    headers=headers
)
print(f"Liked post {post['id']}")

# Get all posts with counts
response = requests.get(f"{BASE_URL}/posts/with_counts/")
posts = response.json()
for p in posts:
    print(f"Post {p['id']} by {p['owner_username']}: {p['content']}")
    print(f"  Likes: {p['likes_count']}, Retweets: {p['retweets_count']}")
```

## 📝 Code Patterns

### Creating a New Endpoint

```python
# 1. Add route in routes/posts.py (or appropriate file)
@router.get("/posts/{post_id}")
def get_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise_not_found_exception("Post not found")
    return post

# 2. If you need authentication, add dependency:
@router.get("/posts/{post_id}")
def get_post(
    post_id: int, 
    db: db_dependency,
    current_user: models.User = Depends(auth.get_current_user)  # ← Add this
):
    # Now you have access to current_user
    ...

# 3. Create Pydantic schema if needed (in schemas.py)
class PostDetail(BaseModel):
    id: int
    content: str
    owner_username: str
    likes_count: int
    
    class Config:
        from_attributes = True
```

### Database Query Examples

```python
# Get all records
posts = db.query(models.Post).all()

# Filter
posts = db.query(models.Post).filter(models.Post.owner_id == 1).all()

# Filter with multiple conditions
posts = db.query(models.Post).filter(
    models.Post.owner_id == 1,
    models.Post.id > 10
).all()

# Get first result
post = db.query(models.Post).filter(models.Post.id == 1).first()

# Order by
posts = db.query(models.Post).order_by(models.Post.timestamp.desc()).all()

# Pagination
posts = db.query(models.Post).offset(10).limit(5).all()  # Skip 10, get 5

# Count
count = db.query(models.Post).count()

# Join
posts = db.query(models.Post).join(models.User).all()

# Filter on joined table
posts = (
    db.query(models.Post)
    .join(models.User)
    .filter(models.User.username == "alice")
    .all()
)
```

### Creating Database Records

```python
# Create
new_post = models.Post(content="Hello", owner_id=1)
db.add(new_post)
db.commit()
db.refresh(new_post)  # Get auto-generated fields (id, timestamp)

# Update
post = db.query(models.Post).filter(models.Post.id == 1).first()
post.content = "Updated content"
db.commit()

# Delete
post = db.query(models.Post).filter(models.Post.id == 1).first()
db.delete(post)
db.commit()
```

## 🔍 Debugging Tips

### Enable SQL Logging
```python
# In database.py
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=True  # ← Add this to see SQL queries in console
)
```

### Check Current User
```python
@router.get("/debug/me")
def debug_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
```

### Inspect Database
```bash
# SQLite
sqlite3 microblog.db
.tables
.schema users
SELECT * FROM users;
.quit
```

## ⚠️ Common Errors

### "Could not validate credentials"
- Token expired (default: 30 minutes)
- Token signature invalid
- User in token doesn't exist
- **Solution**: Login again to get new token

### "Username already registered"
- Tried to register with existing username
- **Solution**: Use different username or login

### "Post not found"
- Post doesn't exist
- User trying to delete/edit someone else's post
- **Solution**: Check post ID and ownership

### "Already liked/retweeted"
- Tried to like/retweet the same post twice
- **Solution**: Unlike/unretweet first, or check before action

### Database locked
- Multiple processes accessing SQLite simultaneously
- **Solution**: Use one process or switch to PostgreSQL for production

## 🎓 Learning Exercises

1. **Add a comment system**: Posts can have comments
   - Create Comment model
   - Add relationships
   - Create CRUD endpoints

2. **Implement user profiles**: GET /users/{id}
   - Return user info with post count
   - List user's posts

3. **Add a feed endpoint**: GET /feed
   - Return posts from users you follow
   - Order by timestamp

4. **Implement search**: GET /posts/search?q=keyword
   - Search in post content
   - Return matching posts

5. **Add hashtags**: #topic support
   - Extract hashtags from post content
   - Create Hashtag model and relationships
   - Search by hashtag

6. **Rate limiting**: Prevent spam
   - Limit posts per user per hour
   - Use Redis or in-memory counter

7. **Pagination improvement**: Cursor-based
   - Instead of offset/limit
   - Better performance for large datasets

## 📚 Resources

- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/en/20/orm/
- JWT Debugger: https://jwt.io/
- HTTP Status Codes: https://httpstatuses.com/
- REST Best Practices: https://restfulapi.net/

