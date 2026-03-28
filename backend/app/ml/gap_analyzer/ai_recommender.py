import httpx
import json
from typing import List, Dict
from app.core.config import settings


async def get_ai_recommendation(
    candidate_name: str,
    match_score: float,
    strong_skills: List[str],
    weak_skills: List[str],
    missing_skills: List[str],
    job_title: str,
    experience_years: float,
    min_experience: str
) -> str:
    """Claude API se detailed AI recommendation lo"""

    if not settings.ANTHROPIC_API_KEY:
        return _fallback_recommendation(
            match_score, strong_skills, weak_skills, missing_skills
        )

    prompt = f"""You are an expert HR recruiter. Analyze this candidate for the role of {job_title}.

Candidate Analysis:
- Overall Match Score: {match_score}%
- Experience: {experience_years} years (Required: {min_experience} years)
- Strong Skills: {', '.join(strong_skills) if strong_skills else 'None'}
- Weak/Partial Skills: {', '.join(weak_skills) if weak_skills else 'None'}
- Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}

Provide a concise 3-4 sentence HR recommendation covering:
1. Overall assessment (strong/average/weak candidate)
2. Key strengths to highlight
3. Critical gaps and their impact
4. Final hiring recommendation (interview/reject/consider for junior role)

Be direct and professional. No bullet points, just paragraph."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"].strip()
    except Exception:
        pass

    return _fallback_recommendation(
        match_score, strong_skills, weak_skills, missing_skills
    )


def _fallback_recommendation(
    score: float,
    strong: List[str],
    weak: List[str],
    missing: List[str]
) -> str:
    if score >= 85:
        verdict = "Strong candidate, highly recommended for interview."
    elif score >= 70:
        verdict = "Good candidate, recommended for interview with minor gaps."
    elif score >= 55:
        verdict = "Average candidate, consider for junior role."
    else:
        verdict = "Weak candidate, does not meet minimum requirements."

    parts = [verdict]
    if strong:
        parts.append(f"Strong in: {', '.join(strong[:3])}.")
    if missing:
        parts.append(f"Key gaps: {', '.join(missing[:3])}.")
    return " ".join(parts)