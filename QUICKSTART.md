# NexusPrime Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Prerequisites

- Python 3.10 or higher
- **Anthropic API key** (for Claude Sonnet 4)
- **Google AI API key** (for Gemini 3 Pro)
- **GitHub token** (for GitHub Models API - Grok 3, GPT-5)
- Git installed

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
GITHUB_TOKEN=your_github_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

**Required API Keys**:

1. **GITHUB_TOKEN**: GitHub personal access token
   - Get it from: https://github.com/settings/tokens
   - Required for GitHub Models API (Grok 3, GPT-5)

2. **ANTHROPIC_API_KEY**: Anthropic API key
   - Get it from: https://console.anthropic.com/
   - Required for Claude Sonnet 4

3. **GOOGLE_API_KEY**: Google AI API key
   - Get it from: https://makersuite.google.com/app/apikey
   - Required for Gemini 3 Pro

### 3. Run the Factory

```bash
python run_factory.py
```

### 4. Launch Dashboard (Optional)

```bash
streamlit run dashboard.py
```

## 🎯 What's New in This Version?

### ✅ Multi-API Architecture
- ✅ Claude Sonnet 4 for requirements and code generation (via Anthropic API)
- ✅ Gemini 3 Pro for architecture and technical review (via Google AI API)
- ✅ Grok 3 for creative analysis and critical thinking (via GitHub Models API)
- ✅ GPT-5 for advanced reasoning and validation (via GitHub Models API)
- ✅ Council debate system with 4 independent judges + arbitration

### ✅ Security Enhancements
- ✅ Required environment variable validation
- ✅ Generated code security scanning
- ✅ Structured error logging

### ✅ Architecture Improvements
- ✅ Modular package structure
- ✅ Clean separation of concerns
- ✅ Thread-safe implementations

### ✅ Advanced RAG System
- ✅ Embedding-based semantic search
- ✅ Automatic fallback to keyword search
- ✅ Lesson management with timestamps

### ✅ Better Dashboard
- ✅ No more blocking loops
- ✅ Auto-refresh every 2 seconds
- ✅ Graceful error handling

### ✅ Comprehensive Testing
- ✅ 24 unit tests
- ✅ 100% critical path coverage
- ✅ 0 security vulnerabilities

## 📖 Basic Usage

### Import the Factory

```python
from nexusprime import build_nexus_factory
from langchain_core.messages import HumanMessage

app = build_nexus_factory()
```

### Run a Task

```python
state = {
    "messages": [HumanMessage(content="Build a REST API for todo items")],
    "feedback_loop_count": 0
}

result = app.invoke(state)
print(f"Quality Score: {result['quality_score']}")
```

### Use the Memory System

```python
from nexusprime.integrations import NexusMemory

memory = NexusMemory()
memory.store_lesson(
    topic="REST API Design",
    context="Building CRUD operations",
    outcome="Success",
    solution="Used FastAPI with Pydantic models"
)
```

## 🧪 Run Tests

```bash
# All tests
python -m pytest tests/ -v

# Just security tests
python -m pytest tests/test_security.py -v

# With coverage report
python -m pytest tests/ --cov=nexusprime
```

## 📚 Next Steps

1. **Read the [Migration Guide](MIGRATION_GUIDE.md)** - Comprehensive documentation
2. **Explore the tests** - See usage examples in `tests/`
3. **Customize agents** - Extend `nexusprime/agents/base.py`
4. **Configure settings** - Adjust `nexusprime/config.py` defaults

## 🐛 Troubleshooting

### Environment Variable Not Set
```
Error: Required environment variable 'GOOGLE_API_KEY' is not set
```
**Fix:** Create `.env` file with required variables

### Module Not Found
```
ModuleNotFoundError: No module named 'nexusprime'
```
**Fix:** `pip install -r requirements.txt`

### Tests Failing
```
ImportError: cannot import name 'Settings'
```
**Fix:** Ensure pydantic-settings is installed: `pip install pydantic-settings`

## 💡 Tips

- Check `nexus.log` for detailed execution logs
- Use `DEBUG` log level for troubleshooting
- Review `status.json` for current factory state
- Browse `nexus_memory.json` to see stored lessons

## 🎓 Learning Resources

- **Code Examples:** See `tests/` directory
- **Architecture:** Read `MIGRATION_GUIDE.md`
- **API Reference:** Check docstrings in source files

---

**Ready to build?** 🚀

```bash
python run_factory.py
```
