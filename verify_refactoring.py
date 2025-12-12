"""Comprehensive verification of the refactoring."""
import os
import sys

# Set test environment variables
os.environ['GOOGLE_API_KEY'] = 'test_key'
os.environ['GITHUB_TOKEN'] = 'test_token'

def verify_imports():
    """Verify all imports work correctly."""
    print("✓ Verifying imports...")
    try:
        from nexusprime import build_nexus_factory, get_settings, NexusMemory
        from nexusprime.agents import ProductOwnerAgent, TechLeadAgent
        from nexusprime.utils import get_logger, get_required_env, validate_generated_code
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def verify_config():
    """Verify configuration system."""
    print("✓ Verifying configuration...")
    try:
        from nexusprime import get_settings
        settings = get_settings()
        assert settings.llm_model == "gemini-2.5-pro"
        assert settings.llm_temperature == 0.2
        assert settings.max_feedback_loops == 5
        print("  ✅ Configuration working correctly")
        return True
    except Exception as e:
        print(f"  ❌ Config failed: {e}")
        return False

def verify_security():
    """Verify security utilities."""
    print("✓ Verifying security utilities...")
    try:
        from nexusprime.utils.security import validate_generated_code, get_required_env
        
        # Test code validation
        safe_code = "def add(a, b): return a + b"
        is_safe, warnings = validate_generated_code(safe_code)
        assert is_safe, "Safe code should pass validation"
        
        unsafe_code = "import os; os.system('ls')"
        is_safe, warnings = validate_generated_code(unsafe_code)
        assert not is_safe, "Unsafe code should fail validation"
        assert len(warnings) > 0, "Should have warnings"
        
        # Test env validation
        api_key = get_required_env("GOOGLE_API_KEY")
        assert api_key == "test_key"
        
        print("  ✅ Security utilities working correctly")
        return True
    except Exception as e:
        print(f"  ❌ Security failed: {e}")
        return False

def verify_memory():
    """Verify memory system."""
    print("✓ Verifying memory system...")
    try:
        from nexusprime.integrations import NexusMemory
        import tempfile
        import os
        
        # Use temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            memory = NexusMemory(memory_path=temp_path, use_embeddings=False)
            
            # Store lesson
            lesson_id = memory.store_lesson("Test", "Context", "Success", "Solution")
            assert lesson_id is not None
            
            # Retrieve
            context = memory.retrieve_context("Test", top_k=1)
            assert "Test" in context
            
            # Delete
            deleted = memory.delete_lesson(lesson_id)
            assert deleted
            
            print("  ✅ Memory system working correctly")
            return True
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        print(f"  ❌ Memory failed: {e}")
        return False

def verify_factory():
    """Verify factory can be built."""
    print("✓ Verifying factory build...")
    try:
        from nexusprime import build_nexus_factory
        app = build_nexus_factory()
        assert app is not None
        print("  ✅ Factory builds successfully")
        return True
    except Exception as e:
        print(f"  ❌ Factory build failed: {e}")
        return False

def main():
    """Run all verifications."""
    print("\n" + "="*60)
    print("  NEXUSPRIME REFACTORING VERIFICATION")
    print("="*60 + "\n")
    
    results = [
        verify_imports(),
        verify_config(),
        verify_security(),
        verify_memory(),
        verify_factory(),
    ]
    
    print("\n" + "="*60)
    if all(results):
        print("  ✅ ALL VERIFICATIONS PASSED!")
        print("="*60 + "\n")
        return 0
    else:
        print("  ❌ SOME VERIFICATIONS FAILED")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
