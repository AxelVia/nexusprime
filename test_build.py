"""Test that the factory can be built."""
import os
os.environ['GOOGLE_API_KEY'] = 'test_key'
os.environ['GITHUB_TOKEN'] = 'test_token'

from nexusprime import build_nexus_factory, get_settings

# Test settings
print("Testing settings...")
settings = get_settings()
print(f"  ✓ LLM Model: {settings.llm_model}")
print(f"  ✓ Temperature: {settings.llm_temperature}")
print(f"  ✓ Max Loops: {settings.max_feedback_loops}")

# Test building factory
print("\nBuilding factory...")
app = build_nexus_factory()
print("  ✓ Factory compiled successfully")

print("\n✅ All backward compatibility checks passed!")
