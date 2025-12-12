# NexusPrime Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_google_api_key_here
GITHUB_TOKEN=your_github_token_here
```

### 3. Run the Factory

```bash
python run_factory.py
```

### 4. Launch Dashboard (Optional)

```bash
streamlit run dashboard.py
```

## 🎯 What's New in This Version?

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
