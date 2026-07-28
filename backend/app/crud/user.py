from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_login_id(db: Session, login_id: str) -> User | None:
    return db.scalar(select(User).where(User.login_id == login_id))


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def update_login_id(db: Session, user: User, login_id: str) -> User:
    user.login_id = login_id
    db.flush()
    return user


def create_user(
    db: Session,
    *,
    login_id: str,
    email: str,
    hashed_password: str,
) -> User:
    user = User(
        login_id=login_id,
        email=email,
        password=hashed_password,
    )
    db.add(user)
    db.flush()
    return user