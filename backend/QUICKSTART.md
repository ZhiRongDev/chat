# Quick Start Guide - Enhanced Chat System

Get up and running with the new LangGraph-based chat system in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Configure API Keys (2 minutes)

### Option A: Minimal Setup (Keep using Gemini)

Edit your `.env` file:
```bash
GEMINI_API_KEY=your_existing_gemini_key_here
DEFAULT_LLM_PROVIDER=gemini
```

That's it! You're ready to go.

### Option B: Add Search (Recommended)

1. Get a free Serper API key: https://serper.dev/
2. Add to `.env`:
```bash
SERPER_API_KEY=your_serper_key_here
```

Now your chat can search the web for current information!

### Option C: Multi-Provider Setup

Add more LLM providers to `.env`:
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

Get keys from:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

## Step 3: Test It! (2 minutes)

### Quick Test
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Test Search (if configured)
```bash
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the latest news about AI?"}'
```

### Check Status
```bash
curl http://localhost:5000/api/v1/chat/status
```

Expected output:
```json
{
  "available_providers": ["gemini"],
  "search_enabled": true,
  "default_provider": "gemini"
}
```

## Step 4: Try the Interactive Example

```bash
python examples/chat_example.py
```

Choose option 6 for an interactive chat session!

## API Quick Reference

### Basic Request (Backward Compatible)
```json
{
  "message": "Your question here"
}
```

### Full Request (All Options)
```json
{
  "message": "Your question here",
  "provider": "gemini",      // "openai", "anthropic" (optional)
  "model": null,             // Specific model (optional)
  "temperature": 0.7,        // 0.0-1.0 (optional)
  "use_search": true         // Enable/disable search (optional)
}
```

### Frontend Example (JavaScript/TypeScript)
```javascript
const response = await fetch('/api/v1/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userInput,
    // Optional: add provider, temperature, etc.
  })
});

// Stream the response
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  console.log(chunk); // Display to user
}
```

## Common Use Cases

### 1. Fast Responses (No Search)
```json
{
  "message": "What is 2+2?",
  "use_search": false
}
```

### 2. Current Information (With Search)
```json
{
  "message": "What happened in the news today?",
  "use_search": true
}
```

### 3. Creative Writing (High Temperature)
```json
{
  "message": "Write a poem about coding",
  "temperature": 1.0,
  "use_search": false
}
```

### 4. Factual Answers (Low Temperature)
```json
{
  "message": "Explain quantum mechanics",
  "temperature": 0.2
}
```

### 5. Switch Providers
```json
{
  "message": "Hello",
  "provider": "anthropic"  // or "openai"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| "GEMINI_API_KEY is not configured" | Add key to `.env` file |
| "Provider not available" | Add corresponding API key or omit provider field |
| Slow responses | Set `"use_search": false` or use faster models |
| 404 errors | Make sure server is running on correct port |

## What Changed?

### Old Way (Still Works!)
```python
# Simple message only
{"message": "Hello"}
```

### New Way (More Features!)
```python
# Choose provider, enable search, adjust temperature
{
  "message": "Hello",
  "provider": "openai",
  "temperature": 0.7,
  "use_search": true
}
```

## Features at a Glance

✅ **Multi-Provider**: Switch between Gemini, OpenAI, Anthropic
✅ **Smart Search**: Automatically searches when needed
✅ **Streaming**: Real-time token-by-token responses
✅ **Flexible**: Adjust temperature, model, search per request
✅ **Backward Compatible**: Old API calls still work
✅ **Well Documented**: Comprehensive docs and examples

## Next Steps

1. ✅ Basic setup complete
2. 🔄 Try the example script: `python examples/chat_example.py`
3. 📖 Read the full docs: `app/service/llm/README.md`
4. 🚀 Update your frontend to use new features
5. 🔍 Add search API key for enhanced results

## Need Help?

- **Full Documentation**: `app/service/llm/README.md`
- **Migration Guide**: `MIGRATION_GUIDE.md`
- **Summary**: `LANGGRAPH_UPGRADE_SUMMARY.md`
- **Examples**: `examples/chat_example.py`
- **API Docs**: http://localhost:5000/docs

## Tips

💡 Start with Gemini only (fastest setup)
💡 Add search for current information queries
💡 Use low temperature (0.2-0.3) for facts
💡 Use high temperature (0.8-1.0) for creativity
💡 Disable search for simple math/logic questions
💡 Check `/api/v1/chat/status` to see what's available

---

**You're ready to go!** 🎉

The system is backward compatible, so your existing code will keep working while you explore the new features.
