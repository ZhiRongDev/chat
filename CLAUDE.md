# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a resume generator application built with a RAG (Retrieval-Augmented Generation) implementation. The system accepts text descriptions, PDFs, images, or URLs to generate LaTeX resumes with features including user registration (SSO), version comparison, keyword updates, and AI-powered career recommendations.

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
- **AI/ML**: Gemini API, Langchain, Langgraph (planned)

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
  - `chat_model.py`: Chat-related models
- **Database**: PostgreSQL via docker-compose (port 5432)
- **Caching**: Redis via docker-compose (port 6379)

### Authentication & Authorization
- **JWT tokens**: Created in `app/auth.py` using `create_access_token()`
- **Token verification**: `verify_access_token()` decodes JWT and validates user
- **Protected routes**: Use `Depends(get_current_user)` dependency
- **Password hashing**: bcrypt via `UserService.hash_the_password()`
- **OAuth2 scheme**: Token URL at `/api/v1/token`

### Router Structure
- **Main router**: `app/router/__init__.py` aggregates all sub-routers
- **API prefix**: All routes prefixed with `/api/v1` (configured in `config.py`)
- **User routes**:
  - Authenticated: `/api/v1/user/` (requires JWT)
  - Non-authenticated: `/api/v1/user/` (registration)
- **Chat routes**: In `app/router/chat_router.py`

### Configuration
- **Settings**: Pydantic BaseSettings in `app/config.py`
- **Environment variables**: Loaded from `.env` file
- **Required env vars**: DB credentials, Redis config, SECRET_KEY, GEMINI_API_KEY, FRONTEND_HOST
- **Template**: Use `.env.template` as reference

### Services Layer
- Business logic in `app/service/` directory
- `user_service.py`: User CRUD operations, password hashing/verification

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
