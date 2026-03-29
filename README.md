# HireAI — Smart Resume Analyzer & Hiring Platform

An AI-powered hiring platform that automatically matches resumes with job descriptions using ML, provides gap analysis, and streamlines the recruitment process.

## Live Demo

- **Frontend:** https://hireai-frontend-ek72.onrender.com
- **Backend API:** https://hireai-backend-fbxa.onrender.com
- **API Docs:** https://hireai-backend-fbxa.onrender.com/api/docs

## Features

### For HR
- Post job descriptions with required skills
- View all applicants with ML match scores (0-100%)
- See skill gap analysis — Strong, Weak, Missing skills
- AI-powered candidate recommendations
- Update application status (Shortlisted, Interview, Selected, Rejected)
- Real-time notifications when someone applies

### For Applicants
- Browse available jobs
- Upload resume (PDF/DOCX) — auto-parsed by ML
- Apply for jobs — instant match score generated
- View skill gaps and AI feedback
- Real-time notifications for status updates

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT + bcrypt |
| ML Engine | scikit-learn (TF-IDF) + BERT (local) |
| Resume Parsing | pdfminer + python-docx |
| AI Recommendations | Claude/OpenAI API |
| Frontend | React + TypeScript + Vite |
| Styling | Tailwind CSS |
| State Management | Zustand |
| Deployment | Render (free tier) |

## Project Structure
```
hireai/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST API routes
│   │   ├── core/                # Config, DB, Security
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── ml/                  # ML Engine
│   │       ├── parsers/         # Resume parser
│   │       ├── matchers/        # JD matcher (TF-IDF/BERT)
│   │       └── gap_analyzer/    # Gap analysis + AI
│   ├── tests/                   # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/          # Reusable UI components
    │   ├── pages/               # HR & Applicant dashboards
    │   ├── store/               # Zustand state
    │   └── api/                 # Axios client
    └── package.json
```

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop

### Backend
```bash
# Clone karo
git clone https://github.com/ranjan781/hireai.git
cd hireai/backend

# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Dependencies install
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# .env file mein apni values fill karo

# Database start (Docker)
docker compose up postgres redis -d

# Server start
uvicorn main:app --reload
```

API docs: http://localhost:8000/api/docs

### Frontend
```bash
cd hireai/frontend
npm install
npm run dev
```

App: http://localhost:5173

### Run Tests
```bash
cd backend
pytest tests/ -v
# 18/18 tests pass
```

## ML Engine

### Resume Parser
- PDF aur DOCX files se text extract karta hai
- Skills dictionary se 50+ technologies detect karta hai
- Experience years automatically calculate karta hai
- Contact info (email, phone, LinkedIn, GitHub) extract karta hai

### JD Matching
- **Local:** BERT (sentence-transformers) — high accuracy
- **Production:** TF-IDF — memory efficient
- Skill overlap score: Required (70%) + Preferred (30%)
- Text similarity score: Cosine similarity
- Final score: Skills (60%) + Text (40%)

### Gap Analyzer
- Strong skills — JD se match
- Weak skills — Preferred skills jo nahi hain
- Missing skills — Required skills jo nahi hain
- Grade: A (85%+), B (70%+), C (55%+), D (40%+), F
- AI recommendation generate karta hai

## API Endpoints
```
POST /api/v1/auth/register    — Register
POST /api/v1/auth/login       — Login
GET  /api/v1/jobs             — Jobs list
POST /api/v1/jobs             — Create job (HR)
POST /api/v1/resumes/upload   — Upload resume
POST /api/v1/applications/apply — Apply for job
GET  /api/v1/applications/my  — My applications
GET  /api/v1/notifications    — Notifications
```

## Environment Variables
```env
APP_NAME=HireAI
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://localhost:6379/0
USE_BERT=true  # false for production (memory saving)
ANTHROPIC_API_KEY=optional
ALLOWED_ORIGINS=["http://localhost:5173"]
```

## Deployment

Deployed on **Render** (free tier):
- Backend: Docker container
- Frontend: Static site
- Database: PostgreSQL (free)

Auto-deploy on `git push origin main`

## Screenshots

### HR Dashboard
- Overview with active jobs and applicants
- Job postings with skill tags
- Applicant table with ML scores and skill gap analysis

### Applicant Dashboard  
- Browse jobs with required skills
- Resume upload with auto skill extraction
- Applications with match scores and AI feedback

## Author

**Rajesh** — Built from scratch as a production-level portfolio project

- GitHub: https://github.com/ranjan781
- Project: https://hireai-frontend-ek72.onrender.com