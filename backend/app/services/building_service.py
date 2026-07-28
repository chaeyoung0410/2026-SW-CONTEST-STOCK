from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.building import Building
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


def ensure_building(db: Session, user_id: int) -> Building:
    building = db.scalar(select(Building).where(Building.user_id == user_id))
    if building is None:
        building = Building(user_id=user_id, image=get_building_image(0))
        db.add(building)
        db.flush()
    return building


def sync_building(db: Session, user_id: int) -> tuple[int, str]:
    building = ensure_building(db, user_id)
    level = get_building_level(db, user_id)
    building.image = get_building_image(level)
    db.flush()
    return level, building.image
