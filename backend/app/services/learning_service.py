from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning import Learning
from app.services.stage_service import ensure_stage_access


# 스테이지 접근 권한 확인 후 해당 스테이지의 개념 설명 페이지들을 합쳐서 반환
def get_learning(db: Session, stage_id: int, user_id: int | None = None) -> dict:
    stage = ensure_stage_access(db, stage_id, user_id)
    pages = list(
        db.scalars(
            select(Learning)
            .where(Learning.stage_id == stage_id)
            .order_by(Learning.page_order)
        )
    )
    content = "\n\n".join(page.content for page in pages) or stage.description
    return {
        "stage_id": stage.stage_id,
        "title": pages[0].title if pages else stage.title,
        "content": content,
        "pages": pages,
    }
