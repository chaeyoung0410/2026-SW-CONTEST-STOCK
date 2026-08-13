from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthStatusResponse, LoginRequest, LoginResponse, SignUpRequest, SignUpResponse
from app.services.auth_service import login, sign_up

router = APIRouter(tags=["Authentication"])


# 회원가입
@router.post("/signup", response_model=SignUpResponse)
def signup(request: SignUpRequest, db: Session = Depends(get_db)) -> SignUpResponse:
    sign_up(db, request.login_id, request.password)
    return SignUpResponse(success=True)


# 로그인 후 액세스 토큰 발급
@router.post("/login", response_model=LoginResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user, token = login(db, request.login_id, request.password)
    return LoginResponse(success=True, user_id=user.user_id, access_token=token)


# 로그인 여부 확인 (비로그인이어도 에러 없이 상태만 반환)
@router.get("/auth/status", response_model=AuthStatusResponse)
def auth_status(current_user: User | None = Depends(get_optional_current_user)) -> AuthStatusResponse:
    return AuthStatusResponse(logged_in=current_user is not None)
