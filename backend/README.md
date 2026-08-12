# Project2026 Backend

FastAPI backend for the Stock Quest MVP. 이 서버가 API와 `frontend/` 정적 페이지를 함께 서빙합니다.

## Run

### Windows (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

### macOS / Linux

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

서버 실행 후 브라우저에서 `http://127.0.0.1:8000/` 로 접속하세요 (Live Server 등 다른 정적 서버로 프론트 파일을
직접 열면 API 요청이 백엔드로 가지 않아 로그인 등이 실패합니다). 테스트 계정은 `kim` / `123456` 입니다.

## Database

기본값은 `.env.example`에 있는 대로 SQLite (`sqlite:///./local.db`)이며, 별도 설정 없이 바로 동작합니다.
MySQL을 쓰려면 `.env`의 `DATABASE_URL`을 아래처럼 바꾸세요.

```text
mysql+pymysql://USER:PASSWORD@HOST:PORT/DB_NAME
```

The database models follow `docs/04_database.md`.

AI 추천 API와 데이터베이스 변경 방법은 각각
[`docs/ai_recommendation_api.md`](docs/ai_recommendation_api.md),
[`migrations/README.md`](migrations/README.md)를 참고하세요.
