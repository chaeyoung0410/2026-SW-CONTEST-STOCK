from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.user import get_user_by_login_id, update_login_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(tags=["User"])


# 내 계정 정보 조회
@router.get("/user", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(login_id=current_user.login_id)


# 로그인 아이디 변경 (중복이면 409 반환)
@router.patch("/user", response_model=UserResponse)
def update_user(
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    existing = get_user_by_login_id(db, request.login_id)
    if existing is not None and existing.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login ID already exists")

    update_login_id(db, current_user, request.login_id)
    db.commit()
    return UserResponse(login_id=current_user.login_id)


# 프로필 정보 조회 (get_user와 동일한 응답)
@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(login_id=current_user.login_id)