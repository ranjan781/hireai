import re
from pathlib import Path
from typing import List, Dict, Any

# PDF parsing
try:
    from pdfminer.high_level import extract_text as pdf_extract
except ImportError:
    pdf_extract = None

# DOCX parsing
try:
    from docx import Document
except ImportError:
    Document = None

import spacy

# spaCy model load — ek baar load hoga memory mein
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = None

# ─── Skill Dictionary ───────────────────────────────────────────────
SKILLS_DB = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "kotlin", "swift", "php", "ruby", "scala", "r", "matlab",

    # Web Frameworks
    "fastapi", "django", "flask", "express", "react", "angular", "vue",
    "nextjs", "nestjs", "spring", "laravel", "rails",

    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
    "sqlite", "oracle", "dynamodb", "firebase",

    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux",

    # ML & Data Science
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "opencv", "nlp", "computer vision",
    "data analysis", "data science", "tableau", "power bi",

    # APIs & Architecture
    "rest api", "graphql", "microservices", "grpc", "websockets",
    "message queue", "kafka", "rabbitmq", "celery",

    # Tools
    "git", "github", "gitlab", "jira", "postman", "figma", "linux",
    "bash", "powershell", "vim",

    # Soft Skills (optional)
    "agile", "scrum", "team leadership", "problem solving",
}

# ─── Experience Patterns ────────────────────────────────────────────
EXPERIENCE_PATTERNS = [
    r'(\d+)\+?\s*years?\s*of\s*(?:work\s*)?experience',
    r'(\d+)\+?\s*years?\s*(?:in|of)\s*(?:software|development|engineering)',
    r'experience\s*(?:of|:)?\s*(\d+)\+?\s*years?',
    r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:exp|experience)',
]

# ─── Main Parser Class ──────────────────────────────────────────────
class ResumeParser:

    def extract_text(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        try:
            if ext == ".pdf" and pdf_extract:
                return pdf_extract(file_path) or ""
            elif ext in [".docx", ".doc"] and Document:
                doc = Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Text extraction error: {e}")
        return ""

    def extract_skills(self, text: str) -> List[str]:
        text_lower = text.lower()
        found = set()

        # Direct match from skills DB
        for skill in SKILLS_DB:
            # Word boundary check
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill.title())

        # spaCy NER se bhi kuch skills nikal sakte hain
        if nlp:
            doc = nlp(text[:5000])  # first 5000 chars process karo
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT"] and len(ent.text) > 2:
                    ent_lower = ent.text.lower()
                    if ent_lower in SKILLS_DB:
                        found.add(ent.text.title())

        return sorted(list(found))

    def extract_experience_years(self, text: str) -> float:
        text_lower = text.lower()
        years_found = []

        for pattern in EXPERIENCE_PATTERNS:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years_found.append(float(match))
                except:
                    pass

        if years_found:
            return max(years_found)  # highest mention return karo

        # Fallback: work history dates se calculate karo
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            years_int = [int(y) for y in years]
            span = max(years_int) - min(years_int)
            return float(min(span, 20))  # max 20 years cap

        return 0.0

    def extract_contact(self, text: str) -> Dict[str, str]:
        contact = {}

        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact["email"] = email_match.group()

        # Phone
        phone_match = re.search(r'(?:\+91|0)?[6-9]\d{9}|\+?\d[\d\s\-]{8,12}\d', text)
        if phone_match:
            contact["phone"] = phone_match.group().strip()

        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group()

        # GitHub
        github_match = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
        if github_match:
            contact["github"] = github_match.group()

        return contact

    def parse(self, file_path: str) -> Dict[str, Any]:
        text = self.extract_text(file_path)

        if not text.strip():
            return {
                "raw_text": "",
                "extracted_skills": [],
                "extracted_experience_years": 0.0,
                "extracted_education": [],
                "contact_info": {},
                "error": "Could not extract text from file"
            }

        skills = self.extract_skills(text)
        experience = self.extract_experience_years(text)
        contact = self.extract_contact(text)

        return {
            "raw_text": text,
            "extracted_skills": skills,
            "extracted_experience_years": experience,
            "extracted_education": [],
            "contact_info": contact,
        }


# Global instance — ek baar banao, baar baar use karo
resume_parser = ResumeParser()