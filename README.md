# 2026-SW-CONTEST-STOCK

## 프로젝트 구조

```text
2026-SW-CONTEST-STOCK/
├── backend/                # FastAPI 서버
│   ├── app/
│   │   ├── main.py         # 앱 진입점
│   │   ├── core/           # 설정, 보안
│   │   ├── db/              # DB 세션, 초기화, 시드 데이터
│   │   ├── models/          # SQLAlchemy 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── services/        # 비즈니스 로직
│   │   └── api/routes/      # 엔드포인트
│   ├── migrations/          # SQL 마이그레이션
│   └── tests/                # pytest 테스트
└── frontend/                 # 정적 프론트엔드
    ├── pages/                 # HTML 화면
    └── assets/                # js / css / img
```
