# 🚀 vibe-resume-ai

AI-powered Resume Analyzer API. Get instant feedback on your resume, match against job descriptions, and receive actionable improvement suggestions.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 💰 Pricing

| Plan | Price | Limits |
|------|-------|--------|
| **Free** | $0 | 3 analyses/day |
| **Pro** | $19/mo | Unlimited |

## 🔌 API Endpoints

### `POST /analyze`
Analyze a resume and get skills, gaps, and improvements.

```bash
curl -X POST https://vibe-resume-ai.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your resume text here..."}'
```

**Response:**
```json
{
  "skills": ["Python", "React", "AWS"],
  "experience_years": 5,
  "education": ["BS Computer Science"],
  "strengths": ["Strong technical skill set"],
  "gaps": ["No leadership experience mentioned"],
  "improvements": ["Add metrics to achievements"],
  "overall_score": 75,
  "summary": "Resume shows 5 years of experience..."
}
```

### `POST /analyze/upload`
Upload a resume file (PDF/TXT).

```bash
curl -X POST https://vibe-resume-ai.onrender.com/analyze/upload \
  -F "file=@resume.pdf"
```

### `POST /match`
Match resume against a job description.

```bash
curl -X POST https://vibe-resume-ai.onrender.com/match \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume...",
    "job_description": "We are looking for..."
  }'
```

**Response:**
```json
{
  "fit_score": 72,
  "matching_skills": ["Python", "AWS"],
  "missing_skills": ["Kubernetes", "Go"],
  "recommendations": ["Consider gaining experience in..."],
  "verdict": "Good match. Highlight relevant experience."
}
```

### `POST /improve`
Get specific improvement suggestions.

```bash
curl -X POST https://vibe-resume-ai.onrender.com/improve \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume...",
    "target_role": "Senior Software Engineer"
  }'
```

### `GET /templates`
Get resume templates and tips.

```bash
curl https://vibe-resume-ai.onrender.com/templates
```

## 🔑 API Keys (Pro)

Include your API key in requests:

```bash
curl -X POST https://vibe-resume-ai.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-pro-key" \
  -d '{"text": "..."}'
```

## 🛠️ Self-Hosting

### Docker

```bash
docker build -t vibe-resume-ai .
docker run -p 8000:8000 vibe-resume-ai
```

### Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📚 API Docs

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## 🗺️ Roadmap

- [ ] Real AI analysis (OpenAI/Claude integration)
- [ ] PDF text extraction (PyPDF2)
- [ ] ATS compatibility scoring
- [ ] Resume rewriting suggestions
- [ ] LinkedIn profile import
- [ ] Stripe payment integration

## 📝 License

MIT

---

Built with ❤️ using FastAPI
