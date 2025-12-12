# 🤖 Multi-LLM Architecture Documentation

This document provides comprehensive information about NexusPrime's Multi-LLM architecture, powered by the GitHub Copilot API.

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

NexusPrime leverages multiple large language models (LLMs) to harness their unique strengths:

- **Claude Sonnet 4** (Anthropic): Excels at precise code generation and requirement analysis
- **Gemini 2.5 Pro** (Google DeepMind): Strong technical reasoning and architecture planning
- **Grok 3** (xAI): Creative thinking and critical analysis

All models are accessed through the **GitHub Copilot Chat Completions API**, which provides:
- Unified interface for multiple providers
- Consistent authentication via GitHub token
- Built-in rate limiting and error handling
- Enterprise-grade reliability

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         NexusPrime Factory                      │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Product    │    │  Tech Lead   │    │  Dev Squad   │    │
│  │    Owner     │───▶│              │───▶│              │    │
│  │ (Claude)     │    │  (Gemini)    │    │  (Claude)    │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                                                   │             │
│                                                   ▼             │
│                                          ┌──────────────┐       │
│                                          │  The Council │       │
│                                          │              │       │
│                                          │  ┌────────┐  │       │
│                                          │  │  Grok  │  │       │
│                                          │  └────────┘  │       │
│                                          │  ┌────────┐  │       │
│                                          │  │ Gemini │  │       │
│                                          │  └────────┘  │       │
│                                          │  ┌────────┐  │       │
│                                          │  │ Claude │  │       │
│                                          │  └────────┘  │       │
│                                          │      │       │       │
│                                          │      ▼       │       │
│                                          │ Arbitration  │       │
│                                          │  (Claude)    │       │
│                                          └──────────────┘       │
│                                                   │             │
│                                                   ▼             │
│                                            ┌──────────────┐     │
│                                            │ Git Push     │     │
│                                            └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   GitHub Copilot API          │
                    │   (Chat Completions)          │
                    └───────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
        ┌─────────────┐     ┌─────────────┐    ┌─────────────┐
        │   Claude    │     │   Gemini    │    │    Grok     │
        │  Sonnet 4   │     │  2.5 Pro    │    │      3      │
        └─────────────┘     └─────────────┘    └─────────────┘
```

## LLM Router

The `CopilotLLMRouter` class (`nexusprime/core/llm_router.py`) manages all LLM interactions.

### Key Features

- **Model Selection**: Automatically routes requests to the appropriate model based on agent name
- **Configuration Management**: Each agent has customized temperature and token limits
- **Token Tracking**: Returns detailed token usage for cost monitoring
- **Error Handling**: Graceful fallbacks and detailed error logging
- **Thread-Safe**: Singleton pattern ensures safe concurrent access

### Code Structure

```python
from nexusprime.core.llm_router import get_llm_router

# Get router instance (singleton)
router = get_llm_router()

# Make a call
response, token_usage = router.call(
    prompt="Your prompt here",
    agent_name="product_owner",
    system_prompt="You are a requirements analyst.",
    custom_config=None  # Optional override
)
```

## Model Configuration

### Default Agent → Model Mapping

| Agent Name | Model | Temperature | Max Tokens | Purpose |
|------------|-------|-------------|------------|---------|
| `product_owner` | Claude Sonnet 4 | 0.3 | 4000 | Requirement refinement & spec generation |
| `tech_lead` | Gemini 2.5 Pro | 0.2 | 4000 | Environment setup & architecture |
| `dev_squad` | Claude Sonnet 4 | 0.1 | 4000 | Precise code generation |
| `council_grok` | Grok 3 | 0.4 | 4000 | Creative review & critical thinking |
| `council_gemini` | Gemini 2.5 Pro | 0.4 | 4000 | Technical & security review |
| `council_claude` | Claude Sonnet 4 | 0.3 | 4000 | Quality review & arbitration |

### Temperature Guidelines

- **0.1 - 0.2**: Highly deterministic, ideal for code generation
- **0.3 - 0.4**: Balanced creativity and consistency
- **0.5 - 0.7**: More creative responses (not used in NexusPrime currently)

### Modifying Configuration

To change a model or configuration, edit `nexusprime/core/llm_router.py`:

```python
AGENT_MODEL_MAPPING: Dict[str, LLMConfig] = {
    "product_owner": LLMConfig(
        provider=LLMProvider.CLAUDE,
        temperature=0.3,
        max_tokens=4000  # Increase if needed
    ),
    # ... other agents
}
```

## Adding New Providers

### Step 1: Add Provider to Enum

Edit `nexusprime/core/llm_router.py`:

```python
class LLMProvider(str, Enum):
    """Supported LLM providers via GitHub Copilot API."""
    
    CLAUDE = "claude-sonnet-4"
    GEMINI = "gemini-2.5-pro"
    GPT4 = "gpt-4o"
    GROK = "grok-3"
    NEW_MODEL = "new-model-name"  # Add here
```

### Step 2: Add to Agent Mapping

```python
AGENT_MODEL_MAPPING: Dict[str, LLMConfig] = {
    # ... existing mappings
    "new_agent": LLMConfig(
        provider=LLMProvider.NEW_MODEL,
        temperature=0.3
    ),
}
```

### Step 3: Test the Integration

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

### Supported Models (GitHub Copilot API)

Check GitHub's documentation for the latest available models:
https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-code-review

Common models include:
- `claude-sonnet-4` (Anthropic Claude)
- `gemini-2.5-pro` (Google Gemini)
- `gpt-4o` (OpenAI GPT-4)
- `grok-3` (xAI Grok)

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

# Get opinions from multiple models
reviewers = ["council_grok", "council_gemini", "council_claude"]
opinions = []

for reviewer in reviewers:
    response, _ = router.call(
        prompt="Review this code...",
        agent_name=reviewer
    )
    opinions.append(response)

# Arbitrate with Claude
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

### Estimated Costs per Model (via GitHub Copilot)

**Note**: Costs are approximate and based on GitHub Copilot pricing. Actual costs may vary.

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Typical Call Cost |
|-------|----------------------|------------------------|-------------------|
| Claude Sonnet 4 | $3.00 | $15.00 | $0.012 - $0.030 |
| Gemini 2.5 Pro | $1.25 | $5.00 | $0.005 - $0.015 |
| Grok 3 | $2.00 | $10.00 | $0.008 - $0.025 |
| GPT-4o | $2.50 | $10.00 | $0.010 - $0.025 |

### Cost Optimization Tips

1. **Use appropriate temperatures**: Lower temperatures (0.1-0.2) often produce shorter, more focused outputs
2. **Limit max_tokens**: Set reasonable limits based on expected output length
3. **Choose models wisely**: Use Gemini for architecture (cheaper), Claude for code (precise)
4. **Monitor usage**: Check `total_tokens` in dashboard regularly
5. **Batch requests**: Combine multiple small requests when possible

### Typical Project Costs

| Project Type | Tokens Used | Estimated Cost |
|-------------|-------------|----------------|
| Simple script (DEV) | 5,000 - 15,000 | $0.05 - $0.20 |
| REST API (DEV) | 15,000 - 50,000 | $0.20 - $0.75 |
| Full application (PROD) | 50,000 - 150,000 | $0.75 - $2.50 |

**Council Review adds**: ~2,000 - 5,000 tokens (4 LLM calls)

## Best Practices

### 1. Model Selection Strategy

- **Claude Sonnet 4**: Use for tasks requiring precision (code generation, specs)
- **Gemini 2.5 Pro**: Use for reasoning and architecture tasks
- **Grok 3**: Use for creative problem-solving and unique perspectives

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

**Error**: `GITHUB_TOKEN not found`

**Solution**: Ensure `.env` file contains:
```
GITHUB_TOKEN=ghp_your_token_here
```

Verify token has Copilot access:
```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.githubcopilot.com/models
```

### Model Not Available

**Error**: `Model 'xyz' not found`

**Solution**: Check available models in GitHub Copilot documentation. Update `LLMProvider` enum with supported model names.

### Rate Limiting

**Error**: `429 Too Many Requests`

**Solution**: Implement exponential backoff or reduce concurrent requests. GitHub Copilot has rate limits per account.

### High Token Usage

**Issue**: Dashboard shows unexpectedly high token counts

**Solution**: 
- Review `max_tokens` settings
- Check prompt sizes (large specs increase token usage)
- Monitor council reviews (each uses 4 separate LLM calls)

## Additional Resources

- [GitHub Copilot API Documentation](https://docs.github.com/en/copilot)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [NexusPrime Main README](../README.md)
- [Walkthrough Guide](../WALKTHROUGH.md)

---

**Questions or Issues?**

Open an issue on the [NexusPrime GitHub repository](https://github.com/AxelVia/nexusprime).
