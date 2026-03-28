from typing import List, Dict, Tuple
import re

# Try sentence-transformers (BERT based — better accuracy)
try:
    from sentence_transformers import SentenceTransformer, util
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    USE_BERT = True
    print("ML: Using BERT sentence-transformers for matching")
except Exception:
    _model = None
    USE_BERT = False
    print("ML: Falling back to TF-IDF matching")

# TF-IDF fallback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class JDMatcher:

    def _normalize_skill(self, skill: str) -> str:
        return skill.lower().strip()

    def _skill_overlap_score(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Tuple[float, List[str], List[str], List[str]]:

        resume_set = {self._normalize_skill(s) for s in resume_skills}
        required_set = {self._normalize_skill(s) for s in required_skills}
        preferred_set = {self._normalize_skill(s) for s in preferred_skills}

        # Strong — exact match in required
        strong = [s for s in resume_skills if self._normalize_skill(s) in required_set]

        # Missing — required skills not in resume
        missing = [s for s in required_skills if self._normalize_skill(s) not in resume_set]

        # Weak — preferred skills not fully matched
        weak = [s for s in preferred_skills if self._normalize_skill(s) not in resume_set]

        # Score calculation
        if required_set:
            required_match = len(required_set - {self._normalize_skill(s) for s in missing}) / len(required_set)
        else:
            required_match = 1.0

        if preferred_set:
            preferred_match = len(preferred_set - {self._normalize_skill(s) for s in weak}) / len(preferred_set)
        else:
            preferred_match = 1.0

        # Required skills = 70% weight, preferred = 30%
        skill_score = (required_match * 0.70 + preferred_match * 0.30) * 100
        return skill_score, strong, weak, missing

    def _text_similarity_score(self, resume_text: str, jd_text: str) -> float:
        if not resume_text or not jd_text:
            return 0.0

        if USE_BERT and _model:
            try:
                emb1 = _model.encode(resume_text[:512], convert_to_tensor=True)
                emb2 = _model.encode(jd_text[:512], convert_to_tensor=True)
                similarity = util.cos_sim(emb1, emb2).item()
                return max(0.0, min(1.0, similarity)) * 100
            except Exception as e:
                print(f"BERT error: {e}, falling back to TF-IDF")

        # TF-IDF fallback
        try:
            vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
            tfidf = vectorizer.fit_transform([resume_text[:2000], jd_text[:2000]])
            score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(score) * 100
        except Exception:
            return 0.0

    def calculate_match(
        self,
        resume_skills: List[str],
        resume_text: str,
        required_skills: List[str],
        preferred_skills: List[str],
        jd_text: str,
    ) -> Dict:

        # Skill-based score (60% weight)
        skill_score, strong, weak, missing = self._skill_overlap_score(
            resume_skills, required_skills, preferred_skills
        )

        # Text similarity score (40% weight)
        text_score = self._text_similarity_score(resume_text, jd_text)

        # Final weighted score
        final_score = round((skill_score * 0.60) + (text_score * 0.40), 1)
        final_score = max(0.0, min(100.0, final_score))

        return {
            "match_score": final_score,
            "strong_skills": strong,
            "weak_skills": weak,
            "missing_skills": missing,
            "score_breakdown": {
                "skill_score": round(skill_score, 1),
                "text_similarity_score": round(text_score, 1),
                "skill_weight": "60%",
                "text_weight": "40%",
            }
        }


# Global instance
jd_matcher = JDMatcher()