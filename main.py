"""
vibe-resume-ai - AI Resume Analyzer API
Free: 3 analyses/day | Pro: $19/mo unlimited
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import hashlib
import time
from datetime import datetime, timedelta
from collections import defaultdict
import re

app = FastAPI(
    title="vibe-resume-ai",
    description="AI-powered resume analysis, job matching, and improvement suggestions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting storage (in production, use Redis)
rate_limits = defaultdict(list)
PRO_KEYS = set()  # In production, store in database

# Models
class ResumeText(BaseModel):
    text: str
    
class MatchRequest(BaseModel):
    resume_text: str
    job_description: str

class ImproveRequest(BaseModel):
    resume_text: str
    target_role: Optional[str] = None

class AnalysisResponse(BaseModel):
    skills: list[str]
    experience_years: int
    education: list[str]
    strengths: list[str]
    gaps: list[str]
    improvements: list[str]
    overall_score: int
    summary: str

class MatchResponse(BaseModel):
    fit_score: int
    matching_skills: list[str]
    missing_skills: list[str]
    recommendations: list[str]
    verdict: str

class ImproveResponse(BaseModel):
    suggestions: list[dict]
    rewritten_sections: dict
    action_items: list[str]
    priority_order: list[str]

# Rate limiting
def get_client_id(x_api_key: Optional[str] = Header(None), x_forwarded_for: Optional[str] = Header(None)):
    if x_api_key and x_api_key in PRO_KEYS:
        return {"id": x_api_key, "tier": "pro"}
    client_ip = x_forwarded_for.split(",")[0] if x_forwarded_for else "unknown"
    return {"id": hashlib.md5(client_ip.encode()).hexdigest()[:16], "tier": "free"}

def check_rate_limit(client: dict = Depends(get_client_id)):
    if client["tier"] == "pro":
        return client
    
    client_id = client["id"]
    now = datetime.now()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Clean old entries
    rate_limits[client_id] = [t for t in rate_limits[client_id] if t > day_start]
    
    if len(rate_limits[client_id]) >= 3:
        raise HTTPException(
            status_code=429, 
            detail={
                "error": "Daily limit reached (3/day for free tier)",
                "upgrade_url": "https://vibe-resume-ai.onrender.com/pricing",
                "reset_at": (day_start + timedelta(days=1)).isoformat()
            }
        )
    
    rate_limits[client_id].append(now)
    return client

# Text extraction helpers
def extract_text_from_upload(content: bytes, filename: str) -> str:
    """Basic text extraction - extend for PDF support later"""
    if filename.endswith('.txt'):
        return content.decode('utf-8', errors='ignore')
    # For PDF, return placeholder (add PyPDF2 later)
    try:
        text = content.decode('utf-8', errors='ignore')
        if text.strip():
            return text
    except:
        pass
    return content.decode('latin-1', errors='ignore')

def extract_skills(text: str) -> list[str]:
    """Extract skills from resume text"""
    skill_patterns = [
        r'\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Go|Rust|Ruby|PHP|Swift|Kotlin)\b',
        r'\b(React|Vue|Angular|Node\.js|Django|Flask|FastAPI|Spring|Rails)\b',
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Terraform|CI/CD)\b',
        r'\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)\b',
        r'\b(Machine Learning|AI|Deep Learning|NLP|Computer Vision)\b',
        r'\b(Agile|Scrum|Project Management|Leadership|Communication)\b',
        r'\b(Git|Linux|REST API|GraphQL|Microservices)\b',
    ]
    
    skills = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.update([m.title() if len(m) > 3 else m.upper() for m in matches])
    
    return list(skills)[:20]

def estimate_experience(text: str) -> int:
    """Estimate years of experience"""
    year_patterns = [
        r'(\d+)\+?\s*years?\s*(of)?\s*experience',
        r'experience[:\s]+(\d+)\s*years?',
    ]
    for pattern in year_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return min(int(match.group(1)), 30)
    
    # Count year ranges
    years = re.findall(r'20\d{2}', text)
    if len(years) >= 2:
        return min(max(int(max(years)) - int(min(years)), 1), 20)
    return 2

def extract_education(text: str) -> list[str]:
    """Extract education info"""
    education = []
    patterns = [
        r"(Bachelor'?s?|Master'?s?|PhD|Ph\.D|MBA|B\.S\.|M\.S\.|B\.A\.|M\.A\.)[^,\n]*(?:in\s+)?([A-Za-z\s]+)?",
        r"(University|College|Institute)[^,\n]+",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches[:3]:
            if isinstance(m, tuple):
                education.append(" ".join(m).strip())
            else:
                education.append(m.strip())
    return education[:3] if education else ["Not specified"]

# Mock AI analysis (replace with real AI later)
def analyze_resume_ai(text: str) -> AnalysisResponse:
    """AI analysis of resume - currently mock, wire to OpenAI/Claude later"""
    skills = extract_skills(text)
    experience = estimate_experience(text)
    education = extract_education(text)
    
    # Score based on content richness
    base_score = 50
    base_score += min(len(skills) * 3, 20)
    base_score += min(experience * 2, 15)
    base_score += 5 if education[0] != "Not specified" else 0
    base_score += 5 if len(text) > 500 else 0
    base_score += 5 if len(text) > 1500 else 0
    
    strengths = []
    gaps = []
    improvements = []
    
    if len(skills) >= 5:
        strengths.append("Strong technical skill set")
    else:
        gaps.append("Limited technical skills listed")
        improvements.append("Add more specific technical skills with proficiency levels")
    
    if experience >= 3:
        strengths.append(f"Solid {experience} years of experience")
    else:
        improvements.append("Emphasize projects and achievements to compensate for experience")
    
    if "lead" in text.lower() or "manage" in text.lower():
        strengths.append("Leadership experience indicated")
    else:
        gaps.append("No leadership experience mentioned")
        improvements.append("Highlight any team leadership or mentoring experience")
    
    if any(word in text.lower() for word in ["achieved", "increased", "reduced", "delivered"]):
        strengths.append("Good use of action verbs and metrics")
    else:
        gaps.append("Lacks quantifiable achievements")
        improvements.append("Add metrics: 'Increased X by Y%' or 'Reduced Z by N hours'")
    
    if len(text) < 300:
        gaps.append("Resume appears too short")
        improvements.append("Expand with more details about responsibilities and achievements")
    
    return AnalysisResponse(
        skills=skills,
        experience_years=experience,
        education=education,
        strengths=strengths or ["Good foundation"],
        gaps=gaps or ["None identified"],
        improvements=improvements or ["Continue building experience"],
        overall_score=min(base_score, 100),
        summary=f"Resume shows {experience} years of experience with {len(skills)} key skills. "
                f"{'Strong candidate for mid-senior roles.' if base_score >= 70 else 'Good foundation, room for improvement.'}"
    )

def match_resume_ai(resume: str, job_desc: str) -> MatchResponse:
    """Match resume against job description"""
    resume_skills = set(s.lower() for s in extract_skills(resume))
    job_skills = set(s.lower() for s in extract_skills(job_desc))
    
    matching = resume_skills & job_skills
    missing = job_skills - resume_skills
    
    if job_skills:
        fit_score = int((len(matching) / len(job_skills)) * 100)
    else:
        fit_score = 50
    
    # Adjust for experience
    resume_exp = estimate_experience(resume)
    job_exp_match = re.search(r'(\d+)\+?\s*years?', job_desc, re.IGNORECASE)
    if job_exp_match:
        required_exp = int(job_exp_match.group(1))
        if resume_exp >= required_exp:
            fit_score = min(fit_score + 10, 100)
        else:
            fit_score = max(fit_score - 10, 0)
    
    recommendations = []
    if missing:
        recommendations.append(f"Consider gaining experience in: {', '.join(list(missing)[:5])}")
    if fit_score < 50:
        recommendations.append("This role may require skills you don't have yet")
    if fit_score >= 70:
        recommendations.append("Customize your resume to emphasize matching skills")
    
    if fit_score >= 80:
        verdict = "Excellent match! Apply with confidence."
    elif fit_score >= 60:
        verdict = "Good match. Highlight relevant experience in your application."
    elif fit_score >= 40:
        verdict = "Moderate match. Consider upskilling or emphasizing transferable skills."
    else:
        verdict = "Low match. This role may require significant skill development."
    
    return MatchResponse(
        fit_score=fit_score,
        matching_skills=[s.title() for s in matching],
        missing_skills=[s.title() for s in list(missing)[:10]],
        recommendations=recommendations or ["Tailor your application to the specific role"],
        verdict=verdict
    )

def improve_resume_ai(resume: str, target_role: Optional[str]) -> ImproveResponse:
    """Generate improvement suggestions"""
    suggestions = []
    rewritten = {}
    actions = []
    priorities = []
    
    # Check for common issues
    if not re.search(r'\d+%|\$\d+|\d+x', resume):
        suggestions.append({
            "section": "Achievements",
            "issue": "Lacks quantifiable metrics",
            "fix": "Add numbers: percentages, dollar amounts, time saved",
            "example": "Instead of 'Improved performance' → 'Improved API response time by 40%'"
        })
        priorities.append("Add metrics to achievements")
    
    if len(resume) < 500:
        suggestions.append({
            "section": "Overall",
            "issue": "Resume is too brief",
            "fix": "Expand each role with 3-5 bullet points",
            "example": "Include: scope, actions, results for each position"
        })
        priorities.append("Expand content")
    
    if "summary" not in resume.lower() and "objective" not in resume.lower():
        suggestions.append({
            "section": "Summary",
            "issue": "Missing professional summary",
            "fix": "Add a 2-3 sentence summary at the top",
            "example": "Results-driven software engineer with X years of experience in Y, specializing in Z."
        })
        rewritten["summary"] = f"Results-driven professional with {estimate_experience(resume)} years of experience. Skilled in {', '.join(extract_skills(resume)[:5])}. Proven track record of delivering impactful solutions."
        priorities.append("Add professional summary")
    
    skills = extract_skills(resume)
    if len(skills) < 5:
        suggestions.append({
            "section": "Skills",
            "issue": "Skills section needs expansion",
            "fix": "List 10-15 relevant skills, organized by category",
            "example": "Languages: Python, JavaScript | Frameworks: React, FastAPI | Tools: Docker, AWS"
        })
        priorities.append("Expand skills section")
    
    if target_role:
        suggestions.append({
            "section": "Targeting",
            "issue": f"Optimize for {target_role}",
            "fix": f"Research common requirements for {target_role} and align your experience",
            "example": f"Use keywords from {target_role} job postings in your bullet points"
        })
    
    actions = [
        "Review each bullet point - does it show impact?",
        "Add 2-3 metrics to your most recent role",
        "Ensure contact info and LinkedIn are current",
        "Get a peer review before applying",
        "Customize for each application"
    ]
    
    return ImproveResponse(
        suggestions=suggestions or [{"section": "General", "issue": "Resume looks solid", "fix": "Keep it updated", "example": "Review quarterly"}],
        rewritten_sections=rewritten,
        action_items=actions,
        priority_order=priorities or ["Maintain current quality"]
    )

# Endpoints
@app.get("/")
def root():
    return {
        "name": "vibe-resume-ai",
        "version": "1.0.0",
        "docs": "/docs",
        "pricing": {
            "free": "3 analyses per day",
            "pro": "$19/month - unlimited"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    data: ResumeText,
    client: dict = Depends(check_rate_limit)
):
    """Analyze a resume and get skills, gaps, and improvement suggestions"""
    if len(data.text.strip()) < 50:
        raise HTTPException(400, "Resume text too short (minimum 50 characters)")
    
    return analyze_resume_ai(data.text)

@app.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_resume_upload(
    file: UploadFile = File(...),
    client: dict = Depends(check_rate_limit)
):
    """Upload a resume file (PDF or TXT) for analysis"""
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(400, "File too large (max 5MB)")
    
    text = extract_text_from_upload(content, file.filename or "resume.txt")
    if len(text.strip()) < 50:
        raise HTTPException(400, "Could not extract sufficient text from file")
    
    return analyze_resume_ai(text)

@app.post("/match", response_model=MatchResponse)
async def match_resume(
    data: MatchRequest,
    client: dict = Depends(check_rate_limit)
):
    """Match a resume against a job description"""
    if len(data.resume_text.strip()) < 50:
        raise HTTPException(400, "Resume text too short")
    if len(data.job_description.strip()) < 50:
        raise HTTPException(400, "Job description too short")
    
    return match_resume_ai(data.resume_text, data.job_description)

@app.post("/improve", response_model=ImproveResponse)
async def improve_resume(
    data: ImproveRequest,
    client: dict = Depends(check_rate_limit)
):
    """Get specific improvement suggestions for a resume"""
    if len(data.resume_text.strip()) < 50:
        raise HTTPException(400, "Resume text too short")
    
    return improve_resume_ai(data.resume_text, data.target_role)

@app.get("/templates")
def get_templates():
    """Get resume templates and examples"""
    return {
        "templates": [
            {
                "id": "software-engineer",
                "name": "Software Engineer",
                "sections": ["Summary", "Skills", "Experience", "Projects", "Education"],
                "tips": ["Lead with technical skills", "Quantify impact", "Include GitHub/portfolio"]
            },
            {
                "id": "product-manager",
                "name": "Product Manager", 
                "sections": ["Summary", "Experience", "Skills", "Education", "Certifications"],
                "tips": ["Focus on outcomes", "Highlight cross-functional work", "Show data-driven decisions"]
            },
            {
                "id": "data-scientist",
                "name": "Data Scientist",
                "sections": ["Summary", "Skills", "Experience", "Projects", "Publications", "Education"],
                "tips": ["List ML/AI frameworks", "Include model metrics", "Link to notebooks/papers"]
            },
            {
                "id": "designer",
                "name": "UX/UI Designer",
                "sections": ["Summary", "Portfolio", "Experience", "Skills", "Education"],
                "tips": ["Portfolio link is essential", "Show process, not just outcomes", "Include user research experience"]
            }
        ]
    }

@app.get("/pricing")
def pricing():
    """Get pricing information"""
    return {
        "plans": [
            {
                "name": "Free",
                "price": 0,
                "limits": "3 analyses per day",
                "features": ["Resume analysis", "Job matching", "Basic suggestions"]
            },
            {
                "name": "Pro",
                "price": 19,
                "period": "month",
                "limits": "Unlimited",
                "features": [
                    "Unlimited analyses",
                    "Priority processing", 
                    "AI-powered rewriting",
                    "ATS optimization",
                    "API access",
                    "Email support"
                ],
                "signup_url": "https://buy.stripe.com/vibe-resume-ai-pro"  # Replace with real Stripe link
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
