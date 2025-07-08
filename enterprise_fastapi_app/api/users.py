from fastapi import APIRouter

from app_fastapi.schemas import user

router = APIRouter()


@router.post("/", response_model=user.User)
def create_user(user_in: user.UserCreate):
    """
    Create a new user.
    In a real app, this would save the user to a database.
    """
    # This is a mock response.
    # We are "creating" a user and returning its data.
    # The password would be hashed and not returned.
    user_data = user_in.model_dump()
    return user.User(
        id=1,
        email=user_data["email"],
        full_name=user_data["full_name"],
        is_active=True,
    ) 