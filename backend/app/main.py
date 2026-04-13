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
    docs_url="/docs",       
    redoc_url="/redoc",    
)

origins = [
    "https://my-job-assistant-xk24.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # NOT "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
   
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