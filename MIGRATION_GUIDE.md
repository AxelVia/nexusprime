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
- `GOOGLE_API_KEY`: Google Gemini API key
- `GITHUB_TOKEN`: GitHub personal access token

Optional (with defaults):
- `LLM_MODEL`: "gemini-2.5-pro"
- `LLM_TEMPERATURE`: 0.2
- `MAX_FEEDBACK_LOOPS`: 5
- `DEV_QUALITY_THRESHOLD`: 75
- `PROD_QUALITY_THRESHOLD`: 95

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
- [ ] Create `.env` file with required variables
- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Update any custom code to use new APIs
- [ ] Run tests to verify compatibility
- [ ] Update deployment scripts if necessary

## 🆘 Support

For issues or questions:
1. Check this migration guide
2. Review test files for usage examples
3. Check logs in `nexus.log`
4. Open an issue on GitHub

## 📄 License

Same as NexusPrime project license.
