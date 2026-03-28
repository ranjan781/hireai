from typing import List, Dict


def generate_recommendation(
    match_score: float,
    strong_skills: List[str],
    weak_skills: List[str],
    missing_skills: List[str],
    experience_years: float,
    min_experience: str = "0"
) -> str:
    try:
        min_exp = float(str(min_experience).replace("+", "").strip())
    except Exception:
        min_exp = 0.0

    if match_score >= 85:
        verdict = "Strong candidate"
        action = "Highly recommended for interview"
    elif match_score >= 70:
        verdict = "Good candidate"
        action = "Recommended for interview with minor gaps"
    elif match_score >= 55:
        verdict = "Average candidate"
        action = "Consider for junior role or re-evaluate after upskilling"
    else:
        verdict = "Weak candidate"
        action = "Does not meet minimum requirements for this role"

    parts = [f"{verdict}. Overall match score: {match_score}%."]

    if strong_skills:
        parts.append(f"Strong in: {', '.join(strong_skills[:4])}.")
    if weak_skills:
        parts.append(f"Needs improvement in: {', '.join(weak_skills[:3])}.")
    if missing_skills:
        parts.append(f"Missing critical skills: {', '.join(missing_skills[:4])}.")

    exp_gap = min_exp - experience_years
    if exp_gap > 1:
        parts.append(f"Experience gap: {exp_gap:.1f} years below requirement.")

    parts.append(action + ".")
    return " ".join(parts)


def analyze_gap(
    match_result: Dict,
    experience_years: float = 0.0,
    min_experience: str = "0"
) -> Dict:
    score = match_result.get("match_score", 0.0)
    strong = match_result.get("strong_skills", [])
    weak = match_result.get("weak_skills", [])
    missing = match_result.get("missing_skills", [])

    if score >= 85:
        grade = "A"
        grade_label = "Excellent"
    elif score >= 70:
        grade = "B"
        grade_label = "Good"
    elif score >= 55:
        grade = "C"
        grade_label = "Average"
    elif score >= 40:
        grade = "D"
        grade_label = "Below Average"
    else:
        grade = "F"
        grade_label = "Poor"

    recommendation = generate_recommendation(
        score, strong, weak, missing,
        experience_years, min_experience
    )

    upskill_suggestions = []
    for skill in (missing + weak)[:5]:
        upskill_suggestions.append({
            "skill": skill,
            "resource": f"Search '{skill} tutorial' on YouTube or Udemy",
            "priority": "High" if skill in missing else "Medium"
        })

    return {
        "match_score": score,
        "grade": grade,
        "grade_label": grade_label,
        "strong_skills": strong,
        "weak_skills": weak,
        "missing_skills": missing,
        "ai_recommendation": recommendation,
        "upskill_suggestions": upskill_suggestions,
        "score_breakdown": match_result.get("score_breakdown", {})
    }