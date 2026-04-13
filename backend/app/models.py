"""
Pydantic models for request validation and response shaping.
FastAPI uses these to auto-validate inputs and generate API docs.
"""
from pydantic import BaseModel, Field


# ── Request Models ────────────────────────────────────────────────────────────

class AnalyzeCVRequest(BaseModel):
    cv_text: str = Field(
        ...,
        min_length=50,
        description="The full text content of your CV/resume.",
        examples=["John Doe\nSoftware Engineer\n5 years experience in Python..."],
    )


class MatchJobRequest(BaseModel):
    cv_text: str = Field(..., min_length=50, description="Your CV text.")
    job_description: str = Field(
        ...,
        min_length=20,
        description="The full job posting text.",
        examples=["We are hiring a Senior Python Developer..."],
    )


class ImproveCVRequest(BaseModel):
    cv_text: str = Field(..., min_length=50, description="Your current CV text.")
    job_description: str = Field(
        ...,
        min_length=20,
        description="The job description to tailor the CV toward.",
    )
    tone: str = Field(
        default="professional",
        description="Tone for the cover letter.",
        pattern="^(professional|enthusiastic|concise)$",
    )


# ── Response Models ───────────────────────────────────────────────────────────

class CVAnalysisResponse(BaseModel):
    summary: str = Field(description="Short summary of the candidate's profile.")
    strengths: list[str] = Field(description="Key strengths found in the CV.")
    weaknesses: list[str] = Field(description="Areas that could be improved.")
    skills: list[str] = Field(description="Technical and soft skills identified.")
    experience_years: str = Field(description="Estimated years of experience.")
    seniority_level: str = Field(description="e.g. Junior, Mid, Senior, Lead.")


class JobMatchResponse(BaseModel):
    match_score: int = Field(description="Match percentage from 0 to 100.", ge=0, le=100)
    qualifies: bool = Field(description="True if the candidate meets the core requirements.")
    matching_skills: list[str] = Field(description="Skills the candidate has that the job requires.")
    missing_skills: list[str] = Field(description="Skills the job requires that are missing from CV.")
    recommendation: str = Field(description="Short advice: apply, improve first, or skip.")
    reasoning: str = Field(description="Explanation of the match score.")


class ImprovedCVResponse(BaseModel):
    improved_cv: str = Field(description="The rewritten, tailored CV text.")
    cover_letter: str = Field(description="A custom cover letter for this specific job.")
    changes_made: list[str] = Field(description="List of improvements made to the original CV.")


class HealthResponse(BaseModel):
    status: str
    environment: str
    model: str