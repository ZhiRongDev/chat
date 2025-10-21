# RAG Quick Start Guide

## What is RAG?

RAG (Retrieval-Augmented Generation) enhances AI responses by retrieving relevant information from your document knowledge base before generating answers.

## Quick Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.template .env
# Edit .env and add your API keys
```

Required API keys (at least one):
- `GEMINI_API_KEY` - Google Gemini
- `OPENAI_API_KEY` - OpenAI (required for embeddings if using OpenAI)

### 3. Run Database Migrations

```bash
# Create database tables including new document models
# The application will auto-create tables on first run
python main.py
```

### 4. Start the Application

```bash
# Development
python main.py

# Production
gunicorn -c gunicorn.conf.py main:app
```

## Using RAG in 3 Steps

### Step 1: Upload Documents

**Via API:**
```bash
# Get authentication token first
TOKEN=$(curl -X POST http://localhost:5000/api/v1/token \
  -d "username=your_user&password=your_password" | jq -r .access_token)

# Upload a PDF document
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"
```

**Or ingest text directly:**
```bash
curl -X POST http://localhost:5000/api/v1/documents/ingest/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning Basics",
    "content": "Machine learning is a method of data analysis that automates analytical model building..."
  }'
```

### Step 2: Chat with RAG

```bash
# Query with RAG enabled
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "use_rag": true,
    "top_k": 5
  }'
```

### Step 3: Manage Documents

**List documents:**
```bash
curl http://localhost:5000/api/v1/documents/ \
  -H "Authorization: Bearer $TOKEN"
```

**Get document details:**
```bash
curl http://localhost:5000/api/v1/documents/{document_id} \
  -H "Authorization: Bearer $TOKEN"
```

**Delete document:**
```bash
curl -X DELETE http://localhost:5000/api/v1/documents/{document_id} \
  -H "Authorization: Bearer $TOKEN"
```

## Python SDK Usage

```python
from app.service.rag import RAGPipeline, DocumentIngestionService

# Initialize services
ingestion = DocumentIngestionService()
rag = RAGPipeline()

# Ingest a document
doc = ingestion.ingest_text(
    text="Your document content here...",
    title="My Document",
    user_id=123
)

# Query with RAG
result = rag.query("What is this document about?")
print(result["response"])

# Stream response
async for chunk in rag.astream("Explain this topic"):
    print(chunk, end="", flush=True)
```

## Configuration Options

### Chat Payload Parameters

```json
{
  "message": "Your question here",
  "use_rag": true,           // Enable RAG mode
  "top_k": 5,                // Number of documents to retrieve (default: 5)
  "min_score": 0.3,          // Minimum relevance score (0.0-1.0, default: 0.3)
  "provider": "openai",      // LLM provider (gemini, openai, anthropic)
  "model": "gpt-4",          // Specific model (optional)
  "temperature": 0.7         // Generation temperature (0.0-1.0)
}
```

### Environment Variables

```bash
# Embedding Configuration
EMBEDDING_PROVIDER=openai              # openai or google (auto-detected if not set)
EMBEDDING_MODEL=text-embedding-3-small # or models/embedding-001
VECTOR_STORE_TYPE=faiss                # faiss or chromadb

# Chunking
CHUNK_SIZE=512                         # Tokens per chunk
CHUNK_OVERLAP=50                       # Overlap between chunks

# Retrieval
RAG_TOP_K=5                            # Default number of documents
RAG_MIN_SCORE=0.3                      # Minimum relevance threshold
```

## Supported Document Formats

- **PDF** (.pdf) - Extracted with pypdf
- **Text** (.txt) - Plain text files
- **Markdown** (.md) - Markdown files
- **URLs** - Web page content
- **Raw text** - Direct text input via API

## How It Works

1. **Document Ingestion**:
   - Upload → Extract text → Split into chunks → Generate embeddings → Store in vector database

2. **Query Processing**:
   - User query → Clean text → Generate embedding

3. **Retrieval**:
   - Search vector store → Find top-k similar chunks → Rank by relevance

4. **Response Generation**:
   - Format context + query → Send to LLM → Generate answer → Add citations

## Tips for Best Results

1. **Document Quality**:
   - Use clean, well-formatted documents
   - Remove unnecessary content before upload
   - Add descriptive titles

2. **Chunking**:
   - Default 512 tokens works for most documents
   - Use 256 for precise retrieval
   - Use 1024 for broad context

3. **Retrieval Tuning**:
   - Start with `top_k=5`, `min_score=0.3`
   - Increase `top_k` for complex questions
   - Increase `min_score` for precise answers
   - Decrease `min_score` if no results returned

4. **Performance**:
   - Use FAISS for production (faster)
   - Use ChromaDB for development (easier debugging)
   - Upload documents in batches
   - Monitor vector store size

## Troubleshooting

### No documents retrieved
- **Check**: Document is uploaded and status is "completed"
- **Fix**: Lower `min_score` or increase `top_k`

### Poor retrieval quality
- **Check**: Embedding model and query preprocessing
- **Fix**: Try different embedding provider or adjust chunk size

### Slow responses
- **Check**: Vector store type and number of documents
- **Fix**: Use FAISS, reduce `top_k`, optimize chunk size

### Out of memory
- **Check**: Number of documents and chunk sizes
- **Fix**: Reduce `chunk_size`, limit document uploads, use pagination

## Next Steps

- Read [RAG_ARCHITECTURE.md](backend/RAG_ARCHITECTURE.md) for detailed architecture
- Read [CLAUDE.md](CLAUDE.md) for complete project documentation
- Check API documentation at http://localhost:5000/docs
- Explore example code in `backend/app/service/rag/`

## Support

For issues or questions:
- Check the documentation
- Review error messages in logs
- Test with smaller documents first
- Verify API keys are configured correctly
