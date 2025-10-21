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
- **Backend**: FastAPI, SQLModel, PostgreSQL, Redis, JWT authentication, bcrypt
- **Infrastructure**: Docker Compose, Nginx (production), Gunicorn
- **AI/ML**:
  - LLMs: Gemini API, OpenAI, Anthropic (via Langchain)
  - RAG: FAISS, ChromaDB (vector stores)
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
# Start all services (frontend, backend, PostgreSQL, Redis)
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
- **Database**: PostgreSQL via docker-compose (port 5432)
- **Caching**: Redis via docker-compose (port 6379)
- **Vector Store**: FAISS/ChromaDB for document embeddings (stored in `data/vector_stores/`)

### Authentication & Authorization
- **JWT tokens**: Created in `app/auth.py` using `create_access_token()`
- **Token verification**: `verify_access_token()` decodes JWT and validates user
- **Protected routes**: Use `Depends(get_current_user)` dependency
- **Password hashing**: bcrypt via `UserService.hash_the_password()`
- **OAuth2 scheme**: Token URL at `/api/v1/token`

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
- **Required env vars**: DB credentials, Redis config, SECRET_KEY, GEMINI_API_KEY, FRONTEND_HOST
- **Template**: Use `.env.template` as reference

### Services Layer
- Business logic in `app/service/` directory
- **User Service** (`user_service.py`): User CRUD operations, password hashing/verification
- **Chat Service** (`chat_service.py`): Chat history and message management
- **LLM Service** (`llm/`): Multi-provider LLM support (Gemini, OpenAI, Anthropic)
- **RAG Service** (`rag/`): Complete RAG pipeline implementation
  - `embedding_service.py`: Text embedding generation
  - `vector_store.py`: FAISS/ChromaDB management
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

## RAG (Retrieval-Augmented Generation)

### Overview
The application implements a complete RAG system that enhances LLM responses with relevant context from a knowledge base.

### RAG Pipeline
```
User Query → Query Preprocessing → Vector Store Search → Top-k Documents
    ↓
Prompt Builder → LLM → Response with Citations
```

### Key Components
1. **Query Preprocessing**: Clean query, generate embedding
2. **Vector Store**: FAISS/ChromaDB for semantic search
3. **Retrieval**: Top-k most relevant document chunks
4. **Prompt Builder**: Format context with query for LLM
5. **Response Generator**: LLM with citations

### Using RAG

**Chat with RAG enabled:**
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": true,
    "top_k": 5,
    "min_score": 0.3
  }'
```

**Upload documents:**
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

### Configuration
```bash
# .env configuration
EMBEDDING_PROVIDER=openai              # or google
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_TYPE=faiss                # or chromadb
CHUNK_SIZE=512
CHUNK_OVERLAP=50
RAG_TOP_K=5
RAG_MIN_SCORE=0.3
```

### Architecture Details
See [RAG_ARCHITECTURE.md](backend/RAG_ARCHITECTURE.md) for complete documentation including:
- Detailed component descriptions
- API endpoint reference
- Performance tuning
- Best practices
- Troubleshooting guide
