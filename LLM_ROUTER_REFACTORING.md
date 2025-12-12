# LLM Router Multi-API Refactoring

## Overview

The LLM Router has been refactored to support multiple AI APIs instead of relying solely on GitHub Models API. This enables the use of:

- **Anthropic API** for Claude Sonnet 4
- **Google AI API** for Gemini 3 Pro
- **GitHub Models API** for Grok 3 and GPT-5

## Architecture

### Agent to Model Mapping

| Agent | Model | API | Configuration |
|-------|-------|-----|---------------|
| `product_owner` | Claude Sonnet 4 | Anthropic API | temp: 0.3 |
| `dev_squad` | Claude Sonnet 4 | Anthropic API | temp: 0.1 |
| `council_claude` | Claude Sonnet 4 | Anthropic API | temp: 0.4 |
| `tech_lead` | Gemini 3 Pro | Google AI API | temp: 0.2 |
| `council_gemini` | Gemini 3 Pro | Google AI API | temp: 0.4 |
| `council_grok` | Grok 3 | GitHub Models API | temp: 0.4 |
| `council_gpt` | GPT-5 | GitHub Models API | temp: 0.4 |

### API Details

#### 1. Anthropic API (Claude Sonnet 4)

- **Endpoint**: `https://api.anthropic.com/v1/messages`
- **Authentication**: `x-api-key: ANTHROPIC_API_KEY`
- **Required Header**: `anthropic-version: 2023-06-01`
- **Model**: `claude-sonnet-4-20250514`

#### 2. Google AI API (Gemini 3 Pro)

- **SDK**: `google-generativeai`
- **Authentication**: `GOOGLE_API_KEY`
- **Model**: `gemini-3-pro` (with fallback to `gemini-2.5-pro`)

#### 3. GitHub Models API (Grok 3, GPT-5)

- **Endpoint**: `https://models.github.ai/inference/chat/completions`
- **Authentication**: `Bearer GITHUB_TOKEN`
- **Models**: 
  - `azureml-xai/grok-3` (Grok 3)
  - `azure-openai/gpt-5` (GPT-5)

## Environment Variables

The following environment variables are required:

```bash
# Required for all operations
GITHUB_TOKEN=xxx              # For GitHub Models API (Grok, GPT-5)

# Required only when using Claude models
ANTHROPIC_API_KEY=xxx         # For Anthropic API (Claude Sonnet 4)

# Required only when using Gemini models
GOOGLE_API_KEY=xxx            # For Google AI API (Gemini 3 Pro)
```

## Implementation Details

### New Methods

1. **`_call_anthropic()`**: Handles calls to Anthropic API
   - Converts system prompt to Anthropic format
   - Handles token counting (input_tokens + output_tokens)
   - Proper error handling with detailed logging

2. **`_call_google()`**: Handles calls to Google AI API
   - Uses `google-generativeai` SDK
   - Lazy initialization of the SDK
   - Fallback from `gemini-3-pro` to `gemini-2.5-pro` if needed
   - Handles token counting when available

3. **`_call_github_models()`**: Handles calls to GitHub Models API
   - Original functionality for Grok and GPT models
   - Maintains backward compatibility

### Routing Logic

The `call()` method now routes to the appropriate API based on the model:

```python
if model == "claude-sonnet-4-20250514":
    return self._call_anthropic(...)
elif model == "gemini-3-pro":
    return self._call_google(...)
elif model in ["azureml-xai/grok-3", "azure-openai/gpt-5"]:
    return self._call_github_models(...)
```

## Changes Made

### Files Modified

1. **`nexusprime/core/llm_router.py`**
   - Updated `LLMProvider` enum with new model names
   - Updated `AGENT_MODEL_MAP` with new agent mappings
   - Added three API-specific methods
   - Updated `call()` method with routing logic
   - Added proper error handling for missing API keys

2. **`nexusprime/agents/council.py`**
   - Changed `council_gpt4` to `council_gpt` (GPT-5)
   - Updated reviewer name from "GPT-4" to "GPT-5"

3. **`requirements.txt`**
   - Added `anthropic>=0.25.0`
   - Added `google-generativeai>=0.3.0`

4. **`.env.test`**
   - Added `ANTHROPIC_API_KEY=test_anthropic_key_789`

5. **`tests/test_llm_router.py`**
   - Complete rewrite to test new multi-API architecture
   - Added tests for Anthropic API calls
   - Added tests for Google AI API calls
   - Added tests for error handling when API keys are missing
   - Updated all model name references

## Backward Compatibility

- The `GitHubModelsRouter` class name remains unchanged
- The `call()` method signature is unchanged
- The `get_llm_router()` singleton function works the same way
- `CopilotLLMRouter` alias still exists for backward compatibility
- All existing code using the router should continue to work

## Error Handling

Each API call method includes:

- Specific error messages indicating which API failed
- Detailed logging of errors
- Proper exception handling and re-raising
- Validation of required API keys before making calls

## Testing

Run the test suite:

```bash
# Run all LLM router tests
python -m pytest tests/test_llm_router.py -v

# Run verification script
python verify_llm_routing.py
```

All tests should pass with proper mocking of API calls.

## Usage Example

```python
from nexusprime.core.llm_router import get_llm_router

# Get the router instance
router = get_llm_router()

# Call with an agent name (automatically routes to correct API)
response, usage = router.call(
    prompt="Analyze this code...",
    agent_name="product_owner",  # Uses Claude via Anthropic API
    system_prompt="You are a product owner."
)

# Or specify a different agent
response, usage = router.call(
    prompt="Design the architecture...",
    agent_name="tech_lead",  # Uses Gemini via Google AI API
)
```

## Migration Notes

For users of the previous version:

1. Install new dependencies: `pip install anthropic google-generativeai`
2. Set environment variables: `ANTHROPIC_API_KEY` and `GOOGLE_API_KEY`
3. Update any agent references from `council_gpt4` to `council_gpt`
4. No code changes needed for existing calls to `router.call()`

## Future Improvements

Potential enhancements:

- Add retry logic for API failures
- Implement rate limiting per API
- Add caching layer for responses
- Support streaming responses
- Add more detailed token usage tracking
- Support for model fine-tuning/customization
