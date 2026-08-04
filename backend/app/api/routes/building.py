from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.building import BuildingResponse
from app.services.building_service import get_building_state

router = APIRouter(tags=["Building"])


@router.get("/building", response_model=BuildingResponse)
def get_building(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BuildingResponse:
    state = get_building_state(db, current_user.user_id)
    return BuildingResponse(**state)