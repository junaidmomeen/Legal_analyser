# Running Legal Document Analyzer Without Redis

This guide shows you how to run the Legal Document Analyzer without Redis dependency. The application will use in-memory storage instead.

## 🚀 Quick Start (No Redis Required)

### Option 1: Windows Users

1. **Run the setup script:**
   ```cmd
   run-without-redis.bat
   ```

2. **Get your OpenRouter API key:**
   - Visit https://openrouter.ai/
   - Sign up and get your API key
   - Edit `backend/.env` and replace `your_openrouter_api_key_here` with your actual key

3. **The backend will start automatically at:**
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Linux/macOS Users

1. **Run the setup script:**
   ```bash
   ./run-without-redis.sh
   ```

2. **Get your OpenRouter API key:**
   - Visit https://openrouter.ai/
   - Sign up and get your API key
   - Edit `backend/.env` and replace `your_openrouter_api_key_here` with your actual key

3. **The backend will start automatically at:**
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 3: Docker (No Redis)

1. **Create environment files:**
   ```bash
   # Copy the content from the scripts above or create manually
   # backend/.env
   # frontend/.env
   ```

2. **Start with Docker:**
   ```bash
   docker-compose -f docker-compose.no-redis.yml up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 Manual Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy content from scripts above)
# Edit with your OpenRouter API key

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup (Optional)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (copy content from scripts above)

# Start the development server
npm run dev
```

## 📋 Environment Variables (No Redis)

### Backend (.env)
```env
# REQUIRED - Get from https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here

# REQUIRED - Generate a secure secret
JWT_SECRET=your_super_secure_jwt_secret_key_change_this_in_production

# Application settings
APP_ENV=development
LOG_LEVEL=INFO
API_VERSION=1.1.0

# File processing
MAX_FILE_SIZE_MB=50
TEMP_STORAGE_PATH=temp_uploads

# Rate limiting (in-memory)
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Redis is disabled - using in-memory storage
# REDIS_URL=redis://redis:6379/0
# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/1
```

### Frontend (.env)
```env
# REQUIRED
VITE_API_URL=http://localhost:8000

# Optional settings
NODE_ENV=development
VITE_DEFAULT_LANGUAGE=en
VITE_DEFAULT_THEME=dark
```

## 🔍 What Works Without Redis

✅ **Fully Functional:**
- Document upload and processing
- AI analysis with OpenRouter
- File validation and OCR
- Report generation (PDF/JSON)
- Authentication with JWT
- Rate limiting (in-memory)
- API endpoints
- Health checks

⚠️ **Limited Functionality:**
- Rate limiting resets on server restart
- No persistent caching across restarts
- Background tasks run synchronously
- No distributed task queue

## 🧪 Testing

### Test the Backend
```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/

# Supported formats
curl http://localhost:8000/supported-formats
```

### Test with a Document
1. Go to http://localhost:8000/docs
2. Use the interactive API documentation
3. Upload a PDF or image file
4. Get the analysis results

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 8000
netstat -tulpn | grep :8000

# Use a different port
python -m uvicorn main:app --reload --port 8001
```

#### 2. API Key Issues
- Ensure your OpenRouter API key is valid
- Check if you have sufficient credits
- Verify the API key is correctly set in `.env`

#### 3. File Upload Issues
- Check file size limits in `.env`
- Ensure `temp_uploads` directory exists
- Verify file permissions

#### 4. Import Errors
```bash
# Make sure all dependencies are installed
pip install -r backend/requirements.txt

# Check Python version (3.11+ required)
python --version
```

### Debug Mode
Enable debug mode in `backend/.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 Monitoring

### Health Checks
- Backend: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs

### Logs
```bash
# View logs in real-time
tail -f backend/logs/backend.log

# Or check the console output
```

## 🚀 Production Considerations

For production use without Redis, consider:

1. **Use a reverse proxy** (nginx) for better performance
2. **Implement file-based caching** for better persistence
3. **Use a proper database** for storing analysis results
4. **Add monitoring and logging** for better observability

## 📝 Next Steps

1. **Get your OpenRouter API key** from https://openrouter.ai/
2. **Run the setup script** for your platform
3. **Update the API key** in `backend/.env`
4. **Start the application** and test with a document
5. **Check the API documentation** at http://localhost:8000/docs

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all environment variables are set correctly
4. Verify all dependencies are installed
5. Check the GitHub Issues for known problems

---

**Note:** This setup is perfect for development and testing. For production use, consider adding Redis for better performance and scalability.
