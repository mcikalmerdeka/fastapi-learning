# From Data Science to Backend Development

A guide for transitioning from data analysis to backend API development.

## 🔄 Mental Model Shift

### Data Science Workflow
```python
# 1. Load data
df = pd.read_csv("users.csv")

# 2. Transform
df['age_group'] = df['age'].apply(lambda x: 'adult' if x >= 18 else 'minor')

# 3. Analyze
avg_age = df['age'].mean()
user_counts = df.groupby('age_group').size()

# 4. Visualize/Report
plt.bar(user_counts.index, user_counts.values)
```

### Backend API Workflow
```python
# 1. Define data structure (persistent!)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    
# 2. Create API to accept/return data
@app.post("/users/")
def create_user(user_data: UserCreate, db: Session):
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    return user

# 3. Query on demand
@app.get("/users/average-age")
def get_average_age(db: Session):
    avg = db.query(func.avg(User.age)).scalar()
    return {"average_age": avg}

# 4. Serve results as JSON API
# Other services/apps consume this
```

## 📊 Concept Mapping

| Data Science | Backend | Key Difference |
|-------------|---------|----------------|
| **Jupyter Notebook** | **FastAPI App** | Interactive exploration → Production service |
| **DataFrame** | **Database Table** | In-memory → Persistent storage |
| **df.columns** | **Model fields** | Dynamic → Strongly typed |
| **df.to_dict()** | **Pydantic schema** | Loose → Validated structure |
| **Analysis script** | **API endpoint** | Run once → Serve millions |
| **pd.read_csv()** | **db.query()** | File I/O → Database query |
| **df.merge()** | **SQLAlchemy join** | Pandas → SQL |
| **df.groupby()** | **func.count() + group_by** | Pandas → SQL aggregation |
| **Input validation** | **Pydantic models** | Manual checks → Automatic |
| **Error handling** | **HTTP exceptions** | Print errors → Status codes |
| **Local execution** | **API server** | Your machine → Accessible to all |

## 🎯 Common Tasks Translated

### 1. Loading Data

**Data Science:**
```python
# Load from CSV
df = pd.read_csv("posts.csv")

# Load from SQL
df = pd.read_sql("SELECT * FROM posts", connection)
```

**Backend:**
```python
# Query all posts
posts = db.query(models.Post).all()

# Query with filter
posts = db.query(models.Post).filter(
    models.Post.created_at >= datetime(2024, 1, 1)
).all()

# Convert to list of dicts (if needed for processing)
posts_data = [
    {
        "id": p.id,
        "content": p.content,
        "timestamp": p.timestamp
    }
    for p in posts
]
```

### 2. Aggregation

**Data Science:**
```python
# Count posts per user
counts = df.groupby('user_id').size()

# Average likes per post
avg_likes = df.groupby('post_id')['likes'].mean()
```

**Backend:**
```python
# Count posts per user (SQL)
from sqlalchemy import func

post_counts = (
    db.query(
        models.User.username,
        func.count(models.Post.id).label('post_count')
    )
    .join(models.Post)
    .group_by(models.User.id)
    .all()
)

# Result: [('alice', 5), ('bob', 3), ...]

# Return as API endpoint
@app.get("/users/post-counts")
def get_post_counts(db: Session):
    counts = db.query(
        models.User.username,
        func.count(models.Post.id).label('count')
    ).join(models.Post).group_by(models.User.id).all()
    
    return [
        {"username": username, "post_count": count}
        for username, count in counts
    ]
```

### 3. Filtering

**Data Science:**
```python
# Filter rows
active_users = df[df['status'] == 'active']
recent_posts = df[df['date'] > '2024-01-01']
```

**Backend:**
```python
# Filter records
active_users = db.query(models.User).filter(
    models.User.status == 'active'
).all()

recent_posts = db.query(models.Post).filter(
    models.Post.timestamp > datetime(2024, 1, 1)
).all()

# As API endpoint with query parameters
@app.get("/posts/")
def get_posts(
    skip: int = 0,
    limit: int = 10,
    min_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Post)
    
    if min_date:
        query = query.filter(models.Post.timestamp >= min_date)
    
    posts = query.offset(skip).limit(limit).all()
    return posts
```

### 4. Joining Data

**Data Science:**
```python
# Merge dataframes
result = pd.merge(
    posts_df,
    users_df,
    left_on='user_id',
    right_on='id',
    how='left'
)
```

**Backend:**
```python
# Join tables
results = (
    db.query(models.Post, models.User)
    .join(models.User, models.Post.owner_id == models.User.id)
    .all()
)

# Or use relationships (easier!)
post = db.query(models.Post).first()
username = post.owner.username  # SQLAlchemy handles join

# As API endpoint
@app.get("/posts/{post_id}/details")
def get_post_details(post_id: int, db: Session):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "Not found")
    
    return {
        "post_id": post.id,
        "content": post.content,
        "author": post.owner.username,  # Relationship!
        "author_email": post.owner.email
    }
```

### 5. Data Validation

**Data Science:**
```python
# Manual validation
if df['age'].isnull().any():
    print("Missing ages!")

if (df['age'] < 0).any():
    print("Invalid ages!")

# Clean data
df = df[df['age'] >= 0]
```

**Backend:**
```python
# Pydantic automatic validation
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., ge=0, le=150)  # 0 <= age <= 150
    email: str  # Must be a string
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# If client sends invalid data, FastAPI returns 422 error automatically!
@app.post("/users/")
def create_user(user: UserCreate, db: Session):
    # user is guaranteed to be valid here
    ...
```

## 🔧 Key Differences to Remember

### 1. Persistence
**Data Science:** Data exists during script execution
```python
df = pd.read_csv("data.csv")
# Process data
# Script ends → data gone
```

**Backend:** Data persists between requests
```python
# Request 1: Create user
user = User(name="Alice")
db.add(user)
db.commit()

# Request 2 (hours later): User still exists!
user = db.query(User).filter(User.name == "Alice").first()
```

### 2. Concurrency
**Data Science:** Usually single-threaded
```python
for row in df.itertuples():
    process(row)  # One at a time
```

**Backend:** Multiple simultaneous users
```python
# 100 users might call this at the same time!
@app.get("/posts/")
def get_posts(db: Session):
    # Must handle concurrent database access
    # Must be efficient (no one wants to wait)
    return db.query(Post).all()
```

### 3. Error Handling
**Data Science:** Print errors, fix in notebook
```python
try:
    result = df['column'].mean()
except KeyError:
    print("Column not found!")  # Fix and re-run cell
```

**Backend:** Return proper HTTP errors
```python
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Client gets proper 404 response
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 4. Data Types
**Data Science:** Flexible types
```python
df['age'] = [25, "26", 27.5]  # Pandas handles mixed types
```

**Backend:** Strict types
```python
class User(Base):
    age = Column(Integer)  # Must be integer!

# If you try to insert "26" (string), you'll get an error
```

## 💡 Tips for Transitioning

### 1. Think in Terms of Resources
Instead of: "I need to analyze user behavior"
Think: "I need endpoints to CREATE users, READ user data, UPDATE profiles, DELETE accounts" (CRUD)

### 2. Design for Multiple Clients
Instead of: "I'll run this once to get results"
Think: "A mobile app, web app, and analytics dashboard will all call this endpoint"

### 3. Security First
Instead of: "This data is on my laptop"
Think: "This data is accessible over the internet - who can access what?"

### 4. Performance Matters
Instead of: "This takes 5 seconds, I can wait"
Think: "If this takes 5 seconds, users will leave"

### 5. Versioning and Compatibility
Instead of: "I'll just change the column name"
Think: "If I change this, existing clients will break"

## 🎓 Learning Path

1. **Start with CRUD**: Create, Read, Update, Delete operations
2. **Add authentication**: Understand JWT tokens
3. **Learn SQL**: You can't avoid it in backend
4. **Understand HTTP**: Status codes, headers, methods
5. **Practice API design**: RESTful patterns
6. **Study database relationships**: Foreign keys, joins
7. **Learn deployment**: Docker, cloud platforms

## 🚀 Your Advantages as a Data Scientist

✅ **You understand data modeling** - easier to design database schemas
✅ **You know SQL** - directly applicable to ORMs
✅ **You think about data quality** - helps with validation
✅ **You understand statistics** - useful for aggregation endpoints
✅ **You're used to documentation** - essential for API docs
✅ **You know Python well** - FastAPI is very Pythonic

## ⚙️ Practice Project Ideas

1. **Weather API**: Store weather data, expose query endpoints
   - Similar to loading CSV and filtering data
   - Add aggregations (average temp by city)

2. **Survey System**: Create surveys, collect responses
   - Demonstrates one-to-many relationships
   - Practice aggregation (count responses)

3. **Expense Tracker**: Track expenses with categories
   - Good for groupby operations (expenses by category)
   - Time-series queries (expenses per month)

4. **Book Library**: Books, authors, borrowing system
   - Multiple relationships
   - Complex queries (available books by genre)

## 📚 Recommended Resources

- **FastAPI Tutorial** (official docs): Best starting point
- **"Designing Data-Intensive Applications"** by Martin Kleppmann: Architecture concepts
- **"REST API Design Rulebook"** by Mark Massé: API design patterns
- **SQLAlchemy Tutorial**: Deep dive into ORM
- **Postman/Insomnia**: Tools for testing APIs

## 🎯 Success Checklist

- [ ] Built a working API with multiple endpoints
- [ ] Implemented authentication (JWT)
- [ ] Used database relationships (foreign keys)
- [ ] Added proper error handling (HTTP exceptions)
- [ ] Validated input data (Pydantic)
- [ ] Tested API with multiple tools (curl, Postman, Python client)
- [ ] Deployed to a cloud platform
- [ ] Documented API (auto-generated by FastAPI!)

---

Remember: You're not starting from zero! Your data science skills are highly valuable in backend development. The main shift is from "analyze once" to "serve continuously" and from "on my machine" to "accessible to the world."

