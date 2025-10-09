# Legal Document Analyzer

Analyze legal documents with AI. Upload a PDF or image. Get a clear summary, key clauses, and a simple report.

## What it does
- Analyze PDFs and images (with OCR if needed)
- Show key clauses and risks
- Download a report (PDF or JSON)
- Works with JWT auth and rate limits

## Tech
- Backend: FastAPI, PyMuPDF, Tesseract OCR, OpenRouter
- Frontend: React + Vite + TypeScript

## Quick start (local)
1) Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
set OPENROUTER_API_KEY=your_key_here
set JWT_SECRET=32+_char_secure_secret
python -m uvicorn main:app --reload
```

2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (frontend) and http://localhost:8000/docs (API).

## Run with Docker
1) Create env file for backend (at `backend/.env`):
```
OPENROUTER_API_KEY=your_openrouter_key
JWT_SECRET=32+_char_secure_secret
APP_ENV=production
LOG_LEVEL=INFO
```

2) Build and start
```bash
docker compose up --build
```

3) Open
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

If your backend URL is different, set `VITE_API_URL` for the frontend container in `docker-compose.yml`.

## Deploy (free-tier friendly)
- Vercel (frontend):
  - Set `VITE_API_URL` to your backend URL
  - Build: `npm run build`, Output: `dist`
- Render/Railway (backend):
  - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
  - Env: `OPENROUTER_API_KEY`, `JWT_SECRET` (32+ chars), `APP_ENV=production`
  - Procfile already included: `web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`

## Environment variables
- Backend: `OPENROUTER_API_KEY`, `JWT_SECRET`, `APP_ENV`, optional: `RATE_LIMIT_*`, `ENABLE_PROMETHEUS`
- Frontend: `VITE_API_URL` (points to backend)

## API (main)
- POST `/analyze` upload file
- GET `/analysis/{file_id}`
- POST `/export/{file_id}/{format}` (pdf|json)
- GET `/documents/{file_id}`
- GET `/health`

## Notes for production
- Use long, random `JWT_SECRET`
- Set strict `ALLOWED_ORIGINS`
- Use Redis for rate limiting (set `RATE_LIMIT_STORAGE_URI`)
- Enable Prometheus metrics (`ENABLE_PROMETHEUS=true`)
- Logs are JSON and include request IDs

## License
MIT
