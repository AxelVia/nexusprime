# 🤖 Multi-API Architecture Documentation

This document provides comprehensive information about NexusPrime's Multi-API architecture, utilizing three separate APIs for optimal performance.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [LLM Router](#llm-router)
- [Model Configuration](#model-configuration)
- [Adding New Providers](#adding-new-providers)
- [Usage Examples](#usage-examples)
- [Cost Estimation](#cost-estimation)
- [Best Practices](#best-practices)

## Overview

NexusPrime leverages multiple large language models (LLMs) through **three separate APIs** to harness their unique strengths:

- **Claude Sonnet 4** (Anthropic API): Excels at precise code generation and requirement analysis
- **Gemini 3 Pro** (Google AI API): Strong technical reasoning and architecture planning
- **Grok 3** (GitHub Models API): Creative thinking and critical analysis
- **GPT-5** (GitHub Models API): Advanced reasoning and validation

Each API provides:
- Direct model access with specialized capabilities
- Independent authentication and rate limiting
- Optimized performance for specific use cases
- Flexible configuration options

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         NexusPrime Factory                      │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Product    │    │  Tech Lead   │    │  Dev Squad   │      │
│  │    Owner     │───▶│              │───▶│              │      │
│  │ (Claude)     │    │  (Gemini)    │    │  (Claude)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Anthropic    │    │  Google AI   │    │ Anthropic    │      │
│  │    API       │    │    API       │    │    API       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
│                      ┌──────────────────────┐                   │
│                      │     The Council      │                   │
│                      │    (4 Judges)        │                   │
│                      │                      │                   │
│                      │  ┌────────────────┐  │                   │
│                      │  │ Claude │ Gemini│  │                   │
│                      │  │ (Anthr)│(Google)│  │                   │
│                      │  └────────────────┘  │                   │
│                      │  ┌────────────────┐  │                   │
│                      │  │ Grok 3 │ GPT-5 │  │                   │
│                      │  │(GitHub)│(GitHub)│  │                   │
│                      │  └────────────────┘  │                   │
│                      └──────────────────────┘                   │
│                                     │                           │
│                                     ▼                           │
│                              ┌──────────────┐                   │
│                              │ Git Push     │                   │
│                              └──────────────┘                   │
└─────────────────────────────────────────────────────────────────┘

API Routing Details:
┌──────────────────────────────────────────────────────────────────┐
│                      GitHubModelsRouter                          │
│                  (nexusprime/core/llm_router.py)                 │
└──────────────────────────────────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
   ┌────────────────┐  ┌────────────────┐  ┌───────────────┐
   │  Anthropic API │  │  Google AI API │  │  GitHub Models│
   │                │  │                │  │      API      │
   │ Claude Sonnet 4│  │  Gemini 3 Pro  │  │  Grok 3       │
   │                │  │                │  │  GPT-5        │
   └────────────────┘  └────────────────┘  └───────────────┘
         │                     │                   │
         ▼                     ▼                   ▼
   ANTHROPIC_API_KEY    GOOGLE_API_KEY      GITHUB_TOKEN
```

## LLM Router

The `GitHubModelsRouter` class (`nexusprime/core/llm_router.py`) manages all LLM interactions across three separate APIs.

### Key Features

- **Multi-API Support**: Routes to Anthropic API, Google AI API, and GitHub Models API
- **Model Selection**: Automatically routes requests to the appropriate model based on agent name
- **Configuration Management**: Each agent has customized temperature and token limits
- **Token Tracking**: Returns detailed token usage for cost monitoring
- **Error Handling**: Graceful fallbacks and detailed error logging
- **Thread-Safe**: Singleton pattern ensures safe concurrent access

### API Routing Logic

The router automatically selects the correct API based on the model:

1. **Anthropic API** (`https://api.anthropic.com/v1/messages`)
   - Used for: Claude Sonnet 4
   - Authentication: `ANTHROPIC_API_KEY`
   - Headers: `x-api-key`, `anthropic-version`

2. **Google AI API** (via `google-generativeai` SDK)
   - Used for: Gemini 3 Pro
   - Authentication: `GOOGLE_API_KEY`
   - Configuration: Direct SDK integration

3. **GitHub Models API** (`https://models.github.ai/inference/chat/completions`)
   - Used for: Grok 3, GPT-5
   - Authentication: `GITHUB_TOKEN`
   - Headers: Bearer token authentication

### Code Structure

```python
from nexusprime.core.llm_router import get_llm_router

# Get router instance (singleton)
router = get_llm_router()

# Make a call - router automatically selects the correct API
response, token_usage = router.call(
    prompt="Your prompt here",
    agent_name="product_owner",  # Routes to Anthropic API
    system_prompt="You are a requirements analyst.",
    custom_config=None  # Optional override
)
```

## Model Configuration

### Default Agent → Model Mapping

| Agent Name | Model | API | Temperature | Max Tokens | Purpose |
|------------|-------|-----|-------------|------------|---------|
| `product_owner` | Claude Sonnet 4 | Anthropic | 0.3 | 8192 | Requirement refinement & spec generation |
| `tech_lead` | Gemini 3 Pro | Google AI | 0.2 | 8192 | Environment setup & architecture |
| `dev_squad` | Claude Sonnet 4 | Anthropic | 0.1 | 8192 | Precise code generation |
| `council_claude` | Claude Sonnet 4 | Anthropic | 0.4 | 8192 | Quality review & arbitration |
| `council_gemini` | Gemini 3 Pro | Google AI | 0.4 | 8192 | Technical & security review |
| `council_grok` | Grok 3 | GitHub Models | 0.4 | 8192 | Creative review & critical thinking |
| `council_gpt` | GPT-5 | GitHub Models | 0.4 | 8192 | Advanced reasoning & validation |

### Temperature Guidelines

- **0.1 - 0.2**: Highly deterministic, ideal for code generation
- **0.3 - 0.4**: Balanced creativity and consistency
- **0.5 - 0.7**: More creative responses (not used in NexusPrime currently)

### Modifying Configuration

To change a model or configuration, edit `nexusprime/core/llm_router.py`:

```python
AGENT_MODEL_MAP: Dict[str, LLMConfig] = {
    "product_owner": LLMConfig(
        provider=LLMProvider.CLAUDE_SONNET_4,
        temperature=0.3,
        max_tokens=8192  # Increase if needed
    ),
    # ... other agents
}
```

## Adding New Providers

### Step 1: Add Provider to Enum

Edit `nexusprime/core/llm_router.py`:

```python
class LLMProvider(str, Enum):
    """Supported LLM providers via multiple APIs."""
    
    # Anthropic API
    CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"
    
    # Google AI API
    GEMINI_3_PRO = "gemini-3-pro-preview"
    
    # GitHub Models API
    GROK_3 = "azureml-xai/grok-3"
    GPT_5 = "azure-openai/gpt-5"
    
    # Add your new model here
    NEW_MODEL = "new-model-identifier"
```

### Step 2: Add to Agent Mapping

```python
AGENT_MODEL_MAP: Dict[str, LLMConfig] = {
    # ... existing mappings
    "new_agent": LLMConfig(
        provider=LLMProvider.NEW_MODEL,
        temperature=0.3
    ),
}
```

### Step 3: Implement API Call Method (if needed)

If your model uses a new API not yet supported, add a new method like `_call_new_api()` following the pattern of existing methods (`_call_anthropic`, `_call_google`, `_call_github_models`).

### Step 4: Test the Integration

```python
from nexusprime.core.llm_router import get_llm_router

router = get_llm_router()
response, usage = router.call(
    prompt="Test prompt",
    agent_name="new_agent"
)
print(f"Response: {response}")
print(f"Tokens used: {usage}")
```

### Supported Models by API

**Anthropic API**:
- `claude-sonnet-4-20250514` (Claude Sonnet 4)

**Google AI API**:
- `gemini-3-pro-preview` (Gemini 3 Pro)
- Other Gemini models as they become available

**GitHub Models API**:
Check GitHub's documentation for the latest available models:
https://github.com/marketplace/models

Common models include:
- `azureml-xai/grok-3` (Grok 3)
- `azure-openai/gpt-5` (GPT-5)
- `azure-openai/gpt-4o` (GPT-4o)

## Usage Examples

### Basic Usage

```python
from nexusprime.core.llm_router import get_llm_router

router = get_llm_router()

# Product Owner call
spec, usage = router.call(
    prompt="Create a REST API for task management",
    agent_name="product_owner"
)

print(f"Specification:\n{spec}")
print(f"Tokens: {usage['total_token_count']}")
```

### Custom Configuration

```python
from nexusprime.core.llm_router import get_llm_router, LLMConfig, LLMProvider

router = get_llm_router()

# Override default config
custom_config = LLMConfig(
    provider=LLMProvider.GEMINI,
    temperature=0.5,
    max_tokens=8000
)

response, usage = router.call(
    prompt="Your prompt",
    agent_name="dev_squad",
    custom_config=custom_config
)
```

### Multi-LLM Council Pattern

```python
from nexusprime.core.llm_router import get_llm_router

router = get_llm_router()

# Get opinions from multiple models across different APIs
reviewers = ["council_claude", "council_gemini", "council_grok", "council_gpt"]
opinions = []

for reviewer in reviewers:
    response, _ = router.call(
        prompt="Review this code...",
        agent_name=reviewer
    )
    opinions.append(response)

# Arbitrate with Claude (via Anthropic API)
arbitration, usage = router.call(
    prompt=f"Synthesize these opinions: {opinions}",
    agent_name="council_claude"
)
```

## Cost Estimation

### Token Usage Tracking

NexusPrime tracks token usage for all LLM calls:

```python
{
    "prompt_tokens": 150,
    "completion_tokens": 800,
    "total_token_count": 950
}
```

### Estimated Costs per Model (by API)

**Note**: Costs vary by API provider. Check each provider's pricing page for current rates.

| Model | API | Input (per 1M tokens) | Output (per 1M tokens) | Typical Call Cost |
|-------|-----|----------------------|------------------------|-------------------|
| Claude Sonnet 4 | Anthropic | $3.00 | $15.00 | $0.012 - $0.030 |
| Gemini 3 Pro | Google AI | $1.25 | $5.00 | $0.005 - $0.015 |
| Grok 3 | GitHub Models | Variable | Variable | $0.008 - $0.025 |
| GPT-5 | GitHub Models | Variable | Variable | $0.010 - $0.025 |

**Pricing Resources**:
- Anthropic: https://www.anthropic.com/pricing
- Google AI: https://ai.google.dev/pricing
- GitHub Models: https://github.com/marketplace/models

### Cost Optimization Tips

1. **Use appropriate temperatures**: Lower temperatures (0.1-0.2) often produce shorter, more focused outputs
2. **Limit max_tokens**: Set reasonable limits based on expected output length
3. **Choose models wisely**: Use Gemini for architecture (cheaper), Claude for code (precise)
4. **Monitor usage**: Check `total_tokens` in dashboard regularly
5. **Batch requests**: Combine multiple small requests when possible
6. **Select optimal API**: Different APIs may have different pricing for similar capabilities

### Typical Project Costs

| Project Type | Tokens Used | Estimated Cost |
|-------------|-------------|----------------|
| Simple script (DEV) | 5,000 - 15,000 | $0.05 - $0.20 |
| REST API (DEV) | 15,000 - 50,000 | $0.20 - $0.75 |
| Full application (PROD) | 50,000 - 150,000 | $0.75 - $2.50 |

**Council Review adds**: ~2,500 - 6,000 tokens (4 LLM calls across 3 APIs)

## Best Practices

### 1. Model Selection Strategy

- **Claude Sonnet 4** (Anthropic API): Use for tasks requiring precision (code generation, specs)
- **Gemini 3 Pro** (Google AI API): Use for reasoning and architecture tasks
- **Grok 3** (GitHub Models API): Use for creative problem-solving and unique perspectives
- **GPT-5** (GitHub Models API): Use for advanced reasoning and validation

### 2. Temperature Tuning

- **Code Generation**: 0.1 - 0.2 (deterministic)
- **Architecture**: 0.2 - 0.3 (balanced)
- **Reviews**: 0.3 - 0.4 (slightly creative for diverse opinions)

### 3. Error Handling

Always wrap LLM calls in try-except blocks:

```python
try:
    response, usage = router.call(...)
except httpx.HTTPStatusError as e:
    logger.error(f"HTTP error: {e}")
    # Implement fallback logic
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle gracefully
```

### 4. Token Budgeting

Set reasonable limits per agent:

```python
# For short responses
LLMConfig(provider=..., max_tokens=1000)

# For detailed specs
LLMConfig(provider=..., max_tokens=4000)

# For complex code generation
LLMConfig(provider=..., max_tokens=8000)
```

### 5. Caching & Reuse

NexusPrime's memory system reduces redundant LLM calls:

```python
# Before calling LLM, check memory
memory_ctx = memory.retrieve_context(query)
if memory_ctx:
    # Use cached knowledge
    ...
```

## Troubleshooting

### Authentication Issues

**Error**: `ANTHROPIC_API_KEY not found` or `GOOGLE_API_KEY not found`

**Solution**: Ensure `.env` file contains all required keys:
```
GITHUB_TOKEN=ghp_your_token_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
GOOGLE_API_KEY=AIza_your_key_here
```

Verify each API key is valid:
- Anthropic: https://console.anthropic.com/
- Google AI: https://makersuite.google.com/app/apikey
- GitHub: https://github.com/settings/tokens

### Model Not Available

**Error**: `Model 'xyz' not found` or API returns 404

**Solution**: 
- Check that the model name matches the API's expected format
- Verify API key has access to the requested model
- Consult API provider documentation for available models:
  - Anthropic: https://docs.anthropic.com/
  - Google AI: https://ai.google.dev/models
  - GitHub Models: https://github.com/marketplace/models

### Rate Limiting

**Error**: `429 Too Many Requests`

**Solution**: 
- Each API has its own rate limits
- Implement exponential backoff or reduce concurrent requests
- Check rate limit documentation for each provider:
  - Anthropic: https://docs.anthropic.com/claude/reference/rate-limits
  - Google AI: https://ai.google.dev/docs/quota_limits
  - GitHub Models: https://docs.github.com/en/rest/overview/rate-limits

### High Token Usage

**Issue**: Dashboard shows unexpectedly high token counts

**Solution**: 
- Review `max_tokens` settings for each agent
- Check prompt sizes (large specs increase token usage)
- Monitor council reviews (each uses 4 separate LLM calls across 3 APIs)
- Consider using more cost-effective models for non-critical tasks

## Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Google AI Documentation](https://ai.google.dev/)
- [GitHub Models Documentation](https://github.com/marketplace/models)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [NexusPrime Main README](../README.md)
- [Walkthrough Guide](../WALKTHROUGH.md)

---

**Questions or Issues?**

Open an issue on the [NexusPrime GitHub repository](https://github.com/AxelVia/nexusprime).
