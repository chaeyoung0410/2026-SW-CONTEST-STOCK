from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user_by_email, get_user_by_login_id, get_user_by_nickname
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.services.building_service import ensure_building


def _resolve_nickname(db: Session, login_id: str, nickname: str | None) -> str:
    if nickname is not None:
        if get_user_by_nickname(db, nickname) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nickname already exists")
        return nickname

    candidate = login_id
    suffix = 1
    while get_user_by_nickname(db, candidate) is not None:
        suffix += 1
        candidate = f"{login_id}{suffix}"
    return candidate


def sign_up(db: Session, login_id: str, email: str | None, password: str, nickname: str | None) -> User:
    if get_user_by_login_id(db, login_id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login ID already exists")

    resolved_email = email if email is not None else f"{login_id}@stockquest.local"
    if get_user_by_email(db, resolved_email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    resolved_nickname = _resolve_nickname(db, login_id, nickname)

    user = create_user(
        db,
        login_id=login_id,
        email=resolved_email,
        hashed_password=hash_password(password),
        nickname=resolved_nickname,
    )
    ensure_building(db, user.user_id)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, login_id: str, password: str) -> tuple[User, str]:
    user = get_user_by_login_id(db, login_id)
    if user is None or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login ID or password")

    token = create_access_token(subject=str(user.user_id))
    return user, token
