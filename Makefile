# Legal Document Analyzer - Development Makefile

.PHONY: help install dev test lint format build clean docker-build docker-run docker-stop deploy

# Default target
help: ## Show this help message
	@echo "Legal Document Analyzer - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Setup
install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd backend && python -m pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

install-dev: ## Install development dependencies
	@echo "Installing backend dev dependencies..."
	cd backend && pip install pytest pytest-cov black isort flake8 mypy
	@echo "Installing frontend dev dependencies..."
	cd frontend && npm install

# Development
dev: ## Start development servers
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up --build

dev-backend: ## Start only backend development server
	cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start only frontend development server
	cd frontend && npm run dev

# Testing
test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && pytest -v --cov=. --cov-report=html --cov-report=term
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-backend: ## Run backend tests only
	cd backend && pytest -v --cov=. --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests only
	cd frontend && npm test -- --coverage --watchAll=false

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	# Add integration test commands here

# Code Quality
lint: ## Run linting on all code
	@echo "Linting backend..."
	cd backend && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	cd backend && flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "Linting frontend..."
	cd frontend && npm run lint

format: ## Format all code
	@echo "Formatting backend..."
	cd backend && black . && isort .
	@echo "Formatting frontend..."
	cd frontend && npm run format

type-check: ## Run type checking
	@echo "Type checking backend..."
	cd backend && mypy . --ignore-missing-imports
	@echo "Type checking frontend..."
	cd frontend && npx tsc --noEmit

# Building
build: ## Build all applications
	@echo "Building backend..."
	cd backend && python -c "import main; print('Backend build successful')"
	@echo "Building frontend..."
	cd frontend && npm run build

build-backend: ## Build backend only
	cd backend && python -c "import main; print('Backend build successful')"

build-frontend: ## Build frontend only
	cd frontend && npm run build

# Docker Operations
docker-build: ## Build Docker images
	docker-compose build

docker-build-prod: ## Build production Docker images
	docker-compose build

docker-run: ## Run application with Docker
	docker-compose up -d

docker-run-prod: ## Run production application with Docker
	docker-compose --profile production up -d

docker-stop: ## Stop Docker containers
	docker-compose down

docker-clean: ## Clean Docker containers and images
	docker-compose down -v --rmi all

docker-logs: ## Show Docker logs
	docker-compose logs -f

# Database Operations
db-migrate: ## Run database migrations
	@echo "No migrations configured yet"

db-seed: ## Seed database with test data
	@echo "No seed data configured yet"

# Security
security-check: ## Run security checks
	@echo "Running backend security checks..."
	cd backend && safety check
	cd backend && bandit -r .
	@echo "Running frontend security checks..."
	cd frontend && npm audit

# Deployment
deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging..."
	# Add staging deployment commands here

deploy-production: ## Deploy to production environment
	@echo "Deploying to production..."
	# Add production deployment commands here

# Utilities
clean: ## Clean build artifacts and cache
	@echo "Cleaning backend..."
	cd backend && find . -type d -name "__pycache__" -delete
	cd backend && find . -type f -name "*.pyc" -delete
	cd backend && rm -rf .pytest_cache .coverage htmlcov/
	@echo "Cleaning frontend..."
	cd frontend && rm -rf node_modules/.cache dist/ coverage/

logs: ## Show application logs
	@echo "Backend logs:"
	@tail -f backend/logs/backend.log 2>/dev/null || echo "No backend logs found"
	@echo "Frontend logs:"
	@docker-compose logs frontend 2>/dev/null || echo "No frontend logs found"

status: ## Show application status
	@echo "Checking application status..."
	@curl -s http://localhost:8000/health && echo "Backend: ✅ Running" || echo "Backend: ❌ Not running"
	@curl -s http://localhost:3000/health && echo "Frontend: ✅ Running" || echo "Frontend: ❌ Not running"

# CI/CD Helpers
ci-test: ## Run tests for CI/CD pipeline
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	$(MAKE) security-check

ci-build: ## Build for CI/CD pipeline
	$(MAKE) build
	$(MAKE) docker-build

# Environment Setup
env-setup: ## Set up environment variables
	@echo "Creating .env files..."
	@cp backend/.env.example backend/.env || echo "Backend .env already exists"
	@cp frontend/.env.example frontend/.env || echo "Frontend .env already exists"
	@echo "Please update the .env files with your configuration"

# Documentation
docs: ## Generate documentation
	@echo "Generating API documentation..."
	cd backend && python -c "import main; print('API docs available at http://localhost:8000/docs')"

# Monitoring
monitor: ## Start monitoring tools
	@echo "Starting monitoring..."
	# Add monitoring commands here

# Backup
backup: ## Backup application data
	@echo "Creating backup..."
	docker-compose exec backend python -c "import shutil; shutil.make_archive('backup-$(shell date +%Y%m%d-%H%M%S)', 'zip', 'exports', 'logs')"
