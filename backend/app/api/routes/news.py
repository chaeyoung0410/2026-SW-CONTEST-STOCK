from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.news import NewsItemResponse
from app.services.news_service import get_news

router = APIRouter(tags=["News"])


@router.get("/news", response_model=list[NewsItemResponse])
def get_news_list(current_user: User = Depends(get_current_user)) -> list[dict]:
    return get_news(limit=5)