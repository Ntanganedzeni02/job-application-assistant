"""
Tests for all /analyze endpoints.
We mock the OpenAI service so tests run without a real API key.

Run: pytest tests/ -v
"""
import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models import CVAnalysisResponse, JobMatchResponse, ImprovedCVResponse
from app.routers.analyze import get_ai_service  # import the dependency to override

# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_CV = """
John Doe — Senior Python Developer
5 years of experience building REST APIs with FastAPI and Django.
Proficient in Python, PostgreSQL, Docker, AWS, and Redis.
Led a team of 3 engineers delivering a microservices platform.
BSc Computer Science, University of Cape Town, 2018.
"""

SAMPLE_JD = """
We are looking for a Python Backend Developer.
Requirements: 3+ years Python, FastAPI or Django, PostgreSQL, Docker.
Nice to have: AWS experience, team lead experience.
"""

MOCK_CV_ANALYSIS = CVAnalysisResponse(
    summary="Experienced Python developer with team leadership skills.",
    strengths=["Python expertise", "API development", "Team leadership"],
    weaknesses=["No frontend experience mentioned"],
    skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
    experience_years="5 years",
    seniority_level="Senior",
)

MOCK_MATCH = JobMatchResponse(
    match_score=88,
    qualifies=True,
    matching_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
    missing_skills=[],
    recommendation="Apply now",
    reasoning="Strong match across all core requirements.",
)

MOCK_IMPROVE = ImprovedCVResponse(
    improved_cv="[Improved CV text...]",
    cover_letter="Dear Hiring Manager, [Cover letter...]",
    changes_made=["Added metrics to bullet points", "Highlighted FastAPI experience first"],
)


# ── Fixture using FastAPI dependency_overrides ────────────────────────────────

@pytest.fixture(autouse=False)
def mock_service():
    service = AsyncMock()
    service.analyze_cv.return_value = MOCK_CV_ANALYSIS
    service.match_job.return_value = MOCK_MATCH
    service.improve_cv_and_generate_cover_letter.return_value = MOCK_IMPROVE

    app.dependency_overrides[get_ai_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_analyze_cv(mock_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/analyze/cv", json={"cv_text": SAMPLE_CV})
    assert response.status_code == 200
    data = response.json()
    assert data["seniority_level"] == "Senior"
    assert "Python" in data["skills"]


@pytest.mark.asyncio
async def test_match_job(mock_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/analyze/match",
            json={"cv_text": SAMPLE_CV, "job_description": SAMPLE_JD},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["match_score"] == 88
    assert data["qualifies"] is True


@pytest.mark.asyncio
async def test_qualify(mock_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/analyze/qualify",
            json={"cv_text": SAMPLE_CV, "job_description": SAMPLE_JD},
        )
    assert response.status_code == 200
    assert response.json()["qualifies"] is True


@pytest.mark.asyncio
async def test_improve_cv(mock_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/analyze/improve",
            json={"cv_text": SAMPLE_CV, "job_description": SAMPLE_JD, "tone": "professional"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "cover_letter" in data
    assert len(data["changes_made"]) > 0


@pytest.mark.asyncio
async def test_analyze_cv_too_short():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/analyze/cv", json={"cv_text": "Short"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_tone():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/analyze/improve",
            json={"cv_text": SAMPLE_CV, "job_description": SAMPLE_JD, "tone": "aggressive"},
        )
    assert response.status_code == 422