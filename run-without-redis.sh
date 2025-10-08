#!/bin/bash

# Legal Document Analyzer - Run without Redis
# This script runs the project without Redis dependency

set -e  # Exit on any error

echo "🚀 Legal Document Analyzer - Running without Redis"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backend .env file without Redis
create_backend_env() {
    print_status "Creating backend/.env without Redis..."
    
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << 'EOF'
# Legal Document Analyzer - Backend Environment Configuration
# Running WITHOUT Redis

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
# DATABASE & CACHING - DISABLED
# =============================================================================

# Redis is disabled - using in-memory storage
# REDIS_URL=redis://redis:6379/0

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
# RATE LIMITING - IN-MEMORY
# =============================================================================

# Rate limiting settings (requests per minute) - using in-memory storage
RATE_LIMIT_REQUESTS_PER_MINUTE=100
# RATE_LIMIT_STORAGE_URI=redis://redis:6379

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

# =============================================================================
# CELERY SETTINGS - DISABLED
# =============================================================================

# Celery is disabled - tasks run synchronously
# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/1
EOF
        print_success "Created backend/.env without Redis"
    else
        print_warning "backend/.env already exists, skipping..."
    fi
}

# Create frontend .env file
create_frontend_env() {
    print_status "Creating frontend/.env..."
    
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << 'EOF'
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
# PRODUCTION SETTINGS
# =============================================================================

# Build optimization
VITE_BUILD_OPTIMIZE=true

# Source map generation (disable in production)
VITE_GENERATE_SOURCEMAP=false
EOF
        print_success "Created frontend/.env"
    else
        print_warning "frontend/.env already exists, skipping..."
    fi
}

# Check Python installation
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "backend/requirements.txt" ]; then
        $PYTHON_CMD -m pip install --upgrade pip
        $PYTHON_CMD -m pip install -r backend/requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "backend/requirements.txt not found"
        exit 1
    fi
}

# Main function
main() {
    print_status "Starting setup process..."
    
    # Check Python
    check_python
    
    # Create environment files
    create_backend_env
    create_frontend_env
    
    # Install dependencies
    install_dependencies
    
    print_success "Setup completed successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Get your OpenRouter API key from: https://openrouter.ai/"
    echo "2. Update backend/.env with your API key"
    echo "3. The application will run with in-memory storage (no Redis needed)"
    echo ""
    echo "🌐 Access URLs:"
    echo "   - Backend:  http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "🚀 Starting backend server..."
    echo ""
    
    # Start the backend server
    cd backend
    $PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# Run main function
main "$@"
