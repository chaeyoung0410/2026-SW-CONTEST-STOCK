from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.building import BuildingResponse
from app.services.building_service import sync_building

router = APIRouter(tags=["Building"])


@router.get("/building", response_model=BuildingResponse)
def get_building(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BuildingResponse:
    level, image = sync_building(db, current_user.user_id)
    db.commit()
    return BuildingResponse(level=level, image=image)
