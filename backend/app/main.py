"""
Job Application Assistant — FastAPI Backend
Entry point: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import HealthResponse
from app.routers.analyze import router as analyze_router

settings = get_settings()

app = FastAPI(
    title="Job Application Assistant API",
    description=(
        "AI-powered backend that analyzes CVs, matches job descriptions, "
        "checks qualifications, and generates improved CVs + cover letters."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allows the frontend (on a different port/domain) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze_router)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint used by Render and GitHub Actions.
    Returns 200 if the server is running correctly.
    """
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        model=settings.openai_model,
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Job Application Assistant API",
        "docs": "/docs",
        "health": "/health",
    }