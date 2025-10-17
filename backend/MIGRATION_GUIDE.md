# Migration Guide: Enhanced Chat with LangGraph

This guide helps you migrate from the previous Gemini-only chat implementation to the new multi-provider LangGraph-based system.

## What's New?

### Before (Old Implementation)
- Single LLM provider (Google Gemini only)
- Direct API calls
- No search capabilities
- Fixed model selection

### After (New Implementation)
- Multiple LLM providers (Gemini, OpenAI, Anthropic)
- LangGraph-based reasoning workflow
- Google Search integration (Serper/Tavily)
- Flexible provider and model selection
- Enhanced error handling

## Breaking Changes

### 1. API Request Format

**Old Format:**
```json
{
  "message": "Hello, how are you?"
}
```

**New Format (Backward Compatible):**
```json
{
  "message": "Hello, how are you?",
  "provider": "gemini",      // Optional - defaults to DEFAULT_LLM_PROVIDER
  "model": null,             // Optional - uses provider default
  "temperature": 0.7,        // Optional - defaults to 0.7
  "use_search": true         // Optional - defaults to true
}
```

**Good News**: The old format still works! If you only send `message`, the system uses default settings.

### 2. Environment Variables

**New Required Variables:**
Add to your `.env` file:

```bash
# At least ONE LLM provider is required
GEMINI_API_KEY=your_key_here

# Optional additional providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Optional search APIs (recommended)
SERPER_API_KEY=
TAVILY_API_KEY=

# Default provider
DEFAULT_LLM_PROVIDER=gemini
```

**Migration Steps:**
1. Copy `.env.template` to `.env` if not already done
2. Keep your existing `GEMINI_API_KEY`
3. Add new optional keys as needed
4. Set `DEFAULT_LLM_PROVIDER=gemini` to maintain current behavior

### 3. Dependencies

**Action Required:**
```bash
cd backend
pip install -r requirements.txt
```

This installs:
- LangChain (core, community, providers)
- LangGraph
- Search API clients

## Migration Paths

### Path 1: Minimal Migration (Keep Current Behavior)

If you want to keep the exact same behavior:

1. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update `.env` (keep existing Gemini key):
   ```bash
   GEMINI_API_KEY=your_existing_key
   DEFAULT_LLM_PROVIDER=gemini
   # Leave other keys empty for now
   ```

3. No code changes needed! Your existing API calls will work.

### Path 2: Add Search Capabilities

Enhance responses with Google Search:

1. Follow Path 1 steps

2. Get a Serper API key from https://serper.dev/ (free tier available)

3. Add to `.env`:
   ```bash
   SERPER_API_KEY=your_serper_key
   ```

4. Search is automatically enabled! The agent will use it when needed.

### Path 3: Multi-Provider Setup

Use different LLM providers:

1. Follow Path 2 steps

2. Get additional API keys:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

3. Add to `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

4. Switch providers via API:
   ```json
   {
     "message": "Hello",
     "provider": "openai"  // or "anthropic"
   }
   ```

## Frontend Migration

### Old Frontend Code:
```typescript
const response = await fetch('/api/v1/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userMessage })
});
```

### New Frontend Code (Enhanced):
```typescript
const response = await fetch('/api/v1/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userMessage,
    provider: selectedProvider,  // Optional: from dropdown
    temperature: 0.7,            // Optional: from slider
    use_search: searchEnabled    // Optional: from toggle
  })
});
```

### Check Available Providers:
```typescript
// New status endpoint
const status = await fetch('/api/v1/chat/status');
const data = await status.json();
// Returns: { available_providers: [...], search_enabled: bool, ... }
```

## Testing Your Migration

### 1. Basic Test (No Search)
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?", "use_search": false}'
```

### 2. Search Test
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the latest news about AI?"}'
```

### 3. Provider Test
```bash
# Test with OpenAI (if configured)
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "provider": "openai"}'
```

### 4. Status Test
```bash
curl http://localhost:5000/api/v1/chat/status
```

Expected response:
```json
{
  "available_providers": ["gemini"],
  "search_enabled": true,
  "default_provider": "gemini"
}
```

## Common Issues & Solutions

### Issue 1: Import Errors
**Error**: `ModuleNotFoundError: No module named 'langchain'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Issue 2: API Key Not Found
**Error**: `ValueError: GEMINI_API_KEY is not configured`

**Solution**: Check `.env` file has the key set:
```bash
GEMINI_API_KEY=your_actual_key_here
```

### Issue 3: Provider Not Available
**Error**: `Provider 'openai' is not available`

**Solution**: Either:
- Add `OPENAI_API_KEY` to `.env`, or
- Don't specify provider in request (uses default)

### Issue 4: Slow Responses
**Cause**: Search adds 1-3 seconds

**Solution**: Disable search for simple queries:
```json
{"message": "What is 2+2?", "use_search": false}
```

## Rollback Plan

If you need to rollback to the old implementation:

1. Restore old `chat_router.py`:
   ```bash
   git checkout HEAD -- backend/app/router/chat_router.py
   ```

2. Remove new dependencies (optional):
   ```bash
   pip uninstall langchain langchain-core langgraph -y
   ```

3. Restart server

## Performance Comparison

| Feature | Old | New | Notes |
|---------|-----|-----|-------|
| Response Time | ~1-2s | ~1-3s | +1s if search is used |
| Providers | 1 | 3+ | Gemini, OpenAI, Anthropic |
| Search | No | Yes | Optional, auto-triggered |
| Streaming | Yes | Yes | Unchanged |
| Error Handling | Basic | Enhanced | Better error messages |

## Recommended Migration Timeline

1. **Day 1**: Install dependencies, test with Gemini only
2. **Day 2**: Add search API key, test search functionality
3. **Day 3**: Add alternative providers (optional)
4. **Day 4**: Update frontend to expose new features (optional)

## Support

For issues or questions:
- Check the [LLM Service README](backend/app/service/llm/README.md)
- Review the [API documentation](http://localhost:5000/docs) (FastAPI auto-docs)
- Test with the `/chat/status` endpoint

## Next Steps

After migration:
1. Monitor response quality and performance
2. Collect user feedback on search integration
3. Consider adding UI controls for provider selection
4. Explore custom tools and RAG capabilities

---

**Questions?** Check the main documentation or test thoroughly in development before deploying to production.
