from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.progress import Progress

BUILDING_IMAGES = {level: f"building_{level}.png" for level in range(15)}


def get_building_level(db: Session, user_id: int) -> int:
    statement = select(func.count()).select_from(Progress).where(
        Progress.user_id == user_id,
        Progress.cleared.is_(True),
    )
    return int(db.scalar(statement) or 0)


def get_building_image(level: int) -> str:
    capped_level = min(level, max(BUILDING_IMAGES))
    return BUILDING_IMAGES.get(capped_level, BUILDING_IMAGES[0])


def get_building_state(db: Session, user_id: int) -> tuple[int, str]:
    level = get_building_level(db, user_id)
    return level, get_building_image(level)
