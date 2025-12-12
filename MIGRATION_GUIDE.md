# NexusPrime Architecture Migration Guide

## 📋 Overview

This document explains the comprehensive refactoring of NexusPrime from a monolithic structure to a modular, maintainable architecture.

## 🏗️ New Architecture

### Directory Structure

```
nexusprime/
├── nexusprime/               # Main package
│   ├── __init__.py          # Public API
│   ├── config.py            # Pydantic configuration
│   ├── agents/              # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract Agent base class
│   │   ├── product_owner.py
│   │   ├── tech_lead.py
│   │   ├── dev_squad.py
│   │   └── council.py
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── state.py         # State TypedDict
│   │   ├── llm.py           # LLM operations
│   │   └── graph.py         # LangGraph construction
│   ├── integrations/        # External integrations
│   │   ├── __init__.py
│   │   ├── memory.py        # Enhanced RAG memory
│   │   └── github_client.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── logging.py       # Structured logging
│       ├── security.py      # Security validation
│       ├── status.py        # Status management
│       └── tokens.py        # Token tracking
├── tests/                   # Test suite
│   ├── conftest.py
│   ├── test_memory.py
│   ├── test_config.py
│   ├── test_security.py
│   └── test_agents.py
├── dashboard.py             # Streamlit dashboard
├── run_factory.py           # Entry point
├── requirements.txt         # Dependencies
└── .gitignore              # Git exclusions
```

## 🔄 Migration from Old Code

### Before (Monolithic)

```python
from nexus_factory import build_nexus_factory
from nexus_memory import NexusMemory
```

### After (Modular)

```python
from nexusprime import build_nexus_factory
from nexusprime.integrations import NexusMemory
```

## 🔒 Security Improvements

### 1. Environment Variable Validation

```python
from nexusprime.utils.security import get_required_env

# This will raise EnvironmentError if not set
api_key = get_required_env("GOOGLE_API_KEY")
```

### 2. Code Validation

```python
from nexusprime.utils.security import validate_generated_code

code = "print('Hello')"
is_safe, warnings = validate_generated_code(code)
if not is_safe:
    for warning in warnings:
        print(f"Security issue: {warning}")
```

### 3. Structured Logging

```python
from nexusprime.utils.logging import get_logger

logger = get_logger(__name__)
logger.info("Operation started")
logger.error("Operation failed", exc_info=True)
```

## 🧠 Enhanced RAG System

### Features

1. **Embedding-based Search** (using sentence-transformers)
2. **Fallback to Keyword Search** (when embeddings unavailable)
3. **Lesson Management** (store, retrieve, delete, list)
4. **Timestamps and IDs** for all lessons

### Usage

```python
from nexusprime.integrations import NexusMemory

memory = NexusMemory()

# Store a lesson
lesson_id = memory.store_lesson(
    topic="API Development",
    context="Building REST API",
    outcome="Success",
    solution="Used FastAPI framework"
)

# Retrieve relevant lessons
context = memory.retrieve_context("How to build API?", top_k=3)
print(context)

# List all lessons
lessons = memory.list_lessons(limit=10)

# Delete a lesson
memory.delete_lesson(lesson_id)
```

## ⚙️ Configuration

### Using Pydantic Settings

```python
from nexusprime.config import get_settings

settings = get_settings()
print(f"Model: {settings.llm_model}")
print(f"Temperature: {settings.llm_temperature}")
```

### Environment Variables

Required:
- `GITHUB_TOKEN`: GitHub personal access token (for GitHub Models API)
- `ANTHROPIC_API_KEY`: Anthropic API key (for Claude Sonnet 4)
- `GOOGLE_API_KEY`: Google AI API key (for Gemini 3 Pro)

Optional (with defaults):
- `LLM_MODEL`: "gemini-3-pro-preview"
- `LLM_TEMPERATURE`: 0.2
- `MAX_FEEDBACK_LOOPS`: 5
- `DEV_QUALITY_THRESHOLD`: 75
- `PROD_QUALITY_THRESHOLD`: 95

## 🌐 Multi-API Architecture Migration

### Overview

NexusPrime now uses **three separate APIs** instead of a single unified API:

1. **Anthropic API** - For Claude Sonnet 4 models
2. **Google AI API** - For Gemini 3 Pro models  
3. **GitHub Models API** - For Grok 3 and GPT-5 models

### Migration Steps

#### 1. Update Environment Variables

**Before**:
```env
GOOGLE_API_KEY=your_google_key
GITHUB_TOKEN=your_github_token
```

**After**:
```env
GITHUB_TOKEN=your_github_token
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

#### 2. Get New API Keys

- **Anthropic API Key**: Get from [console.anthropic.com](https://console.anthropic.com/)
- **Google API Key**: Get from [makersuite.google.com](https://makersuite.google.com/app/apikey)
- **GitHub Token**: Get from [github.com/settings/tokens](https://github.com/settings/tokens)

#### 3. Update Dependencies (if needed)

The Multi-API router automatically selects the correct API based on the model. No code changes required in your applications.

```python
# This still works - router automatically uses the right API
from nexusprime.core.llm_router import get_llm_router

router = get_llm_router()
response, usage = router.call(
    prompt="Your prompt",
    agent_name="product_owner"  # Routes to Anthropic API
)
```

#### 4. Model Mapping Changes

| Agent | Old Model | New Model | New API |
|-------|-----------|-----------|---------|
| Product Owner | Claude Sonnet 4 | Claude Sonnet 4 | Anthropic |
| Tech Lead | Gemini 2.5 Pro | Gemini 3 Pro | Google AI |
| Dev Squad | Claude Sonnet 4 | Claude Sonnet 4 | Anthropic |
| Council (Claude) | Claude Sonnet 4 | Claude Sonnet 4 | Anthropic |
| Council (Gemini) | Gemini 2.5 Pro | Gemini 3 Pro | Google AI |
| Council (Grok) | Grok 3 | Grok 3 | GitHub Models |
| Council (GPT) | *(new)* | GPT-5 | GitHub Models |

#### 5. Benefits of Multi-API Architecture

- **Better Performance**: Direct API access without intermediate layers
- **More Control**: Fine-tune API-specific parameters
- **Flexibility**: Easy to add new providers
- **Redundancy**: If one API has issues, others can still work
- **Cost Optimization**: Choose the most cost-effective API per task

### Backward Compatibility

The `GitHubModelsRouter` class maintains backward compatibility:
- Old agent names still work
- `CopilotLLMRouter` is an alias for `GitHubModelsRouter`
- Existing code continues to function without changes

## 📊 Dashboard Improvements

### Changes

1. **Removed blocking `while True` loop**
2. **Added auto-refresh** with `st_autorefresh`
3. **Better error handling** for missing files
4. **User-friendly error messages**

### Running the Dashboard

```bash
streamlit run dashboard.py
```

## 🧪 Testing

### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_memory.py -v

# Run with coverage
python -m pytest tests/ --cov=nexusprime --cov-report=html
```

### Test Coverage

- **24 tests** covering:
  - Security utilities (10 tests)
  - Memory system (9 tests)
  - Configuration (4 tests)
  - Agents (1 test)

## 🚀 Usage Examples

### Basic Factory Usage

```python
from nexusprime import build_nexus_factory
from langchain_core.messages import HumanMessage

# Build the factory
app = build_nexus_factory()

# Create initial state
initial_state = {
    "messages": [HumanMessage(content="Build a calculator app")],
    "feedback_loop_count": 0
}

# Run the factory
final_state = app.invoke(initial_state)

# Check results
print(f"Status: {final_state['current_status']}")
print(f"Quality: {final_state['quality_score']}")
```

### Custom Agent Implementation

```python
from nexusprime.agents.base import Agent
from nexusprime.core.state import NexusFactoryState

class CustomAgent(Agent):
    def execute(self, state: NexusFactoryState) -> dict:
        self.log_execution("Starting custom logic")
        
        # Your custom logic here
        
        return {
            "current_status": "Custom Agent Complete"
        }
```

## 🔧 Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```
   Error: Required environment variable 'GOOGLE_API_KEY' is not set
   ```
   Solution: Create a `.env` file with required variables

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'nexusprime'
   ```
   Solution: Install dependencies: `pip install -r requirements.txt`

3. **Dashboard Not Refreshing**
   - Check that `streamlit-autorefresh` is installed
   - Verify browser doesn't block auto-refresh

## 📚 API Reference

### Core Functions

- `build_nexus_factory()`: Compile the LangGraph factory
- `get_settings()`: Get configuration settings
- `get_logger(name)`: Get configured logger
- `get_required_env(key)`: Get required env variable

### Agents

- `ProductOwnerAgent`: Refines requirements into specifications
- `TechLeadAgent`: Sets up environment and retrieves context
- `DevSquadAgent`: Generates code based on specifications
- `CouncilAgent`: Reviews quality and archives lessons

## 🎯 Best Practices

1. **Always validate environment variables** at startup
2. **Use structured logging** instead of print statements
3. **Validate generated code** before execution
4. **Write tests** for new functionality
5. **Use type hints** for better code documentation
6. **Handle errors specifically** - avoid generic exceptions

## 📝 Migration Checklist

- [ ] Update imports to use `nexusprime` package
- [ ] Create `.env` file with all 3 required API keys (GITHUB_TOKEN, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Update any custom code to use new APIs (if applicable)
- [ ] Run tests to verify compatibility
- [ ] Update deployment scripts if necessary
- [ ] Verify all 3 APIs are accessible from your environment

## 🆘 Support

For issues or questions:
1. Check this migration guide
2. Review test files for usage examples
3. Check logs in `nexus.log`
4. Open an issue on GitHub

## 📄 License

Same as NexusPrime project license.
