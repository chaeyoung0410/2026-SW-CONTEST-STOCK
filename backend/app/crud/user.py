from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


# 로그인 아이디로 사용자 조회 (없으면 None)
def get_user_by_login_id(db: Session, login_id: str) -> User | None:
    return db.scalar(select(User).where(User.login_id == login_id))


# 로그인 아이디 변경
def update_login_id(db: Session, user: User, login_id: str) -> User:
    user.login_id = login_id
    db.flush()
    return user


# 신규 사용자 생성 (비밀번호는 이미 해시된 값을 받는다)
def create_user(
    db: Session,
    *,
    login_id: str,
    hashed_password: str,
) -> User:
    user = User(
        login_id=login_id,
        password=hashed_password,
    )
    db.add(user)
    db.flush()
    return user