# RAG Architecture Documentation

## Overview

This application implements a complete **RAG (Retrieval-Augmented Generation)** system that enhances LLM responses with relevant context from a knowledge base. The system follows a multi-stage pipeline architecture.

## RAG Pipeline Workflow

```
User Query
   ↓
1. Query Preprocessing (cleaning, embedding)
   ↓
2. Vector Store Search (semantic retrieval from FAISS/ChromaDB)
   ↓
3. Top-k Context Documents
   ↓
4. Prompt Builder (LLM Input with context)
   ↓
5. LLM (OpenAI, Claude, Gemini, etc.)
   ↓
6. Response Generator (with citations)
```

## Architecture Components

### 1. Query Preprocessing (`query_processor.py`)
- **Purpose**: Clean and prepare user queries for retrieval
- **Features**:
  - Text cleaning and normalization
  - Stopword removal
  - Query embedding generation
  - Keyword extraction
- **Key Methods**:
  - `preprocess(query)` - Clean and normalize query
  - `embed_query(query)` - Generate query embedding
  - `process_and_embed(query)` - Complete preprocessing pipeline

### 2. Embedding Service (`embedding_service.py`)
- **Purpose**: Generate text embeddings using various providers
- **Supported Providers**:
  - OpenAI (text-embedding-3-small, text-embedding-3-large)
  - Google (models/embedding-001)
- **Features**:
  - Batch embedding generation
  - Text chunking with token counting
  - Hash generation for deduplication
- **Key Methods**:
  - `embed_text(text)` - Single text embedding
  - `embed_texts(texts)` - Batch embeddings
  - `chunk_text(text, chunk_size, overlap)` - Smart chunking

### 3. Vector Store (`vector_store.py`)
- **Purpose**: Manage vector embeddings for fast similarity search
- **Supported Stores**:
  - **FAISS**: Fast, in-memory, ideal for production
  - **ChromaDB**: Feature-rich, persistent, easier debugging
- **Features**:
  - Similarity search (cosine, euclidean, dot product)
  - Batch insertion
  - Document deletion
  - Persistence to disk
- **Key Methods**:
  - `add_embeddings(embeddings, ids, metadata)` - Store vectors
  - `similarity_search(query_embedding, k)` - Retrieve top-k results
  - `delete_by_ids(ids)` - Remove documents

### 4. Retrieval Service (`retrieval_service.py`)
- **Purpose**: Coordinate semantic search and document retrieval
- **Features**:
  - Top-k document retrieval
  - Relevance score filtering
  - Context expansion (surrounding chunks)
  - Document-specific search
- **Key Methods**:
  - `retrieve(query, top_k, min_score)` - Main retrieval
  - `retrieve_with_context(query, context_chunks)` - Include surrounding text
  - `retrieve_by_document(document_id)` - Document-specific retrieval

### 5. Prompt Builder (`prompt_builder.py`)
- **Purpose**: Construct LLM prompts with retrieved context
- **Features**:
  - Context formatting with sources
  - Token limit management
  - Citation generation
  - Multiple output formats (chat, completion)
- **Key Methods**:
  - `build_context(results)` - Format retrieved documents
  - `build_messages(query, results)` - Create chat messages
  - `add_citations(response, results)` - Add source citations

### 6. RAG Pipeline (`rag_pipeline.py`)
- **Purpose**: Orchestrate the complete RAG workflow
- **Features**:
  - End-to-end query processing
  - Streaming responses
  - Configurable retrieval parameters
  - Pipeline statistics
- **Key Methods**:
  - `query(query, top_k, min_score)` - Synchronous RAG
  - `aquery(query)` - Asynchronous RAG
  - `astream(query)` - Streaming RAG response
  - `retrieve_only(query)` - Retrieval without generation

### 7. Document Ingestion (`document_ingestion.py`)
- **Purpose**: Process and index documents into the knowledge base
- **Supported Formats**:
  - PDF (.pdf)
  - Text (.txt, .md)
  - URLs (web pages)
  - Raw text input
- **Features**:
  - Automatic text extraction
  - Smart chunking
  - Duplicate detection (content hashing)
  - Batch processing
  - Error handling
- **Key Methods**:
  - `ingest_file(file, filename, user_id)` - Upload file
  - `ingest_text(text, title, user_id)` - Direct text
  - `ingest_url(url, user_id)` - Web content
  - `delete_document(document_id)` - Remove document

## Database Models

### Document Model
```python
Document:
  - id: Snowflake ID
  - user_id: Owner
  - filename: Original name
  - file_type: Format (pdf, txt, etc.)
  - file_size: Bytes
  - content_hash: SHA-256 for deduplication
  - chunk_count: Number of chunks
  - status: pending/processing/completed/failed
  - metadata: Custom JSON
```

### DocumentChunk Model
```python
DocumentChunk:
  - id: Snowflake ID
  - document_id: Parent document
  - chunk_index: Order in document
  - content: Text content
  - content_hash: SHA-256
  - token_count: Token count
  - embedding_model: Model used
  - vector_id: ID in vector store
  - metadata: Custom JSON
```

### VectorStoreConfig Model
```python
VectorStoreConfig:
  - name: Store identifier
  - store_type: faiss/chromadb
  - embedding_model: Model name
  - embedding_dimension: Vector dimension
  - distance_metric: cosine/euclidean/dot
  - config: Store-specific settings
```

## API Endpoints

### Chat Endpoints

#### POST `/api/v1/chat/` (RAG-enabled)
Enhanced chat with RAG support:
```json
{
  "message": "What is machine learning?",
  "use_rag": true,
  "top_k": 5,
  "min_score": 0.3,
  "provider": "openai",
  "temperature": 0.7
}
```

### Document Management Endpoints

#### POST `/api/v1/documents/upload`
Upload document file:
```bash
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"
```

#### POST `/api/v1/documents/ingest/text`
Ingest text directly:
```json
{
  "title": "Machine Learning Basics",
  "content": "Machine learning is a subset of artificial intelligence...",
  "metadata": {"category": "education"}
}
```

#### POST `/api/v1/documents/ingest/url`
Ingest from URL:
```json
{
  "url": "https://example.com/article",
  "metadata": {"source": "web"}
}
```

#### GET `/api/v1/documents/`
List user's documents:
```bash
curl http://localhost:5000/api/v1/documents/ \
  -H "Authorization: Bearer <token>"
```

#### GET `/api/v1/documents/{document_id}`
Get document details:
```bash
curl http://localhost:5000/api/v1/documents/123456?include_chunks=true \
  -H "Authorization: Bearer <token>"
```

#### DELETE `/api/v1/documents/{document_id}`
Delete document:
```bash
curl -X DELETE http://localhost:5000/api/v1/documents/123456 \
  -H "Authorization: Bearer <token>"
```

#### GET `/api/v1/documents/stats/overview`
Get statistics:
```bash
curl http://localhost:5000/api/v1/documents/stats/overview \
  -H "Authorization: Bearer <token>"
```

## Configuration

### Environment Variables

```bash
# Embedding Configuration
EMBEDDING_PROVIDER=openai              # or google (auto-detected if not set)
EMBEDDING_MODEL=text-embedding-3-small # or models/embedding-001
VECTOR_STORE_TYPE=faiss                # or chromadb

# Chunking Configuration
CHUNK_SIZE=512                         # Tokens per chunk
CHUNK_OVERLAP=50                       # Overlap between chunks

# Retrieval Configuration
RAG_TOP_K=5                            # Number of documents to retrieve
RAG_MIN_SCORE=0.3                      # Minimum relevance score (0.0-1.0)
```

## Usage Examples

### Python SDK Usage

```python
from app.service.rag import RAGPipeline, DocumentIngestionService

# Initialize RAG pipeline
rag = RAGPipeline(
    llm_provider="openai",
    llm_model="gpt-4",
    top_k=5,
    min_score=0.3
)

# Query with RAG (synchronous)
result = rag.query("What is machine learning?")
print(result["response"])
print(f"Retrieved {result['document_count']} documents")

# Query with streaming
async for chunk in rag.astream("Explain deep learning"):
    print(chunk, end="", flush=True)

# Ingest documents
ingestion = DocumentIngestionService()

# Ingest text
doc = ingestion.ingest_text(
    text="Machine learning is a method of data analysis...",
    title="ML Introduction",
    user_id=123
)

# Ingest PDF
with open("document.pdf", "rb") as f:
    doc = ingestion.ingest_file(f, "document.pdf", user_id=123)

# Ingest URL
doc = ingestion.ingest_url(
    "https://en.wikipedia.org/wiki/Machine_learning",
    user_id=123
)
```

### API Usage

```bash
# 1. Upload a document
curl -X POST http://localhost:5000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@knowledge.pdf"

# 2. Query with RAG
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is in the knowledge document?",
    "use_rag": true,
    "top_k": 5
  }'
```

## Performance Considerations

### Vector Store Selection

**FAISS** (Recommended for Production):
- ✅ Fast in-memory search
- ✅ Scales to millions of vectors
- ✅ Low latency (<10ms)
- ❌ Requires manual persistence
- ❌ Limited metadata filtering

**ChromaDB** (Recommended for Development):
- ✅ Automatic persistence
- ✅ Rich metadata filtering
- ✅ Better debugging tools
- ❌ Slightly slower than FAISS
- ❌ More resource-intensive

### Chunking Strategy

**Optimal Settings**:
- `CHUNK_SIZE=512`: Good balance for most documents
- `CHUNK_OVERLAP=50`: Maintains context continuity
- Smaller chunks (256): Better for precise retrieval
- Larger chunks (1024): Better for broad context

### Retrieval Parameters

**Top-K Selection**:
- `top_k=3`: Fast, focused answers
- `top_k=5`: Balanced (recommended)
- `top_k=10`: Comprehensive, slower

**Score Threshold**:
- `min_score=0.5`: High precision, may miss relevant docs
- `min_score=0.3`: Balanced (recommended)
- `min_score=0.1`: High recall, may include noise

## Monitoring and Debugging

### Pipeline Statistics
```python
rag = RAGPipeline()
stats = rag.get_pipeline_stats()
print(stats)
# Output:
# {
#   'vector_store': {'total_vectors': 1234, 'dimension': 1536, 'store_type': 'faiss'},
#   'embedding_model': 'EmbeddingService(provider=openai, model=text-embedding-3-small)',
#   'llm_model': 'ChatOpenAI(model=gpt-4)',
#   'top_k': 5,
#   'min_score': 0.3
# }
```

### Retrieval Testing
```python
# Test retrieval without LLM generation
results = rag.retrieve_only("machine learning")
for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Document: {result.document_title}")
    print(f"Content: {result.content[:200]}...")
```

## Troubleshooting

### Common Issues

**Problem**: Low retrieval quality
- **Solution**: Adjust `min_score` threshold, increase `top_k`, check embedding model

**Problem**: Slow responses
- **Solution**: Reduce `top_k`, use FAISS instead of ChromaDB, optimize chunk size

**Problem**: Out of memory
- **Solution**: Reduce `chunk_size`, use FAISS with compression, limit document size

**Problem**: Empty retrievals
- **Solution**: Verify documents are indexed, check vector store persistence, lower `min_score`

## Best Practices

1. **Document Preparation**:
   - Clean text before ingestion
   - Remove unnecessary formatting
   - Add meaningful metadata

2. **Chunking Strategy**:
   - Use consistent chunk sizes
   - Ensure overlap for context
   - Test with sample documents

3. **Retrieval Tuning**:
   - Start with default parameters
   - Monitor relevance scores
   - Adjust based on user feedback

4. **Performance**:
   - Use FAISS for production
   - Cache frequently accessed documents
   - Index incrementally

5. **Security**:
   - Implement user-level document isolation
   - Validate file uploads
   - Sanitize text content

## Future Enhancements

- [ ] Hybrid search (semantic + keyword)
- [ ] Query expansion with LLM
- [ ] Document ranking improvements
- [ ] Multi-modal RAG (images, tables)
- [ ] Conversational RAG (chat history)
- [ ] Advanced filters (date, category, tags)
- [ ] Vector store optimization (quantization)
- [ ] Distributed vector stores
