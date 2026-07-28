"""
앱 진입점
실행: uvicorn app.main:app --reload
문서 확인: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, game, learning, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="주식 학습 게임 API v2",
    description="아이디/비밀번호 로그인 + 단계별 다중 문제 구조 반영",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(game.router)
app.include_router(learning.router)
app.include_router(users.router)


@app.get("/", tags=["health check"])
def root():
    return {"status": "ok", "message": "주식 학습 게임 API v2 서버가 정상 동작 중입니다."}
