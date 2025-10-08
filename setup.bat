@echo off
REM Legal Document Analyzer - Quick Setup Script for Windows
REM This script helps you set up the project quickly on Windows

echo 🚀 Legal Document Analyzer - Quick Setup
echo ========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker Compose not found, trying 'docker compose'
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Docker Compose is required
        pause
        exit /b 1
    )
)

echo [SUCCESS] Docker and Docker Compose are available

REM Create backend .env file
if not exist "backend\.env" (
    echo [INFO] Creating backend/.env...
    (
        echo # Legal Document Analyzer - Backend Environment Configuration
        echo.
        echo # =============================================================================
        echo # REQUIRED SETTINGS
        echo # =============================================================================
        echo.
        echo # OpenRouter API Key for AI analysis
        echo # Get your API key from: https://openrouter.ai/
        echo OPENROUTER_API_KEY=your_openrouter_api_key_here
        echo.
        echo # JWT Secret for authentication
        echo # Generate a secure random string for production
        echo JWT_SECRET=your_super_secure_jwt_secret_key_change_this_in_production
        echo.
        echo # =============================================================================
        echo # APPLICATION SETTINGS
        echo # =============================================================================
        echo.
        echo # Application environment ^(development, staging, production^)
        echo APP_ENV=development
        echo.
        echo # Logging configuration
        echo LOG_LEVEL=INFO
        echo LOG_FORMAT=json
        echo.
        echo # API version
        echo API_VERSION=1.1.0
        echo.
        echo # =============================================================================
        echo # DATABASE & CACHING
        echo # =============================================================================
        echo.
        echo # Redis URL for caching and session storage
        echo REDIS_URL=redis://redis:6379/0
        echo.
        echo # =============================================================================
        echo # FILE PROCESSING SETTINGS
        echo # =============================================================================
        echo.
        echo # Temporary storage path for uploaded files
        echo TEMP_STORAGE_PATH=temp_uploads
        echo.
        echo # Maximum file size in MB
        echo MAX_FILE_SIZE_MB=50
        echo MAX_FILE_SIZE=50
        echo.
        echo # Maximum image dimensions
        echo MAX_IMAGE_DIMENSION=2000
        echo.
        echo # =============================================================================
        echo # RETENTION & CLEANUP SETTINGS
        echo # =============================================================================
        echo.
        echo # Cleanup interval in hours
        echo CLEANUP_INTERVAL_HOURS=1
        echo.
        echo # Cache retention in hours
        echo CACHE_RETENTION_HOURS=24
        echo.
        echo # Maximum concurrent analyses
        echo MAX_CONCURRENT_ANALYSES=5
        echo.
        echo # =============================================================================
        echo # SECURITY SETTINGS
        echo # =============================================================================
        echo.
        echo # CORS settings
        echo ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080
        echo ALLOW_CREDENTIALS=false
        echo.
        echo # =============================================================================
        echo # EXPORT SETTINGS
        echo # =============================================================================
        echo.
        echo # Export URL token time-to-live in seconds ^(5 minutes^)
        echo EXPORT_URL_TTL=300
        echo.
        echo # =============================================================================
        echo # RATE LIMITING
        echo # =============================================================================
        echo.
        echo # Rate limiting settings ^(requests per minute^)
        echo RATE_LIMIT_REQUESTS_PER_MINUTE=10
        echo.
        echo # =============================================================================
        echo # DEVELOPMENT SETTINGS
        echo # =============================================================================
        echo.
        echo # Enable debug mode ^(only for development^)
        echo DEBUG=false
        echo.
        echo # Enable hot reload ^(only for development^)
        echo RELOAD=false
        echo.
        echo # =============================================================================
        echo # PRODUCTION SETTINGS
        echo # =============================================================================
        echo.
        echo # Server host ^(0.0.0.0 for Docker, 127.0.0.1 for local^)
        echo HOST=0.0.0.0
        echo.
        echo # Server port
        echo PORT=8000
        echo.
        echo # Number of worker processes ^(for production^)
        echo WORKERS=4
        echo.
        echo # =============================================================================
        echo # OPTIONAL SETTINGS
        echo # =============================================================================
        echo.
        echo # Custom AI model ^(default: openai/gpt-4o-mini^)
        echo AI_MODEL=openai/gpt-4o-mini
        echo.
        echo # Retry delay for AI requests in seconds
        echo RETRY_DELAY=2
        echo.
        echo # Enable AI provider interface
        echo ENABLE_AI_PROVIDER_INTERFACE=true
    ) > backend\.env
    echo [SUCCESS] Created backend/.env
) else (
    echo [WARNING] backend/.env already exists, skipping...
)

REM Create frontend .env file
if not exist "frontend\.env" (
    echo [INFO] Creating frontend/.env...
    (
        echo # Legal Document Analyzer - Frontend Environment Configuration
        echo.
        echo # =============================================================================
        echo # REQUIRED SETTINGS
        echo # =============================================================================
        echo.
        echo # Backend API URL
        echo VITE_API_URL=http://localhost:8000
        echo.
        echo # =============================================================================
        echo # APPLICATION SETTINGS
        echo # =============================================================================
        echo.
        echo # Application environment
        echo NODE_ENV=development
        echo.
        echo # Application title
        echo VITE_APP_TITLE=Legal Document Analyzer
        echo.
        echo # Application description
        echo VITE_APP_DESCRIPTION=AI-powered legal document analysis platform
        echo.
        echo # =============================================================================
        echo # FEATURE FLAGS
        echo # =============================================================================
        echo.
        echo # Enable debug mode
        echo VITE_DEBUG=false
        echo.
        echo # Enable development tools
        echo VITE_DEV_TOOLS=false
        echo.
        echo # =============================================================================
        echo # INTERNATIONALIZATION
        echo # =============================================================================
        echo.
        echo # Default language
        echo VITE_DEFAULT_LANGUAGE=en
        echo.
        echo # Supported languages
        echo VITE_SUPPORTED_LANGUAGES=en,es,fr,de
        echo.
        echo # =============================================================================
        echo # UI SETTINGS
        echo # =============================================================================
        echo.
        echo # Default theme
        echo VITE_DEFAULT_THEME=dark
        echo.
        echo # Enable animations
        echo VITE_ENABLE_ANIMATIONS=true
        echo.
        echo # =============================================================================
        echo # ANALYTICS ^(Optional^)
        echo # =============================================================================
        echo.
        echo # Google Analytics ID ^(optional^)
        echo # VITE_GA_ID=your_google_analytics_id
        echo.
        echo # =============================================================================
        echo # PRODUCTION SETTINGS
        echo # =============================================================================
        echo.
        echo # Build optimization
        echo VITE_BUILD_OPTIMIZE=true
        echo.
        echo # Source map generation ^(disable in production^)
        echo VITE_GENERATE_SOURCEMAP=false
    ) > frontend\.env
    echo [SUCCESS] Created frontend/.env
) else (
    echo [WARNING] frontend/.env already exists, skipping...
)

echo.
echo [SUCCESS] Setup completed successfully!
echo.
echo 📝 Next steps:
echo 1. Get your OpenRouter API key from: https://openrouter.ai/
echo 2. Update backend/.env with your API key
echo 3. Start the application:
echo    - Development: docker-compose -f docker-compose.dev.yml up --build
echo    - Production:  docker-compose up --build
echo.
echo 🌐 Access URLs:
echo    - Frontend: http://localhost:5173 ^(dev^) or http://localhost:3000 ^(prod^)
echo    - Backend:  http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo 📚 For more information, see SETUP.md
echo.
pause
