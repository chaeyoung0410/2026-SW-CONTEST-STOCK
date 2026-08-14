from app.db.base import Base
from app.db.session import engine


# 모델에 정의된 테이블이 없으면 생성 (마이그레이션 없이 최초 실행 시 스키마 구축)
def init_db() -> None:
    Base.metadata.create_all(bind=engine)
