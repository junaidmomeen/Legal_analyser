# OCR Quick Start Guide

## TL;DR

Image OCR now works automatically in Docker. No setup needed for Render/Fly.io/Railway.

## For Deployment (Docker-based platforms)

```bash
# Just deploy - OCR works automatically!
git push origin main
```

That's it. Tesseract installs automatically during Docker build.

**Verify it works:**
```bash
curl https://your-app.com/health
# Look for: "tesseract_ocr": "enabled"
```

## For Local Development

### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr libmagic1
cd backend
python verify_ocr.py
```

### macOS
```bash
brew install tesseract libmagic
cd backend
python verify_ocr.py
```

### Windows
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location
3. Restart terminal
4. Run: `python verify_ocr.py`

## Check OCR Status

### During Startup
Look for this in logs:
```
✓ Tesseract OCR: tesseract 4.1.1
All services initialized successfully | OCR Status: ENABLED
```

### Via API
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "services": {
    "tesseract_ocr": "enabled",
    "image_processing": "available"
  }
}
```

## Test It

Upload an image with text:
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@test_image.png"
```

Should return extracted text without errors.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| OCR shows "disabled" | Rebuild Docker: `docker-compose build --no-cache` |
| Local: "Tesseract not found" | Install Tesseract (see commands above) |
| Image upload fails | Check file size < 50MB, format is PNG/JPG |

## Documentation

- Full setup guide: `backend/OCR_SETUP.md`
- Deployment checklist: `backend/OCR_VERIFICATION_CHECKLIST.md`
- Change log: `backend/CHANGELOG_OCR.md`
- Deployment summary: `DEPLOYMENT_SUMMARY.md`

## Support

1. Check logs for OCR status messages
2. Run health check endpoint
3. Use `python verify_ocr.py` locally
4. Consult OCR_SETUP.md for details

---

**Ready to deploy!** OCR is pre-configured and will work automatically in Docker environments.
