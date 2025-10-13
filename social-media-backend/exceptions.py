# Centralized exception handlers for consistent error responses across the API
from fastapi import HTTPException, status

# 404 Not Found - Resource doesn't exist (e.g., user, post not found)
def raise_not_found_exception(detail: str = "Resource not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

# 403 Forbidden - User is authenticated but doesn't have permission
# (e.g., trying to edit someone else's post)
def raise_forbidden_exception(detail: str = "Not authorized to perform this action"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

# 400 Bad Request - Invalid input or business logic violation
# (e.g., trying to follow yourself)
def raise_bad_request_exception(detail: str = "Invalid request"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

# 401 Unauthorized - Authentication failed (wrong credentials or missing token)
# WWW-Authenticate header tells client to use Bearer token authentication
def raise_unauthorized_exception(detail: str = "Incorrect username or password"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

# 409 Conflict - Resource already exists (e.g., duplicate username)
def raise_conflict_exception(detail: str = "Conflict occurred"):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)