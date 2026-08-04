from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, building, history, learning, news, quiz, result, stage, user
from app.db.init_db import init_db
from app.db.seed_data import seed_default_user, seed_if_empty
from app.db.session import SessionLocal

app = FastAPI(title="Project2026 Stock Quest API", version="0.1.0")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
PAGES_DIR = FRONTEND_DIR / "pages"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_if_empty(db)
        seed_default_user(db)
    finally:
        db.close()


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(stage.router)
app.include_router(learning.router)
app.include_router(quiz.router)
app.include_router(result.router)
app.include_router(building.router)
app.include_router(history.router)
app.include_router(news.router)

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="frontend-assets")
app.mount("/pages", StaticFiles(directory=PAGES_DIR, html=True), name="frontend-pages")


@app.get("/")
def landing_page() -> RedirectResponse:
    return RedirectResponse(url="/pages/index.html")


@app.get("/login")
def login_page() -> RedirectResponse:
    return RedirectResponse(url="/pages/Login.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "Project2026 Backend"}