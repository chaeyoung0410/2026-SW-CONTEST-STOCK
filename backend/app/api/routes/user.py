from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(tags=["User"])


@router.get("/user", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(nickname=current_user.nickname)


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(nickname=current_user.nickname)
