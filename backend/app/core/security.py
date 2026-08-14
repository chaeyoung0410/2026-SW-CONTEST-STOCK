from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 비밀번호를 bcrypt로 해시
def hash_password(password: str) -> str:
    return password_context.hash(password)


# 평문 비밀번호가 저장된 해시와 일치하는지 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


# 로그인 성공 시 사용자 id를 담은 JWT 액세스 토큰 발급 (만료시간 설정값 적용)
def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
