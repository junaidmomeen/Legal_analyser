#!/bin/bash

# Legal Document Analyzer - Quick Setup Script
# This script helps you set up the project quickly

set -e  # Exit on any error

echo "🚀 Legal Document Analyzer - Quick Setup"
echo "========================================"

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

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
        if command -v docker-compose &> /dev/null; then
            print_success "Docker Compose is installed"
        else
            print_warning "Docker Compose not found, trying 'docker compose'"
            if docker compose version &> /dev/null; then
                print_success "Docker Compose (new version) is available"
            else
                print_error "Docker Compose is required"
                exit 1
            fi
        fi
    else
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
}

# Create environment files
create_env_files() {
    print_status "Creating environment files..."
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << 'EOF'
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
EOF
        print_success "Created backend/.env"
    else
        print_warning "backend/.env already exists, skipping..."
    fi

    # Frontend .env
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
EOF
        print_success "Created frontend/.env"
    else
        print_warning "frontend/.env already exists, skipping..."
    fi
}

# Generate secure JWT secret
generate_jwt_secret() {
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -base64 32)
        sed -i.bak "s/your_super_secure_jwt_secret_key_change_this_in_production/$JWT_SECRET/" backend/.env
        rm backend/.env.bak
        print_success "Generated secure JWT secret"
    else
        print_warning "OpenSSL not found, please update JWT_SECRET manually in backend/.env"
    fi
}

# Main setup function
main() {
    print_status "Starting setup process..."
    
    # Check prerequisites
    check_docker
    
    # Create environment files
    create_env_files
    
    # Generate JWT secret
    generate_jwt_secret
    
    print_success "Setup completed successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Get your OpenRouter API key from: https://openrouter.ai/"
    echo "2. Update backend/.env with your API key"
    echo "3. Start the application:"
    echo "   - Development: docker-compose -f docker-compose.dev.yml up --build"
    echo "   - Production:  docker-compose up --build"
    echo ""
    echo "🌐 Access URLs:"
    echo "   - Frontend: http://localhost:5173 (dev) or http://localhost:3000 (prod)"
    echo "   - Backend:  http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "📚 For more information, see SETUP.md"
}

# Run main function
main "$@"
