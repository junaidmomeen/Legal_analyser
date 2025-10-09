# Deployment Guide - Legal Document Analyzer

This guide provides detailed instructions for deploying the Legal Document Analyzer application to various platforms, including free hosting options.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Free Deployment Options](#free-deployment-options)
3. [Docker Deployment](#docker-deployment)
4. [Platform-Specific Deployment](#platform-specific-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Prerequisites

Before deploying, ensure you have:
- OpenRouter API Key (required for AI analysis)
- Git installed
- Docker and Docker Compose (for containerized deployment)
- Domain name (optional, for production deployment)

---

## Free Deployment Options

### Option 1: Railway (Recommended - Free Tier Available)

Railway offers a generous free tier perfect for this application.

**Steps:**

1. **Create Railway Account**
   - Visit [railway.app](https://railway.app) and sign up
   - Connect your GitHub account

2. **Deploy Backend**
   ```bash
   # Fork or clone the repository to your GitHub
   git clone https://github.com/your-username/legal-analyzer.git
   cd legal-analyzer
   ```

3. **Create New Project on Railway**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the backend directory

4. **Configure Environment Variables**
   ```
   OPENROUTER_API_KEY=your_api_key_here
   JWT_SECRET=your_secure_secret_32_chars_minimum
   APP_ENV=production
   LOG_LEVEL=INFO
   ALLOWED_ORIGINS=https://your-frontend-url.railway.app
   ```

5. **Deploy Frontend**
   - Create another service in the same project
   - Select the frontend directory
   - Add environment variable:
     ```
     VITE_API_URL=https://your-backend-url.railway.app
     ```

6. **Access Your Application**
   - Railway provides automatic HTTPS URLs
   - Update CORS settings with your frontend URL

---

### Option 2: Render (Free Tier)

Render offers free hosting for web services and static sites.

**Backend Deployment:**

1. Visit [render.com](https://render.com) and sign up
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Environment:** Python 3
5. Add environment variables (same as Railway)

**Frontend Deployment:**

1. Create a new "Static Site"
2. Configure:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
3. Add environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

**Note:** Free tier spins down after 15 minutes of inactivity (cold starts may be slow).

---

### Option 3: Fly.io (Free Allowance)

Fly.io offers a generous free tier with global deployment.

**Installation:**

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login
```

**Backend Deployment:**

```bash
cd backend
flyctl launch
# Follow the prompts, select region
# Set environment variables
flyctl secrets set OPENROUTER_API_KEY=your_key
flyctl secrets set JWT_SECRET=your_secret
flyctl deploy
```

**Frontend Deployment:**

```bash
cd frontend
# Update VITE_API_URL in .env to your backend URL
flyctl launch
flyctl deploy
```

---

### Option 4: Vercel (Frontend) + Railway/Render (Backend)

**Frontend on Vercel (Free):**

1. Visit [vercel.com](https://vercel.com) and sign up
2. Import your Git repository
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** frontend
   - **Build Command:** npm run build
   - **Output Directory:** dist
4. Add environment variable:
   ```
   VITE_API_URL=https://your-backend-url
   ```
5. Deploy automatically on push

**Backend:** Use Railway or Render as described above.

---

### Option 5: Heroku (Limited Free Tier)

**Note:** Heroku no longer offers a completely free tier, but has affordable options.

**Backend Deployment:**

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
cd backend
heroku create your-app-name-backend

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set OPENROUTER_API_KEY=your_key
heroku config:set JWT_SECRET=your_secret

# Deploy
git push heroku main
```

**Frontend Deployment:**

```bash
cd frontend
heroku create your-app-name-frontend
heroku buildpacks:set heroku/nodejs

# Set environment variables
heroku config:set VITE_API_URL=https://your-backend.herokuapp.com

# Deploy
git push heroku main
```

---

## Docker Deployment

### Local Docker Deployment

**Production Mode:**

```bash
# Clone repository
git clone https://github.com/your-username/legal-analyzer.git
cd legal-analyzer

# Create environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Build and run
docker-compose up --build -d

# Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Development Mode:**

```bash
docker-compose -f docker-compose.dev.yml up --build
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

### Docker Hub Deployment

```bash
# Build and tag images
docker build -t your-username/legal-analyzer-backend:latest ./backend
docker build -t your-username/legal-analyzer-frontend:latest ./frontend

# Push to Docker Hub
docker push your-username/legal-analyzer-backend:latest
docker push your-username/legal-analyzer-frontend:latest

# Pull and run on any server
docker pull your-username/legal-analyzer-backend:latest
docker pull your-username/legal-analyzer-frontend:latest
docker-compose up -d
```

---

## Platform-Specific Deployment

### AWS (Elastic Container Service)

1. **Create ECR Repositories:**
   ```bash
   aws ecr create-repository --repository-name legal-analyzer-backend
   aws ecr create-repository --repository-name legal-analyzer-frontend
   ```

2. **Push Docker Images:**
   ```bash
   # Authenticate
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

   # Tag and push
   docker tag legal-analyzer-backend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/legal-analyzer-backend:latest
   docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/legal-analyzer-backend:latest
   ```

3. **Create ECS Task Definitions and Services** (via AWS Console or CLI)

4. **Configure Load Balancer and Target Groups**

5. **Set Environment Variables in Task Definition**

---

### Google Cloud Platform (Cloud Run)

```bash
# Install gcloud CLI
# Authenticate
gcloud auth login

# Build and deploy backend
cd backend
gcloud builds submit --tag gcr.io/your-project-id/legal-analyzer-backend
gcloud run deploy legal-analyzer-backend \
  --image gcr.io/your-project-id/legal-analyzer-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Set environment variables
gcloud run services update legal-analyzer-backend \
  --set-env-vars OPENROUTER_API_KEY=your_key,JWT_SECRET=your_secret

# Deploy frontend (similar process)
cd frontend
gcloud builds submit --tag gcr.io/your-project-id/legal-analyzer-frontend
gcloud run deploy legal-analyzer-frontend \
  --image gcr.io/your-project-id/legal-analyzer-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

### Azure (Container Instances)

```bash
# Login
az login

# Create resource group
az group create --name legal-analyzer --location eastus

# Create container registry
az acr create --resource-group legal-analyzer --name legalanalyzerregistry --sku Basic

# Build and push images
az acr build --registry legalanalyzerregistry --image legal-analyzer-backend:latest ./backend
az acr build --registry legalanalyzerregistry --image legal-analyzer-frontend:latest ./frontend

# Deploy container instances
az container create \
  --resource-group legal-analyzer \
  --name legal-analyzer-backend \
  --image legalanalyzerregistry.azurecr.io/legal-analyzer-backend:latest \
  --dns-name-label legal-analyzer-backend \
  --ports 8000 \
  --environment-variables OPENROUTER_API_KEY=your_key JWT_SECRET=your_secret
```

---

### DigitalOcean App Platform

1. **Connect GitHub Repository**
2. **Configure Components:**
   - **Backend:**
     - Type: Web Service
     - Dockerfile Path: backend/Dockerfile
     - HTTP Port: 8000
   - **Frontend:**
     - Type: Static Site
     - Build Command: `npm run build`
     - Output Directory: dist

3. **Add Environment Variables** via App Platform console

4. **Deploy** - automatic on git push

---

## Environment Configuration

### Required Environment Variables

**Backend (.env):**

```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here
JWT_SECRET=your_secure_secret_at_least_32_characters_long

# Optional
APP_ENV=production
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
MAX_CONCURRENT_ANALYSES=5
CACHE_RETENTION_HOURS=24
CLEANUP_INTERVAL_HOURS=1
ALLOWED_ORIGINS=https://your-frontend-domain.com
RATE_LIMIT_REQUESTS_PER_MINUTE=100
```

**Frontend (.env):**

```env
VITE_API_URL=https://your-backend-url.com
```

### Security Considerations

1. **JWT Secret:**
   - Generate a secure secret: `openssl rand -hex 32`
   - Never commit to version control

2. **API Keys:**
   - Store in environment variables only
   - Use platform-specific secret management

3. **CORS Configuration:**
   - Set specific origins in production
   - Never use `*` in production

4. **HTTPS:**
   - Always use HTTPS in production
   - Let's Encrypt for free SSL certificates

---

## Post-Deployment Checklist

### Health Checks

- [ ] Backend health endpoint: `https://your-backend/health`
- [ ] Frontend loads correctly
- [ ] File upload works
- [ ] Document analysis completes successfully
- [ ] Export functions work (PDF/JSON)

### Performance Testing

- [ ] Test with various file sizes
- [ ] Verify response times are acceptable
- [ ] Check memory usage
- [ ] Monitor error rates

### Security Audit

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Environment variables secured
- [ ] Rate limiting active
- [ ] Authentication working
- [ ] No sensitive data in logs

### Monitoring Setup

- [ ] Configure logging (Papertrail, Loggly, etc.)
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure error tracking (Sentry)
- [ ] Set up performance monitoring

### Documentation

- [ ] Update README with production URLs
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document rollback procedures

---

## Troubleshooting

### Common Issues

**1. Backend won't start:**
- Check OPENROUTER_API_KEY is set
- Verify JWT_SECRET is at least 32 characters
- Check logs for specific errors

**2. Frontend can't connect to backend:**
- Verify VITE_API_URL is correct
- Check CORS configuration
- Ensure backend is accessible

**3. File upload fails:**
- Check MAX_FILE_SIZE_MB setting
- Verify file type is supported
- Check temporary storage permissions

**4. Analysis timeouts:**
- Increase timeout values
- Check OpenRouter API quota
- Verify network connectivity

**5. High memory usage:**
- Reduce MAX_CONCURRENT_ANALYSES
- Lower CACHE_RETENTION_HOURS
- Enable auto-scaling

---

## Cost Optimization

### Free Tier Limits

- **Railway:** 500 hours/month, $5 credit
- **Render:** 750 hours/month
- **Vercel:** 100 GB bandwidth/month
- **Fly.io:** 3 shared VMs, 160 GB bandwidth
- **Heroku:** $5-7/month for Eco dyno

### Tips for Staying Free

1. Use lightweight deployment (no Redis initially)
2. Implement aggressive caching
3. Set reasonable rate limits
4. Monitor usage regularly
5. Use cold start-tolerant platforms

---

## Support and Resources

- **Documentation:** `/docs` folder in repository
- **API Docs:** `https://your-backend/docs`
- **GitHub Issues:** Report bugs and feature requests
- **Community:** Join discussions on GitHub

---

## Version History

- **v1.0.0** - Initial deployment guide
- Supports Docker, Railway, Render, Vercel, Fly.io, AWS, GCP, Azure, DigitalOcean

---

**Last Updated:** 2025-10-09
