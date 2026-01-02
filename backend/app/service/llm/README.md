# LLM Service - Multi-Provider Chat with LangGraph

This module provides a flexible, multi-provider LLM integration with LangGraph-based reasoning workflows and optional search capabilities.

## Features

- **Multi-Provider Support**: Switch between Google Gemini, OpenAI, and Anthropic Claude
- **LangGraph Workflow**: Intelligent reasoning with search integration
- **Google Search**: Enhanced responses using Serper API or Tavily Search
- **Streaming Responses**: Real-time token streaming for better UX
- **Flexible Configuration**: Easy provider and model switching via API

## Architecture

### Components

1. **LLM Factory** (`llm_factory.py`)

   - Creates LLM instances for different providers
   - Manages API key validation
   - Provides default models for each provider

2. **Search Tools** (`search_tools.py`)

   - Integrates Google Search via Serper API
   - Integrates Tavily Search API
   - Automatic tool availability detection

3. **Agent Graph** (`agent_graph.py`)
   - LangGraph-based reasoning workflow
   - Query analysis and search decision making
   - Response generation with search context

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit your `.env` file with the required API keys:

```bash
# At least one LLM provider is required
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here          # Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here    # Optional

# Search APIs (at least one recommended)
SERPER_API_KEY=your_serper_api_key_here          # Optional
TAVILY_API_KEY=your_tavily_api_key_here          # Optional

# Default provider
DEFAULT_LLM_PROVIDER=gemini  # Options: gemini, openai, anthropic
```

### 3. Get API Keys

- **Gemini**: https://ai.google.dev/
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Serper (Google Search)**: https://serper.dev/
- **Tavily Search**: https://tavily.com/

## Usage

### API Endpoints

#### 1. Chat Endpoint (Streaming)

**POST** `/api/v1/chat/`

Request body:

```json
{
  "message": "What are the latest developments in AI?",
  "provider": "gemini", // Optional: gemini, openai, anthropic
  "model": "gemini-2.5-flash-lite", // Optional: specific model name
  "temperature": 0.7, // Optional: 0.0 to 1.0
  "use_search": true // Optional: enable/disable search
}
```

Response: Streaming text/plain

#### 2. Status Endpoint

**GET** `/api/v1/chat/status`

Response:

```json
{
  "available_providers": ["gemini", "openai"],
  "search_enabled": true,
  "default_provider": "gemini"
}
```

### Python Usage Examples

#### Basic Usage

```python
from app.service.llm import ChatAgentGraph

# Create agent with default settings
agent = ChatAgentGraph()

# Synchronous call
response = agent.invoke("What is LangGraph?")
print(response)
```

#### With Specific Provider

```python
# Use OpenAI
agent = ChatAgentGraph(provider="openai", model="gpt-4o")
response = agent.invoke("Explain quantum computing")
```

#### Streaming Response

```python
# Async streaming
async def stream_chat():
    agent = ChatAgentGraph(provider="anthropic")
    async for chunk in agent.astream("Tell me a story"):
        print(chunk, end="", flush=True)

# Run in async context
import asyncio
asyncio.run(stream_chat())
```

#### Without Search

```python
# Disable search for faster responses
agent = ChatAgentGraph(use_search=False)
response = agent.invoke("What is 2+2?")
```

### Frontend Integration Example

```typescript
// TypeScript/JavaScript example
async function sendMessage(message: string, provider?: string) {
  const response = await fetch("/api/v1/chat/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      provider: provider || "gemini",
      temperature: 0.7,
      use_search: true,
    }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    console.log(chunk); // Handle streaming chunk
  }
}
```

## LangGraph Workflow

The agent uses a multi-node graph for intelligent processing:

```
┌──────────┐
│ Analyzer │ - Analyzes query and decides if search is needed
└────┬─────┘
     │
     ├─── needs_search? ───┐
     │                     │
     ▼                     ▼
┌────────┐           ┌─────────┐
│ Search │           │ Respond │
└───┬────┘           └─────────┘
    │
    ▼
┌──────────┐
│ Responder│ - Generates final response with search context
└──────────┘
```

### Node Descriptions

1. **Analyzer**: Determines if the query requires current information
2. **Search** (conditional): Executes search tools if needed
3. **Responder**: Generates the final response, incorporating search results if available

## Default Models

| Provider  | Default Model              | Notes                        |
| --------- | -------------------------- | ---------------------------- |
| Gemini    | gemini-2.5-flash-lite      | Fast, efficient, multimodal  |
| OpenAI    | gpt-4o-mini                | Cost-effective, good quality |
| Anthropic | claude-3-5-sonnet-20241022 | High quality, large context  |

## Search Tools

### When Search is Triggered

The agent automatically decides to use search when:

- Query asks about recent events or news
- Query requires current/real-time data
- Query asks for specific facts that may be outdated
- Query explicitly requests "latest" or "current" information

### Search Providers

1. **Serper (Google Search)**

   - Returns top 5 Google search results
   - Best for general web search
   - Fast and reliable

2. **Tavily Search**
   - Optimized for AI/LLM applications
   - Provides comprehensive, structured results
   - Good for research queries

## Performance Considerations

- **Streaming**: All responses stream by default for better UX
- **Search Overhead**: Search adds 1-3 seconds but improves accuracy
- **Model Selection**:
  - Use "flash" models for speed (gemini-2.5-flash-lite)
  - Use "pro" models for quality (gpt-4o, claude-3-5-sonnet)
- **Temperature**:
  - Lower (0.1-0.3) for factual answers
  - Higher (0.7-1.0) for creative responses

## Error Handling

The system handles various error scenarios:

- **Missing API Keys**: Returns 400 with helpful message
- **Invalid Provider**: Returns 400 with available providers
- **LLM Errors**: Streams error message to user
- **Search Failures**: Falls back to LLM-only response

## Testing

```bash
# Test the chat endpoint
curl -X POST http://localhost:5000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the weather today?",
    "provider": "gemini",
    "use_search": true
  }'

# Check status
curl http://localhost:5000/api/v1/chat/status
```

## Troubleshooting

### Issue: Provider not available

**Solution**: Check that the corresponding API key is set in `.env`

### Issue: Search not working

**Solution**: Verify `SERPER_API_KEY` or `TAVILY_API_KEY` is configured

### Issue: Slow responses

**Solution**:

- Disable search with `use_search: false`
- Use faster models (gemini-2.5-flash-lite, gpt-4o-mini)
- Lower temperature

### Issue: Import errors

**Solution**: Reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Future Enhancements

- [ ] Add more LLM providers (Cohere, Mistral, etc.)
- [ ] Implement conversation memory/history
- [ ] Add RAG with vector database
- [ ] Support for multi-modal inputs (images, PDFs)
- [ ] Custom tool creation
- [ ] Caching layer for search results

## License

Part of the chat application project.
