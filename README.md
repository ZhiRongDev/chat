# RAG Chat Application

A full-stack **Retrieval-Augmented Generation (RAG)** chat application that combines LLM capabilities with document-based knowledge retrieval. Upload documents, build a knowledge base, and chat with AI using context-aware responses.

## Features

### Core Features

- **RAG-Enhanced Chat**: Chat with AI using standard LLM responses or RAG-enhanced responses with document context
- **LangGraph Agent System**: Multi-step reasoning with integrated search capabilities (Google via Serper, Tavily Search)
- **Document Management**: Upload and manage PDF, TXT, Markdown, DOCX, JSON, CSV, and more
- **Multi-Provider LLM Support**: Gemini, OpenAI, and Anthropic with user-provided API key option
- **Gemini File Search**: Automatic document indexing, embedding, and semantic retrieval with per-user stores

### Authentication & Security

- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Email Verification**: Required email verification for new user accounts via Gmail API
- **Password Reset**: Secure password reset flow with email-based JWT tokens
- **Optional Authentication**: Chat endpoint works with or without authentication

### Development & Deployment

- **Real-time Updates**: Hot reload for development (frontend and backend)
- **Database Migrations**: Alembic-based migration system for schema changes
- **Form Validation**: VeeValidate with Yup schemas for robust input validation
- **Internationalization**: Multi-language support (English, Traditional Chinese) via vue-i18n
- **Comprehensive Testing**: pytest (backend), Vitest (frontend unit), Playwright (E2E)
- **CI/CD Pipeline**: Automated testing, linting, security scanning, and build checks
- **Dockerized**: Easy deployment with Docker Compose (dev and production modes)
- **Utility Scripts**: Makefile and shell scripts for common operations

## Tech Stack

### Backend

- **Framework**: FastAPI with Uvicorn/Gunicorn
- **Database**: PostgreSQL 16 with SQLModel ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI/ML**:
  - LLM Providers: Gemini, OpenAI, Anthropic (via Langchain)
  - Agent Framework: LangGraph for multi-step reasoning
  - RAG: Gemini File Search API
  - Search Tools: Serper (Google Search), Tavily Search
- **Email**: Gmail API for verification and password reset
- **Migrations**: Alembic for database schema management
- **Testing**: pytest with coverage

### Frontend

- **Framework**: Vue 3.5 with TypeScript 5.9
- **Build Tool**: Vite 7.1
- **State Management**: Pinia 3.0
- **Routing**: Vue Router 4.5
- **UI Framework**: Bootstrap 5.3 with Bootstrap Icons
- **Form Validation**: VeeValidate 4.15 with Yup
- **Markdown**: Marked 17.0 with Highlight.js 11.11 for code highlighting
- **Internationalization**: vue-i18n with English and Traditional Chinese
- **Testing**: Vitest (unit), Playwright (E2E)

### Infrastructure

- **Containerization**: Docker with Docker Compose
- **Web Server**: Nginx (production)
- **CI/CD**: GitHub Actions with automated testing, linting, security scanning
- **Deployment**: AWS-ready with health checks and monitoring

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
# Database (use your external database credentials)
POSTGRES_HOST=your-database-host.example.com
POSTGRES_USER=postgres
POSTGRES_DB=chat_dev
POSTGRES_PASSWORD=your-secure-password
POSTGRES_PORT=22463

# API Keys (add at least one)
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here  # Optional
ANTHROPIC_API_KEY=your-anthropic-api-key-here  # Optional

# Search API Keys (for LangGraph agent)
SERPER_API_KEY=your-serper-api-key-here  # Optional: Google Search via Serper
TAVILY_API_KEY=your-tavily-api-key-here  # Optional: Tavily Search

# Gmail API (for email verification and password reset)
GMAIL_CREDENTIALS_PATH=app/service/gmail/credentials.json
GMAIL_TOKEN_PATH=app/service/gmail/token.json
SENDER_EMAIL=your-email@gmail.com

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

#### 5. Stop the Application

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v
```

#### 6. Using the Makefile (Convenient Alternative)

The project includes a Makefile for easier management:

```bash
# Development
make dev          # Start development environment
make logs         # View logs (all services)
make health       # Check service health

# Testing
make test         # Run all tests (backend + frontend)

# Production
make prod         # Start production environment

# Database
make backup       # Backup PostgreSQL database
make restore      # Restore PostgreSQL database

# Cleanup
make stop         # Stop all services
make clean        # Remove containers and volumes
make rebuild      # Clean rebuild of all services
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
# Use your external database or local PostgreSQL
POSTGRES_HOST=localhost  # or your external database host
POSTGRES_USER=postgres
POSTGRES_DB=chat_dev
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=22463

# ... add your API keys
```

**Note**: This project is designed to use external managed PostgreSQL (Zeabur, AWS RDS, Supabase, etc.). If you need to run PostgreSQL locally for development, you can use Docker:

```bash
docker run -d -p 22463:22463 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=chat_dev \
  --name postgres_local \
  postgres:16-alpine
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
├── backend/                     # FastAPI backend
│   ├── alembic/                 # Database migrations
│   │   └── versions/            # Migration scripts
│   ├── app/
│   │   ├── model/               # SQLModel database models
│   │   │   ├── user_model.py    # User with email verification
│   │   │   ├── chat_model.py    # Chat history and messages
│   │   │   └── document_model.py # Documents and Gemini stores
│   │   ├── router/              # API route handlers
│   │   │   ├── user_router.py   # Auth, verification, password reset
│   │   │   ├── chat_router.py   # Chat with RAG support
│   │   │   └── document_router.py # Document management
│   │   ├── service/             # Business logic
│   │   │   ├── llm/             # LLM services
│   │   │   │   ├── agent_graph.py      # LangGraph agent
│   │   │   │   ├── llm_factory.py      # Multi-provider factory
│   │   │   │   └── search_tools.py     # Serper/Tavily search
│   │   │   ├── gmail/           # Email services
│   │   │   ├── user_service.py  # User CRUD
│   │   │   ├── chat_service.py  # Chat management
│   │   │   └── gemini_file_search_service.py  # RAG service
│   │   ├── auth.py              # JWT authentication
│   │   ├── config.py            # Settings & configuration
│   │   └── utils.py             # Snowflake ID generation
│   ├── tests/                   # pytest test suite
│   ├── data/                    # Application data
│   ├── main.py                  # Application entry point
│   ├── requirements.txt         # Python dependencies
│   └── alembic.ini              # Alembic configuration
├── frontend/                    # Vue 3 frontend
│   ├── src/
│   │   ├── api/                 # API client services
│   │   ├── components/          # Vue components
│   │   │   ├── ChatSettings.vue
│   │   │   ├── DocumentManager.vue
│   │   │   ├── MarkdownRenderer.vue
│   │   │   └── Sidebar.vue
│   │   ├── locale/              # i18n translations (en, zh-TW)
│   │   ├── router/              # Vue Router configuration
│   │   ├── stores/              # Pinia state management
│   │   ├── utils/               # Utilities (i18n, locale)
│   │   ├── views/               # Page components
│   │   │   ├── index.vue        # Main chat interface
│   │   │   ├── VerifyEmail.vue
│   │   │   ├── ResetPassword.vue
│   │   │   └── NotFound.vue
│   │   └── __tests__/           # Vitest unit tests
│   ├── e2e/                     # Playwright E2E tests
│   ├── package.json
│   ├── vite.config.ts
│   └── playwright.config.ts
├── docker/                      # Dockerfiles
│   ├── backend/
│   └── frontend/
├── scripts/                     # Utility scripts
│   ├── dev.sh                   # Start development
│   ├── prod.sh                  # Start production
│   ├── logs.sh                  # View logs
│   ├── health-check.sh          # Health checks
│   ├── db-backup.sh             # Database backup
│   └── db-restore.sh            # Database restore
├── .github/workflows/           # CI/CD pipelines
│   ├── ci.yml                   # Main CI pipeline
│   └── docker-build.yml         # Docker builds
├── docker-compose.yml           # Base compose config
├── docker-compose.dev.yml       # Development overrides
├── docker-compose.prod.yml      # Production overrides
├── Makefile                     # Convenience commands
├── README.md                    # This file
├── CLAUDE.md                    # Claude Code guide
├── TESTING.md                   # Testing documentation
├── DOCKER_SETUP.md              # Docker deployment guide
└── QUICKSTART_GEMINI_FILE_SEARCH.md  # RAG quick start
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

This project uses external managed PostgreSQL databases (Zeabur, AWS RDS, Supabase, etc.).

#### Access PostgreSQL Database

```bash
# Connect to your external database
psql -h your-database-host -U postgres -d chat_dev

# Or use your database provider's web console
```

#### View Database Tables

```sql
\dt                          -- List all tables
SELECT * FROM users;         -- View users
SELECT * FROM documents;     -- View documents
SELECT * FROM chat_history;  -- View chat history
```

#### Run Migrations

```bash
cd backend
alembic upgrade head  # Apply all migrations to your external database
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

**Chat (with authentication):**

```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "Hello, how are you?",
    "use_rag": false,
    "provider": "gemini"
  }'
```

**Chat (without authentication, using user-provided API key):**

```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": false,
    "provider": "gemini",
    "gemini_api_key": "your-gemini-api-key-here"
  }'
```

**Chat with RAG (requires authentication for personal document store):**

```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "What does my document say about X?",
    "use_rag": true,
    "provider": "gemini"
  }'
```

**Upload document:**

```bash
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@path/to/document.pdf"
```

**Email verification:**

```bash
curl -X POST http://localhost:5000/api/v1/user/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "token": "JWT_TOKEN_FROM_EMAIL"
  }'
```

**Password reset request:**

```bash
curl -X POST http://localhost:5000/api/v1/user/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

### RAG Configuration

The application uses Google Gemini File Search for RAG functionality. Configuration is automatic:

Edit `.env`:

```bash
# Gemini API Key (required for RAG)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_FILE_SEARCH_MODEL=gemini-2.5-flash-lite  # Model for RAG queries
GEMINI_STORE_SIZE_LIMIT_GB=20                   # Recommended store size
GEMINI_MAX_FILE_SIZE_MB=100                     # Max upload size
```

For detailed RAG usage, see [QUICKSTART_GEMINI_FILE_SEARCH.md](QUICKSTART_GEMINI_FILE_SEARCH.md)

### Testing

The project has comprehensive testing across multiple levels. For detailed testing documentation, see [TESTING.md](TESTING.md).

#### Backend Tests (pytest)

```bash
cd backend

# Run all tests
pytest

# Run specific test files
pytest tests/test_auth.py
pytest tests/test_user_service.py
pytest tests/test_chat_router.py
pytest tests/test_document_router.py

# Verbose output with coverage
pytest -v --cov=app --cov-report=html
```

#### Frontend Unit Tests (Vitest)

```bash
cd frontend

# Run all unit tests
npm run test:unit

# Run with coverage
npm run test:unit -- --coverage

# Run in watch mode
npm run test:unit -- --watch
```

#### Frontend E2E Tests (Playwright)

```bash
cd frontend

# Install browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run specific test file
npm run test:e2e -- tests/authentication.spec.ts
npm run test:e2e -- tests/chat.spec.ts
npm run test:e2e -- tests/email-verification.spec.ts

# Run in specific browser
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=firefox
npm run test:e2e -- --project=webkit

# Debug mode
npm run test:e2e -- --debug

# UI mode for interactive testing
npm run test:e2e -- --ui
```

#### CI/CD Testing

The project uses GitHub Actions for automated testing:

- **Backend Tests**: Run with PostgreSQL service
- **Frontend Unit Tests**: Vitest with coverage reporting
- **Frontend E2E Tests**: Playwright on multiple browsers
- **Linting & Formatting**: ESLint, Prettier, Black, isort
- **Security Scanning**: Trivy for vulnerability detection
- **Build Checks**: Ensure Docker images build successfully

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
lsof -i :5000  # or :5173, :22463, :6379

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

# Ensure POSTGRES_HOST=db in .env when using Docker
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

## Advanced Features

### Email Verification System

New users must verify their email address before they can access the application.

#### Setup Gmail API

1. **Create Google Cloud Project** and enable Gmail API
2. **Create OAuth 2.0 credentials** (Desktop app type)
3. **Download credentials** and save as `backend/app/service/gmail/credentials.json`
4. **Configure environment**:

```bash
# .env
GMAIL_CREDENTIALS_PATH=app/service/gmail/credentials.json
GMAIL_TOKEN_PATH=app/service/gmail/token.json
SENDER_EMAIL=your-email@gmail.com
```

5. **First-time authorization**: Run the backend, it will open a browser for Gmail authorization
6. **Token saved**: `token.json` will be created and used for subsequent emails

#### Email Verification Flow

1. User registers at `/api/v1/user/` → Account created with `is_verified=false`
2. Verification email sent with JWT token link
3. User clicks link → Redirected to frontend `/verify-email?token=...`
4. Frontend calls `/api/v1/user/verify-email` → Account verified
5. User can now login

### Password Reset Flow

Users can reset their password via email:

1. User requests reset at `/api/v1/user/request-password-reset` with email
2. Email sent with JWT token link (15-minute expiration)
3. User clicks link → Redirected to frontend `/reset-password?token=...`
4. User enters new password → Frontend calls `/api/v1/user/reset-password`
5. Password updated, user can login with new password

### LangGraph Agent System

The application includes a sophisticated multi-step reasoning agent powered by LangGraph.

#### Features

- **Multi-step reasoning**: Iterative problem solving with tool usage
- **Search integration**: Google Search (via Serper) and Tavily Search
- **Decision making**: Agent decides when to search, when to respond
- **State management**: Tracks conversation context and search results

#### Architecture

The agent uses a state graph with multiple nodes:

1. **Reasoner**: Analyzes the query and decides next action
2. **Search Decision**: Determines if search is needed
3. **Search Executor**: Runs search queries if needed
4. **Response Generator**: Synthesizes final answer

#### Configuration

```bash
# .env - Both optional, agent works without search if not provided
SERPER_API_KEY=your-serper-api-key-here      # For Google Search
TAVILY_API_KEY=your-tavily-api-key-here      # For Tavily Search
```

#### Using the Agent

The agent is integrated into the chat endpoint. No special configuration needed - it automatically uses available search tools when beneficial.

For detailed architecture, see [backend/app/service/llm/README.md](backend/app/service/llm/README.md).

### Database Migrations with Alembic

The project uses Alembic for database schema management.

#### Create a New Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description of changes"
```

#### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Downgrade one revision
alembic downgrade -1
```

#### Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

### Internationalization (i18n)

The frontend supports multiple languages using vue-i18n.

#### Supported Languages

- **English** (en)
- **Traditional Chinese** (zh-TW)

#### Adding New Languages

1. Create new locale file in `frontend/src/locale/`
2. Import in `frontend/src/utils/i18n.ts`
3. Add to locale options in `frontend/src/utils/locale.ts`

#### Usage in Components

```vue
<template>
  <div>{{ $t("welcome.message") }}</div>
</template>
```

---

## Production Deployment

### Build for Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### Production Checklist

- [ ] Change `SECRET_KEY` in `.env` to a strong random value (use `openssl rand -hex 32`)
- [ ] Set proper `FRONTEND_HOST` for CORS configuration
- [ ] Configure Gmail API credentials for email verification/password reset
- [ ] Set up firewall rules and security groups
- [ ] Enable HTTPS with reverse proxy (nginx/traefik/Caddy)
- [ ] Configure database backups with `scripts/db-backup.sh`
- [ ] Set up log aggregation (e.g., ELK stack, CloudWatch)
- [ ] Configure resource limits in docker-compose.prod.yml
- [ ] Enable monitoring and alerting (Sentry, Prometheus, etc.)
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Set appropriate token expiration times
- [ ] Review and restrict API rate limits

---

## Additional Resources

### Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive guide for Claude Code with architecture details
- **[TESTING.md](TESTING.md)** - Complete testing documentation (backend, frontend, CI/CD)
- **[QUICKSTART_GEMINI_FILE_SEARCH.md](QUICKSTART_GEMINI_FILE_SEARCH.md)** - Quick start guide for Gemini RAG system
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Detailed Docker deployment guide
- **[DOCKER_README.md](DOCKER_README.md)** - Docker configuration reference
- **[backend/app/service/llm/README.md](backend/app/service/llm/README.md)** - LLM service and agent architecture

### API Documentation

- **Swagger UI**: http://localhost:5000/docs (interactive API documentation)
- **ReDoc**: http://localhost:5000/redoc (alternative API documentation)
- **Health Check**: http://localhost:5000/api/v1/health

### Useful Commands

```bash
# Quick development setup
make dev              # Start development environment
make logs             # View all logs
make test             # Run all tests
make health           # Check service health

# Database management
make backup           # Backup database
make restore          # Restore database
alembic upgrade head  # Apply migrations

# Testing
pytest                # Backend tests
npm run test:unit     # Frontend unit tests
npm run test:e2e      # Frontend E2E tests

# Docker management
make stop             # Stop all services
make clean            # Remove containers and volumes
make rebuild          # Full rebuild
```

### Project Statistics

- **Backend**: FastAPI with 5+ routers, 10+ services, comprehensive test coverage
- **Frontend**: Vue 3 with TypeScript, 4+ views, 4+ components, E2E testing
- **Database**: PostgreSQL with Alembic migrations, Snowflake ID generation
- **Testing**: pytest (backend), Vitest (unit), Playwright (E2E), GitHub Actions CI/CD
- **Documentation**: 7 comprehensive .md files covering all aspects

### Getting Help

- **Issues**: Report bugs or request features on the project repository
- **API Docs**: Check Swagger UI at http://localhost:5000/docs for endpoint details
- **Logs**: Use `make logs` or individual service logs for debugging
- **Health**: Use `make health` to verify all services are running correctly

## License

MIT
