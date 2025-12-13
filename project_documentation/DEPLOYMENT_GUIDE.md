# Deployment Guide for RAG Educational Content Generator

## Understanding GitHub Pages vs. This Project

### What is GitHub Pages?
GitHub Pages is a **static website hosting service** provided by GitHub. It:
- Hosts static files (HTML, CSS, JavaScript)
- Serves pre-built websites
- Does NOT support server-side code (Python, Node.js, etc.)
- Does NOT support backend APIs or databases
- Is free for public repositories

### Why GitHub Pages Won't Work for This Project

This project has:
1. **FastAPI Backend** - A Python web server that needs to run continuously
2. **Streamlit Frontend** - A Python application server
3. **Pinecone Integration** - Requires backend API calls
4. **OpenAI API** - Server-side API calls (cannot expose keys in frontend)
5. **Vector Database** - Requires backend processing

**GitHub Pages cannot run Python servers or handle backend logic.**

---

## Deployment Options for This Project

### Option 1: Cloud Platforms (Recommended)

#### A. **Render.com** (Easiest - Free Tier Available)
- **Backend (FastAPI):**
  - Deploy as a Web Service
  - Auto-deploys from GitHub
  - Free tier: 750 hours/month
  - Environment variables support

- **Frontend (Streamlit):**
  - Deploy as a Web Service
  - Streamlit is supported
  - Free tier available

**Steps:**
1. Push code to GitHub
2. Connect GitHub repo to Render
3. Create two services:
   - Backend: Point to `backend/` directory
   - Frontend: Point to `frontend/` directory
4. Add environment variables in Render dashboard
5. Deploy!

#### B. **Railway.app** (Simple - Free Trial)
- Supports both FastAPI and Streamlit
- Auto-deploys from GitHub
- Free $5 credit monthly
- Easy environment variable management

#### C. **Heroku** (Popular - Paid)
- Well-established platform
- Supports Python applications
- Free tier discontinued, but paid plans available
- Good documentation

#### D. **Fly.io** (Modern - Free Tier)
- Supports Docker deployments
- Free tier: 3 shared VMs
- Good for both backend and frontend

### Option 2: Traditional VPS/Cloud Servers

#### A. **AWS EC2 / Google Cloud / Azure**
- Full control over the server
- Can run both backend and frontend
- More setup required
- Pay-as-you-go pricing

**Steps:**
1. Create a virtual machine (VM)
2. Install Python, dependencies
3. Set up reverse proxy (Nginx)
4. Run backend and frontend as services
5. Configure firewall and domain

#### B. **DigitalOcean Droplet**
- Simple VPS hosting
- $4-6/month for basic droplet
- Full server control
- Good for learning

### Option 3: Container-Based Deployment

#### A. **Docker + Docker Compose**
- Containerize both services
- Deploy to any container platform
- Consistent environment

#### B. **Kubernetes** (Advanced)
- For scaling and production
- More complex setup
- Good for large deployments

---

## Recommended Deployment Strategy

### For This Project: **Render.com** (Easiest)

**Why Render:**
- ✅ Free tier available
- ✅ Easy GitHub integration
- ✅ Supports both FastAPI and Streamlit
- ✅ Automatic SSL certificates
- ✅ Environment variable management
- ✅ Simple deployment process

### Step-by-Step Deployment to Render

#### 1. Prepare Your Repository

```bash
# Ensure your code is pushed to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Create `render.yaml` (Optional - for easy setup)

Create `render.yaml` in project root:

```yaml
services:
  # Backend Service
  - type: web
    name: rag-edu-backend
    env: python
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && python -m uvicorn src.rag_edu_generator.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: PINECONE_API_KEY
        sync: false
      - key: PINECONE_ENVIRONMENT
        sync: false
      - key: PINECONE_INDEX_NAME
        sync: false
      - key: BACKEND_HOST
        value: 0.0.0.0
      - key: BACKEND_PORT
        fromService:
          type: web
          name: rag-edu-backend
          property: port
      - key: LOG_LEVEL
        value: INFO
      - key: EMBEDDING_MODEL
        value: text-embedding-3-small
      - key: LLM_MODEL
        value: gpt-4-turbo-preview
      - key: LLM_TEMPERATURE
        value: 0.7
      - key: CORS_ORIGINS
        value: https://rag-edu-frontend.onrender.com

  # Frontend Service
  - type: web
    name: rag-edu-frontend
    env: python
    buildCommand: cd frontend && pip install -r requirements.txt
    startCommand: cd frontend && streamlit run src/streamlit_app/main.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: BACKEND_API_URL
        fromService:
          type: web
          name: rag-edu-backend
          property: host
```

#### 3. Deploy on Render

**Backend Deployment:**
1. Go to [render.com](https://render.com)
2. Sign up/login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** `rag-edu-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m uvicorn src.rag_edu_generator.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (from your `.env` file)
7. Click "Create Web Service"

**Frontend Deployment:**
1. Click "New +" → "Web Service"
2. Connect same GitHub repository
3. Configure:
   - **Name:** `rag-edu-frontend`
   - **Root Directory:** `frontend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run src/streamlit_app/main.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
4. Add environment variable:
   - `BACKEND_API_URL`: Your backend URL (e.g., `https://rag-edu-backend.onrender.com`)
5. Click "Create Web Service"

#### 4. Update CORS Settings

In backend environment variables, set:
```
CORS_ORIGINS=https://rag-edu-frontend.onrender.com
```

---

## Alternative: Docker Deployment

### Create Dockerfiles

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "src.rag_edu_generator.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "src/streamlit_app/main.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_ENVIRONMENT=${PINECONE_ENVIRONMENT}
      - PINECONE_INDEX_NAME=${PINECONE_INDEX_NAME}
    env_file:
      - backend/.env

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_API_URL=http://backend:8000
    depends_on:
      - backend
```

---

## Important Considerations

### 1. Environment Variables
- **Never commit** `.env` files to GitHub
- Use platform's environment variable management
- Keep API keys secure

### 2. Database/Pinecone
- Pinecone is cloud-based, so it works from anywhere
- No additional database setup needed

### 3. File Uploads
- Current implementation stores in memory
- For production, consider:
  - Temporary file storage
  - Cloud storage (S3, etc.)
  - File size limits

### 4. Scaling
- Current setup is for single-user/small groups
- For production scaling:
  - Add Redis for session management
  - Use proper database for document metadata
  - Implement user authentication
  - Add rate limiting

### 5. Cost Optimization
- Monitor API usage (OpenAI, Pinecone)
- Implement caching where possible
- Use free tiers when available
- Set usage limits

---

## Quick Start: Render Deployment

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Create Backend Service on Render:**
   - Connect GitHub repo
   - Set root directory: `backend`
   - Add environment variables
   - Deploy

3. **Create Frontend Service on Render:**
   - Connect same GitHub repo
   - Set root directory: `frontend`
   - Set `BACKEND_API_URL` to backend URL
   - Deploy

4. **Update Backend CORS:**
   - Add frontend URL to `CORS_ORIGINS`

5. **Test:**
   - Visit frontend URL
   - Upload a PDF
   - Test functionality

---

## Summary

**GitHub Pages:** ❌ Not suitable (static only)  
**Render.com:** ✅ Recommended (easiest, free tier)  
**Railway.app:** ✅ Good alternative  
**Docker + VPS:** ✅ Full control  
**AWS/GCP/Azure:** ✅ Enterprise scale

For this project, **Render.com** is the best starting point due to simplicity and free tier availability.

