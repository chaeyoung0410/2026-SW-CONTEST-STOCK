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
