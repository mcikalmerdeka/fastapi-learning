# 👋 Start Here - Social Media Backend Learning Guide

Welcome! This is a comprehensive learning resource for understanding FastAPI backend development, especially designed for those coming from a data science background.

## 📖 Documentation Structure

This project includes several documentation files. Here's the recommended reading order:

### 1. **README.md** ← Start here!
- Project overview
- Quick setup instructions
- API endpoints list
- Basic architecture
- Installation guide

### 2. **DATA_SCIENCE_TO_BACKEND.md** ← For data scientists
- Mental model shift from analysis to APIs
- Concept translations (pandas → SQL)
- Key differences to understand
- Your advantages and learning path

### 3. **Code Files** (with inline comments)
Read in this order:
- `database.py` - Database setup (5 min)
- `models.py` - Database tables (10 min)
- `schemas.py` - API data validation (5 min)
- `auth.py` - Authentication system (15 min)
- `exceptions.py` - Error handling (5 min)
- `main.py` - App initialization (5 min)
- `routes/auth.py` - Login endpoint (10 min)
- `routes/users.py` - User operations (15 min)
- `routes/posts.py` - Post operations (30 min)

### 4. **ARCHITECTURE.md** ← Deep dive
- Database schema diagrams
- Request flow visualizations
- Authentication flow
- Complex query breakdown
- Design patterns explained

### 5. **QUICK_REFERENCE.md** ← Practical guide
- Common commands
- API testing examples (curl, Python)
- Code patterns and snippets
- Database query examples
- Debugging tips
- Common errors and solutions

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install "fastapi[standard]" sqlalchemy "python-jose[cryptography]" "passlib[bcrypt]"

# 2. Navigate to project folder
cd social-media-backend

# 3. Start the server
fastapi dev main.py

# 4. Open API documentation in browser
# http://localhost:8000/docs
```

## 🎯 Learning Goals

By studying this project, you will understand:

✅ How to build a REST API with FastAPI
✅ How to work with SQL databases using an ORM
✅ How to implement JWT authentication
✅ How to structure a production-grade backend project
✅ How to handle errors and validate data
✅ How to write complex database queries
✅ How to design API endpoints following REST principles

## 📚 Reading Paths

### Path 1: Quick Learner (2 hours)
1. README.md (overview)
2. Skim through code files focusing on comments
3. Run the API and test endpoints using Swagger UI
4. Try QUICK_REFERENCE examples

### Path 2: Deep Understanding (1 day)
1. README.md
2. DATA_SCIENCE_TO_BACKEND.md (if from data background)
3. Read all code files carefully with inline comments
4. ARCHITECTURE.md (understand flows)
5. QUICK_REFERENCE.md (practice examples)
6. Experiment with modifications

### Path 3: Mastery (3-5 days)
1. All documentation thoroughly
2. Study every line of code
3. Implement suggested exercises
4. Build similar features from scratch
5. Deploy to production

## 🔍 Key Files Explained

```
social-media-backend/
│
├── 📘 Documentation (Start here!)
│   ├── START_HERE.md ← You are here
│   ├── README.md ← Project overview
│   ├── ARCHITECTURE.md ← Deep technical dive
│   ├── QUICK_REFERENCE.md ← Practical examples
│   └── DATA_SCIENCE_TO_BACKEND.md ← DS transition guide
│
├── 🔧 Core Setup Files
│   ├── main.py ← App entry point (FastAPI initialization)
│   ├── database.py ← Database connection setup
│   └── auth.py ← Authentication utilities (JWT, passwords)
│
├── 🗃️ Data Layer
│   ├── models.py ← Database tables (SQLAlchemy ORM)
│   └── schemas.py ← API request/response validation (Pydantic)
│
├── 🛠️ Utilities
│   └── exceptions.py ← Centralized error handling
│
└── 🌐 API Endpoints
    └── routes/
        ├── auth.py ← Login endpoint
        ├── users.py ← User registration, follow/unfollow
        └── posts.py ← Post CRUD, likes, retweets
```

## 💡 Key Concepts

### 1. **Separation of Concerns**
- **Models**: Database structure (what's stored)
- **Schemas**: API structure (what's sent/received)
- **Routes**: Endpoint logic (what happens)

### 2. **Dependency Injection**
FastAPI automatically provides:
- Database sessions
- Current authenticated user
- Request data validation

### 3. **Type Safety**
Everything is typed:
- Database columns have types
- API inputs/outputs are validated
- Python type hints everywhere

### 4. **Security by Design**
- Passwords are hashed (never stored plain)
- JWT tokens for authentication
- Protected endpoints require auth
- Input validation prevents injection

## 🎓 Learning Exercises

### Beginner (After reading code)
1. Add a new field to User model (e.g., `bio`)
2. Create an endpoint to get a single post by ID
3. Add query parameters to filter posts

### Intermediate (After understanding architecture)
1. Implement a comment system for posts
2. Add user profile endpoint with post count
3. Create endpoint to list user's followers

### Advanced (After mastery)
1. Implement a feed (posts from followed users)
2. Add hashtag support with search
3. Implement rate limiting
4. Add database migrations with Alembic

## 🐛 Testing the API

### Using Swagger UI (Easiest)
1. Start server: `fastapi dev main.py`
2. Open: http://localhost:8000/docs
3. Try endpoints interactively!

### Using Python (Most flexible)
See QUICK_REFERENCE.md for complete examples:
```python
import requests
BASE_URL = "http://localhost:8000"

# Register
requests.post(f"{BASE_URL}/users/", json={...})

# Login
response = requests.post(f"{BASE_URL}/token", data={...})
token = response.json()["access_token"]

# Create post (authenticated)
headers = {"Authorization": f"Bearer {token}"}
requests.post(f"{BASE_URL}/posts/", headers=headers, json={...})
```

### Using curl (Terminal)
```bash
# Register user
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret"}'
```

## ❓ Common Questions

**Q: Where's the database file?**
A: `microblog.db` is created when you first run the app (SQLite file-based database)

**Q: How do I reset the database?**
A: Delete `microblog.db` and restart the app

**Q: How do I see SQL queries?**
A: In `database.py`, add `echo=True` to `create_engine()`

**Q: Why JWT instead of sessions?**
A: JWTs are stateless - better for APIs and microservices

**Q: Can I use PostgreSQL instead?**
A: Yes! Just change `SQLALCHEMY_DATABASE_URL` in `database.py`

**Q: How do I deploy this?**
A: Many options: Railway, Render, Heroku, AWS, DigitalOcean, etc.

## 🚨 Troubleshooting

**"Module not found" error**
→ Install dependencies: `pip install "fastapi[standard]" sqlalchemy python-jose passlib`

**"Could not validate credentials"**
→ Token expired or invalid. Login again to get new token.

**"Database is locked"**
→ SQLite issue with concurrent access. Restart server or use PostgreSQL.

**Port 8000 already in use**
→ Another app using the port. Use: `uvicorn main:app --port 8001`

## 🌟 Next Steps

After mastering this project:

1. **Study production patterns**:
   - Environment variables for configuration
   - Database migrations (Alembic)
   - Logging and monitoring
   - Unit testing (pytest)

2. **Learn deployment**:
   - Docker containerization
   - Cloud platform deployment
   - CI/CD pipelines

3. **Explore advanced topics**:
   - WebSockets for real-time features
   - Background tasks (Celery)
   - Caching (Redis)
   - API versioning

4. **Build your own project**:
   - E-commerce API
   - Blog platform
   - Task manager
   - Your idea!

## 📞 Additional Resources

- **Official FastAPI Docs**: https://fastapi.tiangolo.com
- **FastAPI GitHub**: https://github.com/tiangolo/fastapi
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Pydantic Docs**: https://docs.pydantic.dev
- **JWT.io**: https://jwt.io (decode/understand tokens)

## 🎉 You're Ready!

Start with README.md, then explore the code files. All files have extensive comments explaining what's happening and why.

Don't rush - take time to understand each concept. Run the code, modify it, break it, fix it. That's how you learn!

Good luck! 🚀

---

**Remember**: Every expert was once a beginner. You've got this! 💪

