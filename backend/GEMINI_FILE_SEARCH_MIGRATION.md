# Migration Guide: FAISS/ChromaDB → Gemini File Search

This guide explains the migration from the old RAG system (FAISS/ChromaDB) to Google's Gemini File Search API.

## Overview

### What Changed
- **Old System**: Manual chunking, embedding, and vector store management with FAISS/ChromaDB
- **New System**: Google Gemini File Search handles everything automatically

### Why Migrate
1. **Simplified Architecture**: ~1,180 lines of code removed (40% reduction)
2. **Reduced Dependencies**: Removed 5 packages (FAISS, ChromaDB, tiktoken, etc.)
3. **Lower Costs**: No embedding API costs, only indexing ($0.15/1M tokens)
4. **Better Performance**: Google-managed infrastructure
5. **Built-in Citations**: Automatic grounding metadata

## Migration Steps

### 1. Update Environment Variables

**Old `.env`:**
```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_TYPE=faiss
CHUNK_SIZE=512
CHUNK_OVERLAP=50
RAG_TOP_K=5
RAG_MIN_SCORE=0.3
```

**New `.env`:**
```bash
GEMINI_API_KEY=your-gemini-api-key-here         # Required
GEMINI_FILE_SEARCH_MODEL=gemini-2.0-flash-exp
GEMINI_STORE_SIZE_LIMIT_GB=20
GEMINI_MAX_FILE_SIZE_MB=100
```

### 2. Run Database Migration

The migration will:
- Add Gemini-related columns to `document` table
- Create `gemini_file_search_store` table
- Drop `document_chunk` and `vector_store_config` tables

**Using Alembic:**
```bash
cd backend
alembic upgrade head
```

**Manual migration:**
```sql
-- The migration file is at: alembic/versions/001_migrate_to_gemini_file_search.py
-- It can be applied manually or via Alembic
```

### 3. Install/Remove Dependencies

**Remove old packages:**
```bash
pip uninstall faiss-cpu chromadb tiktoken sentence-transformers langchain-chroma
```

**Install from updated requirements.txt:**
```bash
pip install -r requirements.txt
```

### 4. Re-upload Documents

**Important**: Existing documents must be re-uploaded to Gemini File Search Stores.

The old vector store data is not compatible with Gemini File Search. Users need to:

1. Download their existing documents (if needed for backup)
2. Upload documents again using the new API

**Migration script example:**
```python
# This is a conceptual script - adapt as needed
from app.model import engine
from app.model.document_model import Document
from app.service.gemini_file_search_service import GeminiFileSearchService
from sqlmodel import Session, select

def migrate_user_documents(user_id: int):
    """Migrate user's documents to Gemini File Search"""
    gemini_service = GeminiFileSearchService()

    with Session(engine) as session:
        # Get user's old documents
        statement = select(Document).where(Document.user_id == user_id)
        documents = session.exec(statement).all()

        # Create File Search Store for user
        store = gemini_service.get_or_create_user_store(session, user_id)

        for doc in documents:
            if doc.source_url:
                # Re-download and upload if from URL
                # Implementation depends on your needs
                pass
            else:
                # If you have original files, re-upload them
                # gemini_service.upload_file_to_store(...)
                pass
```

### 5. Update Client Code

**Old API call:**
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

**New API call (requires authentication):**
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

**Key changes:**
- ✅ Authentication now required (`Authorization: Bearer <token>`)
- ✅ Must specify `provider: "gemini"` or omit (defaults to gemini for RAG)
- ❌ Removed: `top_k`, `min_score` parameters (Gemini handles this)
- ✅ Optional: `max_output_tokens` for response length

## API Changes

### Document Endpoints (No breaking changes)

All document endpoints remain the same:
- `POST /api/v1/documents/upload` - Upload files
- `POST /api/v1/documents/ingest/text` - Ingest text
- `POST /api/v1/documents/ingest/url` - Ingest from URL
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document

**New endpoint:**
- `GET /api/v1/documents/stores/info` - Get user's File Search Store info

### Chat Endpoint Changes

**Breaking change:** RAG mode now requires authentication.

**Old (non-authenticated):**
```python
@nonauth_router.post("/")
async def chat_stream(payload: ChatPayload):
    # RAG available without authentication
```

**New (authenticated):**
```python
@auth_router.post("/")
async def chat_stream(payload: ChatPayload, current_user: User = Depends(get_current_user)):
    # RAG requires authentication to access user's File Search Store
```

### Response Format

**New response includes citations:**
```
Your answer based on the documents...

[Sources: Retrieved from your documents]
```

The `grounding_metadata` provides details about which documents were used.

## Architecture Changes

### Files Removed
```
backend/app/service/rag/
├── __init__.py
├── document_ingestion.py      (12,338 lines)
├── embedding_service.py        (6,215 lines)
├── prompt_builder.py           (7,707 lines)
├── query_processor.py          (3,997 lines)
├── rag_pipeline.py            (10,304 lines)
├── retrieval_service.py        (9,120 lines)
└── vector_store.py             (9,685 lines)
```

### Files Added
```
backend/app/service/
└── gemini_file_search_service.py  (~450 lines)
```

### Database Schema Changes

**Added to `document` table:**
- `gemini_file_id` - Gemini File API ID
- `gemini_store_id` - File Search Store ID
- `gemini_mime_type` - MIME type
- `gemini_metadata` - Custom metadata

**Removed from `document` table:**
- `chunk_count`

**Tables dropped:**
- `document_chunk`
- `vector_store_config`

**New table:**
- `gemini_file_search_store`

## Configuration Reference

### Gemini File Search Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `GEMINI_API_KEY` | None | **Required** - Gemini API key |
| `GEMINI_FILE_SEARCH_MODEL` | `gemini-2.0-flash-exp` | Model for RAG queries |
| `GEMINI_STORE_SIZE_LIMIT_GB` | 20 | Recommended store size limit |
| `GEMINI_MAX_FILE_SIZE_MB` | 100 | Max file upload size |

### Rate Limits by Tier

| Tier | Storage Limit |
|------|---------------|
| Free | 1 GB |
| Tier 1 | 10 GB |
| Tier 2 | 100 GB |
| Tier 3 | 1 TB |

**Recommendation**: Keep each File Search Store under 20 GB for optimal performance.

### Pricing

- **Indexing**: $0.15 per 1M tokens (one-time cost when uploading)
- **Storage**: Free
- **Query embeddings**: Free
- **Retrieved tokens**: Charged as context tokens in LLM API call

## Troubleshooting

### Issue: "No documents found in your knowledge base"

**Solution**: Upload documents first before using RAG:
```bash
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"
```

### Issue: "RAG mode currently only supports Gemini provider"

**Solution**: Use `provider: "gemini"` or omit the provider parameter:
```json
{
  "message": "your question",
  "use_rag": true,
  "provider": "gemini"
}
```

### Issue: "Gemini API key required for RAG mode"

**Solution**: Set `GEMINI_API_KEY` in your `.env` file or provide it in the request:
```json
{
  "message": "your question",
  "use_rag": true,
  "gemini_api_key": "your-api-key"
}
```

### Issue: Migration failed / Database errors

**Solution**: Check if you have existing data that conflicts:
```bash
# Rollback migration
alembic downgrade -1

# Check for conflicts
# Fix data issues
# Re-run migration
alembic upgrade head
```

## Testing the Migration

### 1. Test Document Upload
```bash
# Upload a test document
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@test.pdf"

# Verify upload
curl -X GET http://localhost:5000/api/v1/documents/ \
  -H "Authorization: Bearer <token>"
```

### 2. Test RAG Query
```bash
# Query with RAG
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize the uploaded document",
    "use_rag": true
  }'
```

### 3. Test Store Info
```bash
# Get store information
curl -X GET http://localhost:5000/api/v1/documents/stores/info \
  -H "Authorization: Bearer <token>"
```

## Rollback Plan

If you need to rollback to the old system:

1. **Rollback database migration:**
```bash
alembic downgrade -1
```

2. **Restore old RAG service files from git:**
```bash
git checkout HEAD -- backend/app/service/rag/
```

3. **Restore old requirements.txt:**
```bash
git checkout HEAD -- backend/requirements.txt
pip install -r requirements.txt
```

4. **Restore old configuration:**
```bash
git checkout HEAD -- backend/app/config.py
git checkout HEAD -- backend/.env.template
```

## Support

For issues or questions:
1. Check the [Gemini File Search API documentation](https://ai.google.dev/gemini-api/docs/file-search)
2. Review the code in [gemini_file_search_service.py](app/service/gemini_file_search_service.py)
3. Open an issue in the project repository
