# Legal Document Analyzer

Analyze legal documents with AI. Upload a PDF or image. Get a clear summary, key clauses, and a simple report.

## What it does
- Analyze PDFs and images (with OCR if needed)
- Show key clauses and risks
- Download a report (PDF or JSON)
- Rate limiting enabled; no authentication required

## Tech
- Backend: FastAPI, PyMuPDF, Tesseract OCR, OpenRouter
- Frontend: React + Vite + TypeScript

## Quick start (local)
1) Backend

**Install OCR (required for images):**
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr libmagic1`
- macOS: `brew install tesseract libmagic`
- Windows: Download from [tesseract-ocr](https://github.com/UB-Mannheim/tesseract/wiki)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
set OPENROUTER_API_KEY=your_key_here
python -m uvicorn main:app --reload
```

Verify OCR: `python verify_ocr.py`

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
- Render/Railway/Fly.io (backend):
  - Docker build auto-installs Tesseract OCR
  - Start command: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
  - Env: `OPENROUTER_API_KEY`, `APP_ENV=production`
  - Procfile already included for non-Docker deployments
  - **OCR automatically works in Docker** - no manual setup needed!

## Environment variables
- Backend: `OPENROUTER_API_KEY`, `APP_ENV`, optional: `RATE_LIMIT_*`, `ENABLE_PROMETHEUS`
- Frontend: `VITE_API_URL` (points to backend)

## API (main)
- POST `/analyze` upload file
- GET `/analysis/{file_id}`
- POST `/export/{file_id}/{format}` (pdf|json)
- GET `/documents/{file_id}`
- GET `/health`

## Notes for production
- Set strict `ALLOWED_ORIGINS`
- Use Redis for rate limiting (set `RATE_LIMIT_STORAGE_URI`)
- Enable Prometheus metrics (`ENABLE_PROMETHEUS=true`)
- Logs are JSON and include request IDs
- OCR status logged on startup and available at `/health`

## OCR Troubleshooting
- Check OCR status: `curl https://your-api.com/health`
- View startup logs for OCR detection messages
- See [backend/OCR_SETUP.md](backend/OCR_SETUP.md) for detailed setup guide

## License
MIT
