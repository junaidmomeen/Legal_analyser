# Legal Document Analyzer - Setup Guide

This guide will walk you through setting up and running the Legal Document Analyzer project.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (recommended for easy setup)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for local development)
- **Git** (for cloning the repository)

## 🚀 Quick Start with Docker (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/legal-analyzer.git
cd legal-analyzer
```

### 2. Set Up Environment Variables

#### Backend Environment (.env)
Create `backend/.env` file with the following content:

```env
# Legal Document Analyzer - Backend Environment Configuration

# =============================================================================
# REQUIRED SETTINGS
# =============================================================================

# OpenRouter API Key for AI analysis
# Get your API key from: https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here

# JWT Secret for authentication
# Generate a secure random string for production
JWT_SECRET=your_super_secure_jwt_secret_key_change_this_in_production

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Application environment (development, staging, production)
APP_ENV=development

# Logging configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# API version
API_VERSION=1.1.0

# =============================================================================
# DATABASE & CACHING
# =============================================================================

# Redis URL for caching and session storage
REDIS_URL=redis://redis:6379/0

# =============================================================================
# FILE PROCESSING SETTINGS
# =============================================================================

# Temporary storage path for uploaded files
TEMP_STORAGE_PATH=temp_uploads

# Maximum file size in MB
MAX_FILE_SIZE_MB=50
MAX_FILE_SIZE=50

# Maximum image dimensions
MAX_IMAGE_DIMENSION=2000

# =============================================================================
# RETENTION & CLEANUP SETTINGS
# =============================================================================

# Cleanup interval in hours
CLEANUP_INTERVAL_HOURS=1

# Cache retention in hours
CACHE_RETENTION_HOURS=24

# Maximum concurrent analyses
MAX_CONCURRENT_ANALYSES=5

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# CORS settings
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080
ALLOW_CREDENTIALS=false

# =============================================================================
# EXPORT SETTINGS
# =============================================================================

# Export URL token time-to-live in seconds (5 minutes)
EXPORT_URL_TTL=300

# =============================================================================
# RATE LIMITING
# =============================================================================

# Rate limiting settings (requests per minute)
RATE_LIMIT_REQUESTS_PER_MINUTE=10

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

# Enable debug mode (only for development)
DEBUG=false

# Enable hot reload (only for development)
RELOAD=false

# =============================================================================
# PRODUCTION SETTINGS
# =============================================================================

# Server host (0.0.0.0 for Docker, 127.0.0.1 for local)
HOST=0.0.0.0

# Server port
PORT=8000

# Number of worker processes (for production)
WORKERS=4

# =============================================================================
# OPTIONAL SETTINGS
# =============================================================================

# Custom AI model (default: openai/gpt-4o-mini)
AI_MODEL=openai/gpt-4o-mini

# Retry delay for AI requests in seconds
RETRY_DELAY=2

# Enable AI provider interface
ENABLE_AI_PROVIDER_INTERFACE=true
```

#### Frontend Environment (.env)
Create `frontend/.env` file with the following content:

```env
# Legal Document Analyzer - Frontend Environment Configuration

# =============================================================================
# REQUIRED SETTINGS
# =============================================================================

# Backend API URL
VITE_API_URL=http://localhost:8000

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Application environment
NODE_ENV=development

# Application title
VITE_APP_TITLE=Legal Document Analyzer

# Application description
VITE_APP_DESCRIPTION=AI-powered legal document analysis platform

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Enable debug mode
VITE_DEBUG=false

# Enable development tools
VITE_DEV_TOOLS=false

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

# Default language
VITE_DEFAULT_LANGUAGE=en

# Supported languages
VITE_SUPPORTED_LANGUAGES=en,es,fr,de

# =============================================================================
# UI SETTINGS
# =============================================================================

# Default theme
VITE_DEFAULT_THEME=dark

# Enable animations
VITE_ENABLE_ANIMATIONS=true

# =============================================================================
# ANALYTICS (Optional)
# =============================================================================

# Google Analytics ID (optional)
# VITE_GA_ID=your_google_analytics_id

# =============================================================================
# PRODUCTION SETTINGS
# =============================================================================

# Build optimization
VITE_BUILD_OPTIMIZE=true

# Source map generation (disable in production)
VITE_GENERATE_SOURCEMAP=false
```

### 3. Get Your OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Replace `your_openrouter_api_key_here` in `backend/.env` with your actual API key

### 4. Start the Application

#### Development Mode
```bash
# Start development environment with hot reload
docker-compose -f docker-compose.dev.yml up --build
```

#### Production Mode
```bash
# Start production environment
docker-compose up --build
```

### 5. Access the Application

- **Frontend**: http://localhost:5173 (dev) or http://localhost:3000 (prod)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Local Development Setup

If you prefer to run the application locally without Docker:

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy content from above)
# Edit the .env file with your API key

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (copy content from above)

# Start the development server
npm run dev
```

### 3. Redis Setup (Required)

You'll need Redis running for the backend to work:

#### Option A: Docker Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

#### Option B: Local Redis Installation
- **Windows**: Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- **macOS**: `brew install redis && brew services start redis`
- **Linux**: `sudo apt-get install redis-server && sudo systemctl start redis`

## 🔧 Available Commands

### Using Makefile
```bash
make help              # Show all available commands
make dev               # Start development environment
make test              # Run all tests
make lint              # Run code linting
make format            # Format code
make build             # Build applications
make docker-build      # Build Docker images
make clean             # Clean build artifacts
make security-check    # Run security scans
```

### Using Docker Compose
```bash
# Development
docker-compose -f docker-compose.dev.yml up --build
docker-compose -f docker-compose.dev.yml down

# Production
docker-compose up --build
docker-compose down

# View logs
docker-compose logs -f
```

### Using npm/yarn (Frontend)
```bash
npm run dev            # Start development server
npm run build          # Build for production
npm run test           # Run tests
npm run lint           # Run linting
npm run format         # Format code
```

### Using Python (Backend)
```bash
python -m uvicorn main:app --reload    # Development server
pytest                                 # Run tests
black .                                # Format code
flake8 .                               # Lint code
```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Backend Tests Only
```bash
cd backend
pytest -v --cov=. --cov-report=html
```

### Frontend Tests Only
```bash
cd frontend
npm test -- --coverage
```

### Integration Tests
```bash
# Start the application first
docker-compose -f docker-compose.dev.yml up -d

# Run integration tests
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## 🔒 Security Configuration

### JWT Secret Generation
Generate a secure JWT secret:
```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

### Environment Security
- Never commit `.env` files to version control
- Use different secrets for development and production
- Rotate secrets regularly in production

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8000
netstat -tulpn | grep :5173

# Kill the process or use different ports
```

#### 2. Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
docker run -d -p 6379:6379 redis:7-alpine
```

#### 3. API Key Issues
- Ensure your OpenRouter API key is valid
- Check if you have sufficient credits
- Verify the API key is correctly set in `.env`

#### 4. File Upload Issues
- Check file size limits in `.env`
- Ensure `temp_uploads` directory exists
- Verify file permissions

### Debug Mode
Enable debug mode in `backend/.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 Monitoring

### Health Checks
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000/health

### Logs
```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Local logs
tail -f backend/logs/backend.log
```

### System Status
```bash
make status
```

## 🚀 Production Deployment

### Environment Variables for Production
Update your `.env` files for production:

```env
# Backend Production Settings
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Frontend Production Settings
NODE_ENV=production
VITE_DEBUG=false
VITE_GENERATE_SOURCEMAP=false
```

### Build and Deploy
```bash
# Build production images
docker-compose build

# Deploy
docker-compose up -d

# Check status
docker-compose ps
```

## 📝 Next Steps

1. **Get your OpenRouter API key** from https://openrouter.ai/
2. **Create the environment files** as shown above
3. **Start the application** using Docker or local setup
4. **Upload a legal document** to test the analysis
5. **Check the API documentation** at http://localhost:8000/docs

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all environment variables are set correctly
4. Verify all dependencies are installed
5. Check the GitHub Issues for known problems

## 📚 Additional Resources

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [OpenRouter Documentation](https://openrouter.ai/docs) - AI provider docs
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Backend framework
- [React Documentation](https://react.dev/) - Frontend framework
- [Tailwind CSS Documentation](https://tailwindcss.com/) - Styling framework
