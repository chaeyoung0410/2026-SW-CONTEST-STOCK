from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ranking import RankingResponse
from app.services.ranking_service import get_ranking

router = APIRouter(tags=["Ranking"])


@router.get("/ranking", response_model=list[RankingResponse])
def get_rankings(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[dict]:
    return get_ranking(db, limit)
