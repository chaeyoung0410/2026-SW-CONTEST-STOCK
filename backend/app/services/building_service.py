from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.progress import Progress

TOTAL_BUILDING_LEVELS = 14

BUILDING_IMAGES = {
    level: f"building_{level}.png"
    for level in range(TOTAL_BUILDING_LEVELS + 1)
}

NEXT_FEATURES = {
    0: ["건물의 기초 공사가 시작돼요"],
    1: ["외벽이 조금 더 단단해져요"],
    2: ["창문이 추가돼요"],
    3: ["입구가 꾸며져요"],
    4: ["건물 외관이 확장돼요"],
    5: ["간판이 설치돼요"],
    6: ["외벽 장식이 추가돼요"],
    7: ["건물의 층수가 높아져요"],
    8: ["조명이 추가돼요"],
    9: ["창문과 외관이 업그레이드돼요"],
    10: ["옥상 공간이 꾸며져요"],
    11: ["건물 전체가 확장돼요"],
    12: ["고급 외장재가 추가돼요"],
    13: ["최종 건물로 완성돼요"],
    14: [],
}


def get_building_level(db: Session, user_id: int) -> int:
    statement = (
        select(func.count())
        .select_from(Progress)
        .where(
            Progress.user_id == user_id,
            Progress.cleared.is_(True),
        )
    )

    level = int(db.scalar(statement) or 0)

    # 스테이지 수를 초과하지 않도록 제한
    return min(level, TOTAL_BUILDING_LEVELS)


def get_building_image(level: int) -> str:
    capped_level = min(max(level, 0), TOTAL_BUILDING_LEVELS)
    return BUILDING_IMAGES[capped_level]


def get_building_progress(level: int) -> int:
    capped_level = min(max(level, 0), TOTAL_BUILDING_LEVELS)
    return round((capped_level / TOTAL_BUILDING_LEVELS) * 100)


def get_next_features(level: int) -> list[str]:
    capped_level = min(max(level, 0), TOTAL_BUILDING_LEVELS)
    return NEXT_FEATURES.get(capped_level, [])


def get_building_state(db: Session, user_id: int) -> dict:
    level = get_building_level(db, user_id)

    return {
        "level": level,
        "image": get_building_image(level),
        "progress": get_building_progress(level),
        "next_features": get_next_features(level),
    }