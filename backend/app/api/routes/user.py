from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.user import get_user_by_nickname, update_nickname
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(tags=["User"])


@router.get("/user", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(nickname=current_user.nickname)


@router.patch("/user", response_model=UserResponse)
def update_user(
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    existing = get_user_by_nickname(db, request.nickname)
    if existing is not None and existing.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nickname already exists")

    update_nickname(db, current_user, request.nickname)
    db.commit()
    return UserResponse(nickname=current_user.nickname)


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(nickname=current_user.nickname)
