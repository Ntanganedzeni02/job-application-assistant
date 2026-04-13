from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAIError

from app.config import Settings, get_settings
from app.models import (
    AnalyzeCVRequest,
    CVAnalysisResponse,
    ImprovedCVResponse,
    ImproveCVRequest,
    JobMatchResponse,
    MatchJobRequest,
)
from app.services.openai_service import OpenAIService

router = APIRouter(prefix="/analyze", tags=["Analysis"])


def get_ai_service(settings: Settings = Depends(get_settings)) -> OpenAIService:
    """FastAPI dependency — creates the AI service with current settings."""
    return OpenAIService(settings)


#  Endpoint 1: Analyze CV
@router.post(
    "/cv",
    response_model=CVAnalysisResponse,
    summary="Analyze a CV",
    description="Extract structured profile data: strengths, weaknesses, skills, seniority.",
)
async def analyze_cv(
    body: AnalyzeCVRequest,
    service: OpenAIService = Depends(get_ai_service),
) -> CVAnalysisResponse:
    try:
        return await service.analyze_cv(body.cv_text)
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


#  Endpoint 2: Match Job 
@router.post(
    "/match",
    response_model=JobMatchResponse,
    summary="Match CV to Job Description",
    description="Score fit (0-100), list matching/missing skills, get a recommendation.",
)
async def match_job(
    body: MatchJobRequest,
    service: OpenAIService = Depends(get_ai_service),
) -> JobMatchResponse:
    try:
        return await service.match_job(body.cv_text, body.job_description)
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


#  Endpoint 3: Qualify Check (lightweight match)

@router.post(
    "/qualify",
    response_model=JobMatchResponse,
    summary="Do I Qualify?",
    description="Quick qualification check — same as /match but semantically clearer.",
)
async def qualify(
    body: MatchJobRequest,
    service: OpenAIService = Depends(get_ai_service),
) -> JobMatchResponse:
    try:
        return await service.match_job(body.cv_text, body.job_description)
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


#  Endpoint 4: Improve CV + Cover Letter 

@router.post(
    "/improve",
    response_model=ImprovedCVResponse,
    summary="Improve CV & Generate Cover Letter",
    description="Rewrites your CV for a specific job and generates a tailored cover letter.",
)
async def improve_cv(
    body: ImproveCVRequest,
    service: OpenAIService = Depends(get_ai_service),
) -> ImprovedCVResponse:
    try:
        return await service.improve_cv_and_generate_cover_letter(
            cv_text=body.cv_text,
            job_description=body.job_description,
            tone=body.tone,
        )
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")