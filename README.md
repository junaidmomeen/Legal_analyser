# Legal Document Analyzer

[![Backend Tests](https://github.com/your-username/legal-analyzer/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/your-username/legal-analyzer/actions/workflows/backend-ci.yml)
[![Frontend Tests](https://github.com/your-username/legal-analyzer/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/your-username/legal-analyzer/actions/workflows/frontend-ci.yml)
[![Full Stack CI](https://github.com/your-username/legal-analyzer/actions/workflows/fullstack-ci.yml/badge.svg)](https://github.com/your-username/legal-analyzer/actions/workflows/fullstack-ci.yml)

A modern, full-stack legal document analysis platform powered by AI. Upload contracts, policies, or legal documents and receive instant AI-powered insights, OCR text extraction, and structured analysis reports.

## ✨ Features

### 🔍 AI-Powered Analysis
- **Document Processing**: Upload PDFs and images with automatic OCR
- **AI Analysis**: GPT-4 powered legal document insights
- **Key Clause Detection**: Automatically identify and categorize important clauses
- **Risk Assessment**: Get risk scores and importance ratings for each clause
- **Multi-language Support**: English, Spanish, French, and German

### 🔒 Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Built-in protection against abuse
- **Input Validation**: Comprehensive file type and size validation
- **CORS Configuration**: Environment-specific security settings

### 🎨 Modern User Interface
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark Theme**: Modern, professional appearance
- **Accessibility**: WCAG 2.1 AA compliant with keyboard navigation
- **Internationalization**: Multi-language support with dynamic switching
- **Interactive Dashboard**: Real-time analysis results with filtering and search

### 🚀 Production Ready
- **Automated Cleanup**: Retention jobs for efficient resource management
- **Health Monitoring**: Built-in health checks and monitoring
- **Structured Logging**: JSON logging with request tracking
- **Export Options**: Download reports in PDF and JSON formats
- **Error Handling**: Comprehensive error management and user feedback

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Python 3.11+**: Modern Python with async support
- **OpenRouter**: AI analysis with GPT-4
- **PyMuPDF**: PDF processing and text extraction
- **Tesseract OCR**: Image text recognition
- **Redis**: Caching and session storage
- **JWT**: Secure authentication

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations
- **React i18next**: Internationalization
- **Axios**: HTTP client

### DevOps
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipelines
- **Pytest**: Backend testing
- **Jest**: Frontend testing
- **ESLint**: Code linting
- **Black/Prettier**: Code formatting

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- OpenRouter API Key

### Option 1: Docker (Recommended)

1. **Clone and setup**
   ```bash
   git clone https://github.com/your-username/legal-analyzer.git
   cd legal-analyzer
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. **Configure environment**
   Edit `backend/.env` and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_api_key_here
   JWT_SECRET=your_secure_secret_here
   ```

3. **Start the application**
   ```bash
   # Development mode
   docker-compose -f docker-compose.dev.yml up --build
   
   # Production mode
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:5173 (dev) or http://localhost:3000 (prod)
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

1. **Backend setup**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install requirements (pip issue fixed)
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    # Start the backend
    python -m uvicorn main:app --reload
    ```
    
    **Note**: If you encounter pip installation issues, use the setup script:
    - Windows: `setup-requirements.bat`
    - Linux/Mac: `./setup-requirements.sh`

2. **Frontend setup** (new terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🧪 Testing

    ```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend

# Security checks
make security-check
```

## 📁 Project Structure

```
legal_analyzer/
├── backend/                    # FastAPI backend
│   ├── services/              # Business logic
│   │   ├── ai_analyzer.py     # AI analysis service
│   │   ├── document_processor.py # Document processing
│   │   ├── retention_jobs.py  # Automated cleanup
│   │   └── report_generator.py # Report generation
│   ├── models/                # Pydantic models
│   ├── routers/               # API routes
│   ├── tests/                 # Backend tests
│   │   ├── test_auth_integration.py # Auth tests
│   │   └── test_retention_jobs.py   # Retention tests
│   ├── middleware/            # Custom middleware
│   ├── utils/                 # Utility functions
│   └── Dockerfile             # Backend container
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── LanguageSelector.tsx
│   │   │   ├── HelpDialog.tsx
│   │   │   └── ...
│   │   ├── hooks/             # Custom hooks
│   │   │   └── useAccessibility.ts
│   │   ├── i18n/              # Internationalization
│   │   │   ├── index.ts
│   │   │   └── locales/
│   │   └── api/               # API client
│   ├── Dockerfile             # Frontend container
│   └── nginx.conf             # Nginx configuration
├── .github/workflows/         # CI/CD pipelines
│   ├── backend-ci.yml         # Backend CI/CD
│   ├── frontend-ci.yml        # Frontend CI/CD
│   └── fullstack-ci.yml       # Full stack CI/CD
├── docker-compose.yml         # Production setup
├── docker-compose.dev.yml     # Development setup
└── Makefile                   # Development commands
```

## 🔧 API Endpoints

### Core Endpoints
- `POST /analyze` - Analyze a document (requires authentication)
- `GET /analysis/{file_id}` - Get analysis results
- `POST /export/{file_id}/{format}` - Export analysis (PDF/JSON)
- `GET /documents/{file_id}` - Download original document

### System Endpoints
- `GET /health` - Health check
- `GET /stats` - System statistics
- `GET /retention/status` - Retention jobs status
- `POST /retention/cleanup` - Manual cleanup trigger

### Public Endpoints
- `GET /` - API information
- `GET /supported-formats` - Supported file formats

## 🌐 Internationalization

The application supports multiple languages:
- 🇺🇸 English
- 🇪🇸 Spanish (Español)
- 🇫🇷 French (Français)
- 🇩🇪 German (Deutsch)

Language switching is available via the UI or browser preferences.

## ♿ Accessibility Features

- **Keyboard Navigation**: Full keyboard support with shortcuts
- **Screen Reader**: Compatible with screen readers
- **High Contrast**: Support for high contrast mode
- **Reduced Motion**: Respects user motion preferences
- **Focus Management**: Proper focus handling and visual indicators
- **ARIA Labels**: Comprehensive accessibility labels

### Keyboard Shortcuts
- `Ctrl+U` - Upload new file
- `Ctrl+N` - Start new analysis
- `Ctrl+F` - Focus search
- `F1` - Show help
- `Escape` - Close dialogs

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: 10 requests per minute per user
- **Input Validation**: File type, size, and content validation
- **CORS Protection**: Environment-specific CORS configuration
- **Request ID Tracking**: Unique request IDs for debugging
- **Security Headers**: Comprehensive security headers

## 📊 Monitoring & Observability

- **Health Checks**: Built-in health monitoring
- **Structured Logging**: JSON logging with request tracking
- **Metrics**: Prometheus-compatible metrics
- **Error Tracking**: Comprehensive error handling and reporting
- **Performance Monitoring**: Request timing and resource usage

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export OPENROUTER_API_KEY="your_api_key"
   export JWT_SECRET="your_secure_secret"
   export APP_ENV="production"
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose up -d
   ```

3. **Verify Deployment**
    ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000/health
   ```

### Cloud Deployment

The application is ready for deployment on:
- **AWS**: ECS, EKS, or EC2
- **Google Cloud**: Cloud Run, GKE, or Compute Engine
- **Azure**: Container Instances, AKS, or App Service
- **Kubernetes**: With provided manifests

## 🧪 Development Commands

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

## 📈 Performance

- **Backend**: FastAPI with async support for high concurrency
- **Frontend**: React 18 with optimized rendering
- **Caching**: Redis-based caching for improved performance
- **File Processing**: Streaming file uploads and processing
- **Database**: In-memory storage with configurable retention

## 🔄 Automated Features

### Retention Jobs
- **Analysis Cleanup**: Automatic removal of old analyses
- **File Cleanup**: Temporary file management
- **Export Cleanup**: Automatic export file cleanup
- **Log Rotation**: Log file management
- **Configurable Policies**: Customizable retention periods

### CI/CD Pipeline
- **Automated Testing**: Backend and frontend test automation
- **Code Quality**: Linting, formatting, and type checking
- **Security Scanning**: Vulnerability and dependency scanning
- **Container Building**: Automated Docker image building
- **Deployment**: Automated deployment to staging and production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/TypeScript
- Write tests for new features
- Update documentation as needed
- Ensure accessibility compliance

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/your-username/legal-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/legal-analyzer/discussions)

## 🗺️ Roadmap

- [ ] GraphQL API support
- [ ] Advanced document comparison features
- [ ] Batch processing capabilities
- [ ] Webhook integrations
- [ ] Plugin architecture
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support

## 🙏 Acknowledgments

- **OpenRouter** for AI capabilities
- **FastAPI** for the backend framework
- **React** for the frontend framework
- **Tailwind CSS** for styling
- **All contributors** and users

---

**Legal Document Analyzer** - Making legal document analysis accessible, fast, and intelligent. 🚀
