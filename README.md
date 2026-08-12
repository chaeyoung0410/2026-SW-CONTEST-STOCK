# 2026-SW-CONTEST-STOCK — Stock Quest

주식/경제 개념을 퀴즈로 학습하며 건물을 성장시키는 게이미피케이션 학습 서비스입니다.
FastAPI 백엔드가 REST API와 프론트엔드 정적 페이지를 함께 서빙하는 단일 서버 구조입니다.

- 로그인 / 회원가입
- 스테이지별 퀴즈 풀이 및 결과/기록 확인
- 오답 기반 AI 맞춤 학습 추천
- 학습 진행도에 따른 건물 성장 연출
- 마이페이지 (경제 뉴스, 학습 통계)

## 빠른 실행 (Windows / PowerShell)

> ⚠️ 실제 코드와 서버는 `backend/` 가 아니라 **`repo/backend`** 안에 있습니다. 이 저장소를 클론했다면
> 그 클론 폴더 자체가 곧 `backend/`, `frontend/` 를 담고 있는 위치이니 아래 경로를 자신의 클론 위치에 맞게 읽으세요.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

서버가 뜨면 브라우저에서 아래 주소로 접속하세요.

```
http://127.0.0.1:8000/
```

**테스트 계정**: `kim` / `123456` (DB가 비어있을 때 자동으로 시드됩니다)

### ⚠️ VSCode Live Server로 열지 마세요

프론트 페이지들은 `fetch("/login")`처럼 상대경로로 백엔드 API를 호출합니다. Live Server(보통 5500번 포트)로 `index.html`을 열면
API 요청이 백엔드가 없는 5500번 포트로 나가버려 **"서버와 연결할 수 없습니다"** 에러가 발생합니다. 반드시 위 uvicorn 서버가
직접 서빙하는 `http://127.0.0.1:8000/` 로 접속해야 정상 동작합니다.

## 세부 문서

- 백엔드 실행/구조: [`backend/README.md`](backend/README.md)
- AI 추천 API: [`backend/docs/ai_recommendation_api.md`](backend/docs/ai_recommendation_api.md)
- DB 마이그레이션: [`backend/migrations/README.md`](backend/migrations/README.md)

## 기술 스택

- Backend: FastAPI, SQLAlchemy, SQLite(기본) / MySQL(선택)
- Frontend: HTML/CSS/JS (백엔드가 정적 파일로 서빙)
