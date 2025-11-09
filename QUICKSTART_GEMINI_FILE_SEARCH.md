# Quick Start: Gemini File Search RAG

This guide gets you up and running with the new Gemini File Search RAG system in 5 minutes.

## Prerequisites

- Python 3.10+
- PostgreSQL database running
- Redis running
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Step 1: Configure Environment

```bash
cd backend

# Copy template
cp .env.template .env

# Edit .env and set:
# GEMINI_API_KEY=your-gemini-api-key-here
```

**Required settings:**
```bash
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_FILE_SEARCH_MODEL=gemini-2.0-flash-exp
```

## Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: Old packages (FAISS, ChromaDB, tiktoken) have been removed.

## Step 3: Run Database Migration

```bash
cd backend
alembic upgrade head
```

This will:
- Create `gemini_file_search_store` table
- Update `document` table with Gemini fields
- Remove old `document_chunk` and `vector_store_config` tables

## Step 4: Test the Integration (Optional)

```bash
cd backend
python test_gemini_file_search.py
```

Expected output:
```
============================================================
Testing Gemini File Search Integration
============================================================
✅ Gemini API key found
✅ GeminiFileSearchService initialized
✅ Database connection successful
...
✅ All tests passed!
```

## Step 5: Start the Application

**Using Docker Compose:**
```bash
docker-compose up --build
```

**Or run locally:**
```bash
# Backend
cd backend
python main.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Step 6: Try It Out!

### 6.1 Register/Login

```bash
# Register a new user
curl -X POST http://localhost:5000/api/v1/user/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login to get token
curl -X POST http://localhost:5000/api/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"

# Save the access_token from response
export TOKEN="your-access-token-here"
```

### 6.2 Upload a Document

**Option A: Upload a file**
```bash
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@your-document.pdf"
```

**Option B: Ingest text directly**
```bash
curl -X POST http://localhost:5000/api/v1/documents/ingest/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning Basics",
    "content": "Machine learning is a subset of artificial intelligence (AI) that focuses on building systems that learn from data. Unlike traditional programming, where explicit instructions are provided, machine learning algorithms identify patterns and make decisions with minimal human intervention. Common types include supervised learning, unsupervised learning, and reinforcement learning."
  }'
```

**Option C: Ingest from URL**
```bash
curl -X POST http://localhost:5000/api/v1/documents/ingest/url \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article.pdf"
  }'
```

### 6.3 Check Your Documents

```bash
# List all documents
curl -X GET http://localhost:5000/api/v1/documents/ \
  -H "Authorization: Bearer $TOKEN"

# Get store info
curl -X GET http://localhost:5000/api/v1/documents/stores/info \
  -H "Authorization: Bearer $TOKEN"
```

### 6.4 Chat with RAG

```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": true,
    "provider": "gemini"
  }'
```

**Expected response:**
```
Based on your documents, machine learning is a subset of artificial intelligence...

[Sources: Retrieved from your documents]
```

### 6.5 Compare: Regular Chat vs RAG

**Regular chat (no documents):**
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": false,
    "provider": "gemini"
  }'
```

**RAG chat (uses your documents):**
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": true,
    "provider": "gemini"
  }'
```

The RAG response will be based on your uploaded documents!

## Common Use Cases

### Academic Research
```bash
# Upload research papers
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@research_paper.pdf"

# Ask questions about your research
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the key findings from the research papers",
    "use_rag": true
  }'
```

### Technical Documentation
```bash
# Upload documentation
for doc in docs/*.md; do
  curl -X POST http://localhost:5000/api/v1/documents/upload \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$doc"
done

# Ask technical questions
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I configure the authentication system?",
    "use_rag": true
  }'
```

### Code Knowledge Base
```bash
# Ingest code documentation
curl -X POST http://localhost:5000/api/v1/documents/ingest/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API Reference",
    "content": "..."
  }'

# Ask coding questions
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me an example of using the document upload API",
    "use_rag": true
  }'
```

## Troubleshooting

### Error: "No documents found in your knowledge base"
**Solution**: Upload at least one document first.

### Error: "Gemini API key required for RAG mode"
**Solution**: Set `GEMINI_API_KEY` in `.env` file.

### Error: "RAG mode currently only supports Gemini provider"
**Solution**: Use `"provider": "gemini"` or omit the provider parameter.

### Migration from old system
**Solution**: See [GEMINI_FILE_SEARCH_MIGRATION.md](backend/GEMINI_FILE_SEARCH_MIGRATION.md)

## Advanced Configuration

### Custom RAG Model
```bash
# In .env
GEMINI_FILE_SEARCH_MODEL=gemini-2.5-pro  # Use Pro model for better quality
```

### Adjust Response Length
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain machine learning in detail",
    "use_rag": true,
    "max_output_tokens": 4096
  }'
```

### Custom Temperature
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the main points",
    "use_rag": true,
    "temperature": 0.3
  }'
```

## What's Next?

- 📚 Read the [full migration guide](backend/GEMINI_FILE_SEARCH_MIGRATION.md)
- 🔧 Explore the [service implementation](backend/app/service/gemini_file_search_service.py)
- 📖 Check out [Gemini File Search API docs](https://ai.google.dev/gemini-api/docs/file-search)
- 🧪 Run the [test script](backend/test_gemini_file_search.py)

## Support

- **Documentation**: [CLAUDE.md](CLAUDE.md)
- **API Reference**: Check FastAPI docs at `http://localhost:5000/docs`
- **Issues**: Open an issue in the repository

---

**Happy coding with Gemini File Search! 🚀**
