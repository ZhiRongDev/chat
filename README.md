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
- **Email Verification**: Required email verification for new user accounts via Gmail SMTP
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
- **Caching & Rate Limiting**: Redis 7 with sliding window rate limiter
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI/ML**:
  - LLM Providers: Gemini, OpenAI, Anthropic (via Langchain)
  - Agent Framework: LangGraph for multi-step reasoning
  - RAG: Gemini File Search API
  - Search Tools: Serper (Google Search), Tavily Search
- **Email**: Gmail SMTP for verification and password reset
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
- **Caching**: Redis 7 (Alpine) for rate limiting
- **Web Server**: Nginx (production)
- **CI/CD**: GitHub Actions with automated testing, linting, security scanning
- **Deployment**: AWS-ready with health checks and monitoring

## Utility Scripts

The `scripts/` directory contains helpful tools for development and operations:

### Redis Monitoring

**Quick Monitor (Shell Script)**:
```bash
./scripts/redis-monitor.sh
```

**Python Monitor (Advanced)**:
```bash
# Monitor all keys once
python scripts/monitor_redis.py

# Monitor rate limit keys continuously
python scripts/monitor_redis.py --pattern "rate_limit:*" --watch 5

# Clear all rate limit keys
python scripts/monitor_redis.py --pattern "rate_limit:*" --clear
```

See [scripts/README_REDIS_MONITOR.md](scripts/README_REDIS_MONITOR.md) for detailed documentation.

### Other Scripts

- `scripts/dev.sh` - Start development environment
- `scripts/prod.sh` - Start production environment
- `scripts/logs.sh` - View application logs
- `scripts/health-check.sh` - Check service health
- `scripts/db-backup.sh` / `scripts/db-restore.sh` - Database backup/restore
