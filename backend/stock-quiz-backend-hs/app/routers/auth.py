"""
2. 회원가입 / 3. 로그인 / 8-4. 로그아웃 화면 대응 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_db
from app.models import GameProgress, User
from app.schemas import (
    CheckIdResponse,
    LoginRequest,
    LogoutResponse,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["인증"])


@router.get("/check-id", response_model=CheckIdResponse, summary="아이디 중복 확인")
def check_id(user_id: str, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.user_id == user_id).first() is not None
    return CheckIdResponse(available=not exists)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입 (아이디 + 6자리 비밀번호)",
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 아이디입니다.",
        )

    user = User(
        user_id=payload.user_id,
        nickname=payload.user_id,  # 닉네임은 일단 아이디와 동일하게 설정 (원하면 이후 변경 기능 추가 가능)
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 신규 유저는 게임 진행상태도 함께 생성
    db.add(GameProgress(user_id=user.id))
    db.commit()

    return SignupResponse(user_id=user.user_id, created_at=user.created_at)


@router.post("/login", response_model=TokenResponse, summary="로그인")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == payload.user_id).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    access_token = create_access_token(data={"sub": user.user_id})
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=LogoutResponse, summary="로그아웃")
def logout(current_user: User = Depends(get_current_user)):
    # JWT는 서버가 상태를 저장하지 않으므로(stateless), 실제 무효화는 프론트엔드에서
    # 저장해둔 토큰을 삭제하는 것으로 처리합니다. 이 엔드포인트는 형식을 맞추기 위한 것입니다.
    return LogoutResponse(message="로그아웃 되었습니다.")
