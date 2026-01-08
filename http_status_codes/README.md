# FastAPI Authentication & Status Codes Tutorial

This project demonstrates **JWT authentication**, **HTTP status codes**, and **rate limiting** in FastAPI. Perfect for beginners learning backend development.

---

## 📁 Project Structure

```
http_status_codes/
├── main.py              # Application entry point
├── database.py          # Database configuration
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic validation schemas
├── auth.py              # JWT authentication logic
├── rate_limit.py        # Rate limiting implementation
├── app.db               # SQLite database (auto-generated)
└── routers/
    ├── __init__.py
    └── users.py         # User-related API endpoints
```

---

## 🗂️ File Explanations

### **`main.py`** - Application Entry Point

**Purpose:** Initializes the FastAPI app and connects everything together.

```python
app = FastAPI(title="FastAPI Status Code Starter")
Base.metadata.create_all(bind=engine)  # Create database tables
app.include_router(users.router)        # Register user routes
```

**Key Features:**

- Creates database tables on startup
- Registers routers (endpoints)
- Exception handler for database errors (503 Service Unavailable)
- Health check endpoint (`GET /`)

---

### **`database.py`** - Database Configuration

**Purpose:** Sets up SQLite database connection and session management.

```python
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

**Key Concepts:**

- **Engine:** Manages database connections
- **SessionLocal:** Creates database sessions for queries
- **get_db():** Dependency injection function that provides DB sessions to endpoints
- **Base:** Parent class for all database models

---

### **`models.py`** - Database Models

**Purpose:** Defines what data structure looks like in the database.

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="user")
```

**Translation:** Creates a `users` table with columns: id, email, password, role.

⚠️ **Note:** In production, NEVER store plain text passwords! Use bcrypt/argon2 to hash them.

---

### **`schemas.py`** - Data Validation

**Purpose:** Validates incoming requests and outgoing responses using Pydantic.

```python
class UserCreate(BaseModel):
    email: EmailStr      # Validates email format
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
```

**Why separate from models?**

- **Models** = Database structure (what's stored)
- **Schemas** = API structure (what users send/receive)

Example: Users send passwords (UserCreate), but we don't return passwords (UserResponse).

---

### **`auth.py`** - JWT Authentication

**Purpose:** Handles token creation and validation.

#### 🔑 How JWT Authentication Works

**Step 1: User Signs Up/Logs In**

```
User sends: { "email": "john@example.com", "password": "secret" }
       ↓
Backend creates user in database
       ↓
Backend generates JWT token: create_token(user.id)
       ↓
Returns: { "token": "eyJhbGc..." }
```

**What's in the token?**

```json
{
  "sub": "2" // "subject" = user ID
}
```

This is **signed** with a secret key so it can't be forged.

---

**Step 2: User Accesses Protected Endpoint**

```
User sends request with header:
Authorization: Bearer eyJhbGc...
       ↓
FastAPI extracts token using HTTPBearer()
       ↓
get_current_user() decodes token
       ↓
Extracts user_id from token
       ↓
Endpoint uses user_id to fetch user from DB
```

#### 🛡️ Security Flow Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. POST /users/ {"email": "john@example.com", "password": "secret"}
       ↓
┌─────────────────────────────────────────────────────────┐
│  Backend (users.py)                                     │
│  - Checks if email exists (409 Conflict if duplicate)  │
│  - Creates user in database                             │
│  - Calls create_token(user.id)                         │
└──────┬──────────────────────────────────────────────────┘
       │ 2. Returns {"token": "eyJhbGc..."}
       ↓
┌─────────────┐
│   Client    │  (Stores token)
└──────┬──────┘
       │ 3. GET /users/me
       │    Header: Authorization: Bearer eyJhbGc...
       ↓
┌─────────────────────────────────────────────────────────┐
│  FastAPI Security (auth.py)                             │
│  - HTTPBearer() extracts token from header              │
│  - get_current_user() is called automatically           │
│  - jwt.decode(token) validates signature                │
│  - Extracts user_id from payload                        │
└──────┬──────────────────────────────────────────────────┘
       │ 4. Passes user_id to endpoint
       ↓
┌─────────────────────────────────────────────────────────┐
│  Endpoint (users.py)                                    │
│  def get_my_profile(user_id: int = Depends(...)):      │
│      user = db.get(User, user_id)                      │
│      return user profile                                │
└─────────────────────────────────────────────────────────┘
```

---

#### 🔐 Code Walkthrough

**Creating a Token:**

```python
def create_token(user_id: int):
    return jwt.encode({"sub": str(user_id)}, SECRET_KEY, algorithm="HS256")
```

- Takes user ID
- Creates JSON: `{"sub": "2"}`
- Signs it with secret key
- Returns encoded token

**Validating a Token:**

```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Extract token from "Bearer <token>"

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload["sub"])  # Return user ID
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

**What happens when token is invalid?**

- Expired → 401 Unauthorized
- Tampered → 401 Unauthorized
- Missing → 403 Forbidden (HTTPBearer raises this automatically)

---

### **`rate_limit.py`** - Rate Limiting

**Purpose:** Prevents abuse by limiting requests per user.

```python
LIMIT = 5       # Max requests
WINDOW = 60     # Per 60 seconds

REQUESTS = {}   # In-memory storage: {client_id: [timestamp1, timestamp2, ...]}
```

**How it works:**

1. User makes request with `client_id`
2. Check history: filter out timestamps older than 60 seconds
3. If count ≥ 5 → Reject with 429 Too Many Requests
4. Else → Add current timestamp and allow

**Example:**

```
Client "user123" makes requests at:
[10:00:00, 10:00:05, 10:00:10, 10:00:15, 10:00:20]  ← 5 requests in 20 seconds
[10:00:25] ← 6th request → REJECTED (429)
[10:01:01] ← After 60s from first request → ALLOWED (first request expired)
```

⚠️ **Note:** This uses in-memory storage. In production, use Redis for distributed rate limiting.

---

### **`routers/users.py`** - API Endpoints

**Purpose:** Defines all user-related routes.

#### Route Order Matters! 🚨

```python
@router.get("/me")              # ✅ Specific route first
@router.get("/limited")         # ✅ Another specific route
@router.get("/{user_id}")       # ⚠️ Dynamic route MUST be last
```

**Why?** FastAPI matches routes top-to-bottom. If `/{user_id}` comes first, `/me` would be interpreted as `user_id="me"` and fail.

---

## 🔄 Complete Authentication Flow (Step-by-Step)

### **Scenario: New User Signs Up and Accesses Their Profile**

#### **1. User Registration**

```http
POST /users/
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "mypassword"
}
```

**Backend Process:**

```
1. Pydantic validates email format (UserCreate schema)
2. Check if email exists in database
   - If yes → 409 Conflict
   - If no → Continue
3. Create User object: User(email=..., password=..., role="user")
4. Save to database
5. Generate JWT token: create_token(user.id)
6. Return {"token": "eyJhbGc..."}
```

**Response:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.xyz..."
}
```

---

#### **2. User Accesses Protected Route**

```http
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.xyz...
```

**Backend Process:**

```
1. HTTPBearer() dependency extracts token from Authorization header
2. get_current_user() is called automatically
3. jwt.decode() validates token signature
   - Invalid signature → 401 Unauthorized
   - Valid → Extract payload {"sub": "1"}
4. Return user_id = 1 to endpoint function
5. Endpoint queries: db.get(User, 1)
6. Returns user data (excluding password via UserResponse schema)
```

**Response:**

```json
{
  "id": 1,
  "email": "alice@example.com",
  "role": "user"
}
```

---

## 📊 HTTP Status Codes Used

| Code    | Status               | When Used                               | Example                         |
| ------- | -------------------- | --------------------------------------- | ------------------------------- |
| **200** | OK                   | Successful GET request                  | GET /users/me                   |
| **201** | Created              | Resource created successfully           | POST /users/                    |
| **204** | No Content           | Successful DELETE (no response body)    | DELETE /users/1                 |
| **401** | Unauthorized         | Invalid/missing token                   | Bad JWT token                   |
| **403** | Forbidden            | Valid user but insufficient permissions | Non-admin accessing admin route |
| **404** | Not Found            | Resource doesn't exist                  | GET /users/999                  |
| **409** | Conflict             | Resource already exists                 | Email already registered        |
| **422** | Unprocessable Entity | Validation failed                       | Invalid email format            |
| **429** | Too Many Requests    | Rate limit exceeded                     | 6th request in 60 seconds       |
| **503** | Service Unavailable  | Database down                           | Database connection failed      |

---

## 🧪 Testing Guide

### **1. Create a User**

```bash
POST /users/
Body: {"email": "test@example.com", "password": "test123"}
Response: {"token": "eyJhbGc..."}
```

### **2. Authorize in Swagger**

1. Click 🔒 **Authorize** button (top right)
2. Paste token (WITHOUT "Bearer" prefix)
3. Click **Authorize**

### **3. Test Protected Endpoint**

```bash
GET /users/me
Response: {"id": 1, "email": "test@example.com", "role": "user"}
```

### **4. Test Rate Limiting**

```bash
GET /users/limited?client_id=test123
# Click Execute 6 times quickly
# 6th request returns 429 Too Many Requests
```

---

## 🔒 Security Best Practices (Not Implemented Here)

This is a **learning project**. In production, you should:

1. **Hash passwords** using `bcrypt` or `passlib`

   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"])
   hashed = pwd_context.hash(password)
   ```

2. **Use environment variables** for secrets

   ```python
   import os
   SECRET_KEY = os.getenv("SECRET_KEY")
   ```

3. **Add token expiration**

   ```python
   jwt.encode({"sub": str(user_id), "exp": datetime.utcnow() + timedelta(hours=1)})
   ```

4. **Use HTTPS** in production
5. **Store rate limits in Redis** instead of memory

---

## 🚀 Running the Project

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic python-jose

# Run server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload

# Access Swagger docs
http://localhost:8000/docs
```

---

## 🎓 Key Learnings

1. **JWT tokens** allow stateless authentication (server doesn't store sessions)
2. **Dependency Injection** (`Depends()`) makes code reusable and testable
3. **Route order matters** - specific routes before dynamic parameters
4. **HTTP status codes** communicate what happened to the client
5. **Pydantic schemas** validate data automatically
6. **SQLAlchemy** handles database operations safely

---

## 📚 Next Steps

- Add password hashing with `passlib`
- Implement refresh tokens
- Add user roles and permissions
- Write tests with `pytest`
- Deploy to production (Railway, Render, etc.)

---

## ❓ Common Errors & Solutions

| Error                                    | Cause                   | Solution                                |
| ---------------------------------------- | ----------------------- | --------------------------------------- |
| `ImportError: attempted relative import` | Running file directly   | Use `python main.py` not `python -m`    |
| `422 missing header authorization`       | Wrong route order       | Move specific routes above `/{user_id}` |
| `401 Invalid token`                      | Token expired/corrupted | Generate new token                      |
| `429 Rate limit exceeded`                | Too many requests       | Wait 60 seconds or change client_id     |

---

**Happy Learning! 🎉**

Got questions? The best way to learn is to break things and fix them. Try modifying the code and see what happens!
