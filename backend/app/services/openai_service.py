import json
import re
from openai import AsyncOpenAI

from app.config import Settings
from app.models import (
    CVAnalysisResponse,
    JobMatchResponse,
    ImprovedCVResponse,
)


class OpenAIService:
    """Wrapper around the OpenAI API with structured output parsing."""

    def __init__(self, settings: Settings):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def _chat(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a chat completion request.
        Returns the raw text content of the assistant's reply.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,  # Lower = more consistent, factual output
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """
        Safely extract a JSON object from the model's response.
        Handles cases where the model wraps JSON in markdown code fences.
        """
        # Strip ```json ... ``` fences if present
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)


    async def analyze_cv(self, cv_text: str) -> CVAnalysisResponse:
        """Extract structured profile data from a CV."""
        system = """You are an expert HR analyst and career coach.
Analyze the provided CV and return ONLY a JSON object with this exact structure:
{
  "summary": "2-3 sentence profile summary",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "skills": ["skill1", "skill2", ...],
  "experience_years": "e.g. 3-5 years",
  "seniority_level": "Junior | Mid | Senior | Lead | Executive"
}
No extra text. Only valid JSON."""

        user = f"Analyze this CV:\n\n{cv_text}"
        raw = await self._chat(system, user)
        data = self._parse_json(raw)
        return CVAnalysisResponse(**data)

    async def match_job(self, cv_text: str, job_description: str) -> JobMatchResponse:
        """Score how well a CV matches a job description."""
        system = """You are a senior technical recruiter.
Compare the CV against the job description and return ONLY a JSON object:
{
  "match_score": <integer 0-100>,
  "qualifies": <true|false>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "recommendation": "Apply now | Improve first | Not a good fit",
  "reasoning": "2-3 sentences explaining the score"
}
Be honest and precise. Only return valid JSON."""

        user = f"CV:\n{cv_text}\n\n---\n\nJob Description:\n{job_description}"
        raw = await self._chat(system, user)
        data = self._parse_json(raw)
        return JobMatchResponse(**data)

    async def improve_cv_and_generate_cover_letter(
        self,
        cv_text: str,
        job_description: str,
        tone: str,
    ) -> ImprovedCVResponse:
        """Rewrite the CV for a specific job and generate a matching cover letter."""
        system = f"""You are an expert CV writer and career coach.
Your task is to:
1. Rewrite and improve the CV to better match the job description
2. Write a compelling cover letter (tone: {tone})

Return ONLY a JSON object with this structure:
{{
  "improved_cv": "Full rewritten CV text here...",
  "cover_letter": "Full cover letter text here...",
  "changes_made": ["change1", "change2", "change3", ...]
}}

Guidelines:
- Keep the CV truthful — enhance wording, don't fabricate experience
- Highlight relevant skills and tailor bullet points to the job
- Cover letter should be 3-4 paragraphs, address the company's needs
- Only return valid JSON"""

        user = (
            f"Original CV:\n{cv_text}\n\n"
            f"---\n\nJob Description:\n{job_description}"
        )
        raw = await self._chat(system, user)
        data = self._parse_json(raw)
        return ImprovedCVResponse(**data)