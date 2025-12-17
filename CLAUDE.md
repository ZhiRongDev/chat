# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **RAG (Retrieval-Augmented Generation) chat application** that combines LLM capabilities with document-based knowledge retrieval. The system allows users to:

- Upload documents (PDF, TXT, MD) to build a knowledge base
- Chat with AI using standard LLM responses or RAG-enhanced responses
- Retrieve relevant context from documents to answer queries
- Manage document libraries with user authentication

## Architecture

### Monorepo Structure

- **frontend/**: Vue 3 + TypeScript + Vite application
- **backend/**: FastAPI Python application
- **docker/**: Docker configurations for frontend and backend
- **scripts/**: Utility scripts

### Tech Stack

- **Frontend**: Vue 3, TypeScript, Pinia (state management), Vue Router, Bootstrap 5, Axios
- **Backend**: FastAPI, SQLModel, PostgreSQL, JWT authentication, bcrypt
- **Infrastructure**: Docker Compose, Nginx (production), Gunicorn
- **AI/ML**:
  - LLMs: Gemini API, OpenAI, Anthropic (via Langchain)
  - Embeddings: OpenAI Embeddings, Google Embeddings
  - Frameworks: Langchain, Langgraph

## Development Commands

### Backend (FastAPI)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.template .env
# Edit .env with your configuration

# Run development server
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Run with Gunicorn (production)
gunicorn -c gunicorn.conf.py main:app
```

### Frontend (Vue 3)

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview

# Format code
npm run format

# Unit tests (Vitest)
npm run test:unit

# E2E tests (Playwright)
npx playwright install  # First time only
npm run test:e2e
npm run test:e2e -- --project=chromium  # Specific browser
npm run test:e2e -- tests/example.spec.ts  # Specific test
npm run test:e2e -- --debug  # Debug mode
```

### Docker

```bash
# Start all services (frontend, backend)
# Note: PostgreSQL should be configured as external service (Zeabur, AWS RDS, etc.)
docker-compose up

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Backend Architecture

### Application Factory Pattern

- Entry point: `backend/main.py` → imports `create_app()` from `app/__init__.py`
- FastAPI app created with lifespan context manager for Snowflake ID generator initialization
- CORS middleware configured for `http://localhost:5173` (development frontend)

### Database & Models

- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **ID Generation**: Snowflake IDs for distributed unique identifiers (worker-based)
- **Models location**: `backend/app/model/`
  - `user_model.py`: User table with Snowflake IDs, bcrypt password hashing
  - `chat_model.py`: Chat history and messages
  - `document_model.py`: Document metadata, chunks, and vector store config
- **Database**: External managed PostgreSQL (Zeabur, AWS RDS, Supabase, etc.)

### Authentication & Authorization

- **JWT tokens**: Created in `app/auth.py` using `create_access_token()`
- **Token verification**: `verify_access_token()` decodes JWT and validates user
- **Protected routes**: Use `Depends(get_current_user)` dependency
- **Password hashing**: bcrypt via `UserService.hash_the_password()`
- **Cookie-based auth**: JWT tokens stored in httpOnly cookies (sessionId)

### Router Structure

- **Main router**: `app/router/__init__.py` aggregates all sub-routers
- **API prefix**: All routes prefixed with `/api/v1` (configured in `config.py`)
- **User routes** (`user_router.py`):
  - Authenticated: `/api/v1/user/` (requires JWT)
  - Non-authenticated: `/api/v1/user/` (registration)
- **Chat routes** (`chat_router.py`):
  - `/api/v1/chat/` - Chat with LLM (supports RAG mode)
  - `/api/v1/chat/history` - Chat history management
- **Document routes** (`document_router.py`):
  - `/api/v1/documents/upload` - Upload documents
  - `/api/v1/documents/ingest/text` - Ingest text
  - `/api/v1/documents/ingest/url` - Ingest from URL
  - `/api/v1/documents/` - List documents
  - `/api/v1/documents/{id}` - Get/delete document

### Configuration

- **Settings**: Pydantic BaseSettings in `app/config.py`
- **Environment variables**: Loaded from `.env` file
- **Required env vars**: DB credentials, SECRET_KEY, GEMINI_API_KEY, FRONTEND_HOST
- **Template**: Use `.env.template` as reference

### Services Layer

- Business logic in `app/service/` directory
- **User Service** (`user_service.py`): User CRUD operations, password hashing/verification
- **Chat Service** (`chat_service.py`): Chat history and message management
- **LLM Service** (`llm/`): Multi-provider LLM support (Gemini, OpenAI, Anthropic)
- **RAG Service** (`rag/`): Complete RAG pipeline implementation
  - `embedding_service.py`: Text embedding generation
  - `query_processor.py`: Query preprocessing
  - `retrieval_service.py`: Semantic document retrieval
  - `prompt_builder.py`: Context-aware prompt construction
  - `rag_pipeline.py`: End-to-end RAG orchestration
  - `document_ingestion.py`: Document processing and indexing

## Frontend Architecture

### State Management (Pinia)

- **User store**: `stores/user.ts` manages authentication state (username, token)
- **Logout function**: `logout()` clears user state

### API Communication

- **Axios instance**: Configured in `api/service.ts`
- **Base URL**: Set via `VITE_API_BASE_URL` environment variable
- **Interceptors**:
  - Request: Automatically adds `Authorization: Bearer {token}` header from Pinia store
  - Response: Handles 401 (auto-logout), 403, 500 errors globally

### Routing

- **Router**: `router/index.ts` uses Vue Router with history mode
- **Current routes**:
  - `/` → `views/index.vue` (Home)
  - `/:pathMatch(.*)*` → `views/NotFound.vue` (404)
- **View structure**:
  - `views/auth/`: Authentication pages (Login, Register, ForgetPassword, Auth)
  - `views/dashboard/`: Dashboard, Chat
  - `components/`: Reusable components (Sidebar)

### Styling

- **Framework**: Bootstrap 5
- **SCSS**: Global variables auto-imported in `vite.config.ts`
  - Path: `@/assets/styles/scss/_variables.scss`
- **Alias**: `@` resolves to `frontend/src/`

### Internationalization

- **Library**: vue-i18n
- **Setup**: `utils/i18n.ts` and `utils/locale.ts`
- **Locale files**: `locale/` directory

### Testing

- **Unit tests**: Vitest with jsdom environment (`vitest.config.ts`)
- **E2E tests**: Playwright (`playwright.config.ts`)
- **Test files**: `__tests__/` directory

## Key Patterns

### Snowflake ID Generation

- Each worker process gets a unique ID (PID % 1024) during startup
- IDs generated via `snowflake_generator()` in `app/utils.py`
- Ensures distributed unique IDs across multiple workers/containers

### Password Security

- Never store plaintext passwords
- Hash passwords using bcrypt in `UserService.hash_the_password()`
- Store as bytes in database (`User.password` field)

### Error Handling

- Backend: Custom error codes in `app/error.py`
- Frontend: Axios interceptors handle common HTTP errors
- Use FastAPI's `HTTPException` for API errors

### CORS Configuration

- Development: Frontend runs on port 5173, backend on 5000
- CORS middleware in `app/__init__.py` allows localhost:5173
- Production: Nginx proxies frontend (port 80) to backend (port 5000)

## Node Version

Project requires Node.js version ^20.19.0 or >=22.12.0 (specified in `frontend/package.json`).

## RAG (Retrieval-Augmented Generation) with Gemini File Search

### Overview

The application uses **Google's Gemini File Search API** for RAG functionality. This provides:

- Automatic document chunking and embedding
- Built-in semantic search
- Integrated citations and grounding metadata
- No manual vector store management

### How It Works

```
User uploads documents → Gemini File Search Store → Documents indexed automatically
    ↓
User query → Gemini File Search retrieval → Context-aware LLM response with citations
```

### Key Components

1. **Document Upload**: Files uploaded to Gemini File Search Store (per-user)
2. **Automatic Indexing**: Gemini handles chunking, embedding, and vector storage
3. **RAG Query**: Gemini retrieves relevant context and generates responses
4. **Citations**: Built-in grounding metadata shows which documents were used

### Using RAG

**Upload documents (Authentication required):**

```bash
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"
```

**Ingest text:**

```bash
curl -X POST http://localhost:5000/api/v1/documents/ingest/text \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ML Basics",
    "content": "Machine learning is a subset of AI..."
  }'
```

**Chat with RAG enabled (Authentication required):**

```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": true,
    "provider": "gemini"
  }'
```

**Get store information:**

```bash
curl -X GET http://localhost:5000/api/v1/documents/stores/info \
  -H "Authorization: Bearer <token>"
```

### Configuration

```bash
# .env configuration
GEMINI_API_KEY=your-gemini-api-key-here         # Required for RAG
GEMINI_FILE_SEARCH_MODEL=gemini-2.5-flash-lite   # Model for RAG queries
GEMINI_STORE_SIZE_LIMIT_GB=20                   # Recommended size limit per store
GEMINI_MAX_FILE_SIZE_MB=100                     # Max file size for upload
```

### Supported File Formats

- **Documents**: PDF, DOCX, TXT, MD, RTF
- **Data**: JSON, CSV, XML, YAML
- **Code**: Python, Java, JavaScript, TypeScript, Go, etc.
- **Presentations**: PPTX
- **Spreadsheets**: XLSX
- **Max size**: 100MB per file

### Key Features

- **Per-User Stores**: Each user has their own File Search Store
- **Automatic Management**: No manual chunking or embedding configuration
- **Built-in Citations**: Responses include grounding metadata
- **Cost-Effective**: Only pay for indexing ($0.15/1M tokens), storage is free
- **Persistent Storage**: Documents remain until explicitly deleted
