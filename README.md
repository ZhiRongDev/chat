# RAG Chat Application

A full-stack **Retrieval-Augmented Generation (RAG)** chat application that combines LLM capabilities with document-based knowledge retrieval. Upload documents, build a knowledge base, and chat with AI using context-aware responses.

## Features

- **RAG-Enhanced Chat**: Chat with AI using standard LLM responses or RAG-enhanced responses with document context
- **Document Management**: Upload and manage PDF, TXT, and Markdown documents
- **Multi-Provider LLM Support**: Gemini, OpenAI, and Anthropic
- **Gemini File Search**: Automatic document indexing, embedding, and semantic retrieval
- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Real-time Updates**: Hot reload for development
- **Dockerized**: Easy deployment with Docker Compose

## Tech Stack

### Required
* FastAPI
* Typescript
* PostgresSQL
* JWT
* Nginx
* Langchain, Langgraph
* Docker
* Deploy on AWS
* Redis
* SocketIO for processing progress.
* Database migration.

---

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.13+** and **Node.js 20.19+/22.12+** for local development
- At least one LLM API key (Gemini, OpenAI, or Anthropic)

### Option 1: Docker (Recommended)

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd chat
```

#### 2. Set Up Environment Variables
```bash
# Copy the environment template
cp backend/.env.template .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required configuration in `.env`:**
```bash
# Database (use these values for Docker)
DB_HOST=db
REDIS_HOST=redis

# API Keys (add at least one)
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here  # Optional
ANTHROPIC_API_KEY=your-anthropic-api-key-here  # Optional

# Other settings can use defaults from template
```

#### 3. Start the Application

**For Development (with hot reload):**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

**For Production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

#### 4. Access the Application
- **Frontend**: http://localhost:5173 (dev) or http://localhost:80 (prod)
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

#### 5. Stop the Application
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v
```

### Option 2: Local Development (Without Docker)

#### 1. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.template .env
nano .env  # Configure for local development
```

**Configure `.env` for local development:**
```bash
DB_HOST=localhost
REDIS_HOST=localhost
# ... add your API keys
```

**Start PostgreSQL and Redis locally:**
```bash
# Using Docker for just the databases
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=chat_dev \
  --name postgres_local \
  postgres:16-alpine

docker run -d -p 6379:6379 \
  --name redis_local \
  redis:7-alpine
```

**Run the backend:**
```bash
# Development mode (with auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Production mode (with Gunicorn)
gunicorn -c gunicorn.conf.py main:app
```

#### 2. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env  # If exists, or create manually
```

**Create `frontend/.env`:**
```bash
VITE_API_BASE_URL=http://localhost:5000
```

**Run the frontend:**
```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build
npm run preview
```

#### 3. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs

---

## Development Environment Setup

### Understanding the Project Structure

```
chat/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── model/       # SQLModel database models
│   │   ├── router/      # API route handlers
│   │   ├── service/     # Business logic
│   │   │   ├── llm/     # LLM service providers
│   │   │   └── gemini_file_search_service.py  # Gemini File Search RAG
│   │   ├── auth.py      # JWT authentication
│   │   └── config.py    # Settings & configuration
│   ├── data/            # Application data
│   ├── main.py          # Application entry point
│   └── requirements.txt
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── api/         # API client
│   │   ├── components/  # Vue components
│   │   ├── router/      # Vue Router
│   │   ├── stores/      # Pinia state management
│   │   └── views/       # Page components
│   └── package.json
├── docker/              # Dockerfiles
│   ├── backend/
│   └── frontend/
├── docker-compose.yml           # Base compose config
├── docker-compose.dev.yml       # Development overrides
├── docker-compose.prod.yml      # Production overrides
└── README.md
```

### Hot Reload Configuration

Hot reload is **automatically enabled** in development mode:

#### Backend Hot Reload
The backend uses Python's `watchfiles` to automatically reload on code changes:
- **What triggers reload**: Any `.py` file changes in `backend/`
- **Volume mount**: `./backend:/app/backend`
- **Startup command**: `python main.py` (configured with `--reload` in `main.py`)

#### Frontend Hot Reload
The frontend uses Vite's built-in HMR (Hot Module Replacement):
- **What triggers reload**: Any file changes in `frontend/src/`
- **Volume mount**: `./frontend:/app/frontend`
- **Startup command**: `npm run dev -- --host 0.0.0.0`

#### Testing Hot Reload

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# In another terminal, make a change to test:
# Backend: Edit backend/app/router/chat_router.py
# Frontend: Edit frontend/src/views/index.vue

# Watch the logs - you should see the service restart automatically
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f frontend
```

### CPU-Only Configuration (No GPU/CUDA)

This project is configured to run **without GPU/CUDA** by default:

#### Environment Variables Set
```bash
CUDA_VISIBLE_DEVICES=     # Empty = no GPU visible
TORCH_DEVICE=cpu          # Force CPU execution
```

#### Where It's Configured
1. **Dockerfile** ([docker/backend/Dockerfile](docker/backend/Dockerfile:10-11)): Set at build time
2. **.env.template** ([backend/.env.template](backend/.env.template:5-7)): For local development
3. **docker-compose.dev.yml** ([docker-compose.dev.yml](docker-compose.dev.yml:35-37)): Runtime override

#### Libraries Using CPU
- **FAISS**: Using `faiss-cpu` package (not `faiss-gpu`)
- **Sentence Transformers**: Will use CPU due to `TORCH_DEVICE=cpu`
- **ChromaDB**: CPU-only by default

### Working with the Database

#### Access PostgreSQL Database
```bash
# Via Docker
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db psql -U postgres -d chat_dev

# Local connection
psql -h localhost -U postgres -d chat_dev
```

#### View Database Tables
```sql
\dt                          -- List all tables
SELECT * FROM users;         -- View users
SELECT * FROM documents;     -- View documents
SELECT * FROM chat_history;  -- View chat history
```

#### Reset Database
```bash
# Stop containers and remove volumes
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v

# Restart (will create fresh database)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Working with Redis

#### Access Redis CLI
```bash
# Via Docker
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec redis redis-cli

# Commands
KEYS *           # List all keys
GET key_name     # Get value
FLUSHALL         # Clear all data (use with caution!)
```

### API Development

#### API Documentation
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

#### Test API Endpoints

**Register a user:**
```bash
curl -X POST http://localhost:5000/api/v1/user/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

**Chat (with token):**
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "Hello, how are you?",
    "use_rag": false
  }'
```

**Upload document:**
```bash
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@path/to/document.pdf"
```

### RAG Configuration

The application uses Google Gemini File Search for RAG functionality. Configuration is automatic:

Edit `.env`:
```bash
# Gemini API Key (required for RAG)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_FILE_SEARCH_MODEL=gemini-2.0-flash-exp  # Model for RAG queries
GEMINI_STORE_SIZE_LIMIT_GB=20                   # Recommended store size
GEMINI_MAX_FILE_SIZE_MB=100                     # Max upload size
```

For detailed RAG usage, see [QUICKSTART_GEMINI_FILE_SEARCH.md](QUICKSTART_GEMINI_FILE_SEARCH.md)

### Testing

#### Backend Tests
```bash
cd backend
pytest                          # Run all tests
pytest tests/test_auth.py       # Run specific test file
pytest -v                       # Verbose output
pytest --cov                    # With coverage
```

#### Frontend Tests
```bash
cd frontend

# Unit tests (Vitest)
npm run test:unit
npm run test:unit -- --coverage

# E2E tests (Playwright)
npx playwright install          # First time only
npm run test:e2e
npm run test:e2e -- --debug     # Debug mode
npm run test:e2e -- --project=chromium  # Specific browser
```

### Debugging

#### View Logs
```bash
# All services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f frontend

# Last 100 lines
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=100 backend
```

#### Check Service Health
```bash
# Check if services are running
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Backend health check
curl http://localhost:5000/api/v1/health

# Check database connection
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python -c "from app.database import engine; print('DB Connected!')"
```

#### Enter Container Shell
```bash
# Backend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec backend bash

# Frontend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec frontend sh

# Database
docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec db bash
```

### Common Issues & Solutions

#### Port Already in Use
```bash
# Find process using port
lsof -i :5000  # or :5173, :5432, :6379

# Kill process
kill -9 <PID>

# Or use different ports in docker-compose.dev.yml
```

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps db

# Check logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs db

# Ensure DB_HOST=db in .env when using Docker
```

#### Module Not Found Errors
```bash
# Rebuild containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Or clear cache
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
docker system prune -a
```

#### Hot Reload Not Working
```bash
# Ensure volumes are mounted correctly in docker-compose.dev.yml
# Check logs for file watcher errors
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend

# On Linux, you may need to increase inotify watchers:
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Production Deployment

### Build for Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### Production Checklist
- [ ] Change `SECRET_KEY` in `.env` to a strong random value
- [ ] Set proper `FRONTEND_HOST` for CORS
- [ ] Configure firewall/security groups
- [ ] Enable HTTPS with reverse proxy (nginx/traefik)
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Set resource limits in docker-compose
- [ ] Enable monitoring (Sentry, etc.)

---

## Additional Resources

- **Gemini File Search Guide**: See [QUICKSTART_GEMINI_FILE_SEARCH.md](QUICKSTART_GEMINI_FILE_SEARCH.md)
- **Docker Deployment**: See [DOCKER_README.md](DOCKER_README.md) and [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **Claude Code Guide**: See [CLAUDE.md](CLAUDE.md)
- **API Documentation**: http://localhost:5000/docs (when running)

## License

MIT
