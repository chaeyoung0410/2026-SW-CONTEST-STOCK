# Project2026 Backend

FastAPI backend for the Stock Quest MVP.

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Database

Set `DATABASE_URL` in `.env` to your MySQL database.

```text
mysql+pymysql://USER:PASSWORD@HOST:PORT/DB_NAME
```

The database models follow `docs/04_database.md`.

AI 추천 API와 데이터베이스 변경 방법은 각각
[`docs/ai_recommendation_api.md`](docs/ai_recommendation_api.md),
[`migrations/README.md`](migrations/README.md)를 참고하세요.
