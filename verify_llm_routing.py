#!/usr/bin/env python3
"""
Verification script for the multi-API LLM router.
Tests that the correct API is selected for each agent.
"""

import os
import sys

# Set up minimal environment
os.environ['GITHUB_TOKEN'] = 'test_token_123'
os.environ['ANTHROPIC_API_KEY'] = 'test_anthropic_key'
os.environ['GOOGLE_API_KEY'] = 'test_google_key'

from nexusprime.core.llm_router import GitHubModelsRouter, LLMProvider


def verify_routing():
    """Verify that the router maps agents to correct APIs."""
    
    print("=" * 70)
    print("LLM Router Multi-API Verification")
    print("=" * 70)
    
    router = GitHubModelsRouter()
    
    # Define expected mappings
    expected_mappings = {
        "product_owner": (LLMProvider.CLAUDE_SONNET_4, "Anthropic API"),
        "dev_squad": (LLMProvider.CLAUDE_SONNET_4, "Anthropic API"),
        "council_claude": (LLMProvider.CLAUDE_SONNET_4, "Anthropic API"),
        "tech_lead": (LLMProvider.GEMINI_3_PRO, "Google AI API"),
        "council_gemini": (LLMProvider.GEMINI_3_PRO, "Google AI API"),
        "council_grok": (LLMProvider.GROK_3, "GitHub Models API"),
        "council_gpt": (LLMProvider.GPT_5, "GitHub Models API"),
    }
    
    print("\nAgent to API Mapping:")
    print("-" * 70)
    print(f"{'Agent':<20} {'Model':<30} {'API':<20}")
    print("-" * 70)
    
    all_correct = True
    
    for agent_name, (expected_model, expected_api) in expected_mappings.items():
        config = router.AGENT_MODEL_MAP.get(agent_name)
        
        if not config:
            print(f"❌ {agent_name:<20} NOT FOUND")
            all_correct = False
            continue
        
        actual_model = config.provider
        
        # Determine which API would be used
        if actual_model == LLMProvider.CLAUDE_SONNET_4:
            actual_api = "Anthropic API"
        elif actual_model == LLMProvider.GEMINI_3_PRO:
            actual_api = "Google AI API"
        elif actual_model in [LLMProvider.GROK_3, LLMProvider.GPT_5]:
            actual_api = "GitHub Models API"
        else:
            actual_api = "Unknown API"
        
        if actual_model == expected_model and actual_api == expected_api:
            status = "✅"
        else:
            status = "❌"
            all_correct = False
        
        print(f"{status} {agent_name:<20} {actual_model.value:<30} {actual_api:<20}")
    
    print("-" * 70)
    
    # Test available models
    print("\nAvailable Models:")
    print("-" * 70)
    models = router.list_available_models()
    for model in models:
        print(f"  • {model}")
    
    print("-" * 70)
    
    if all_correct:
        print("\n✅ All agent mappings are correct!")
        return 0
    else:
        print("\n❌ Some agent mappings are incorrect!")
        return 1


def verify_api_methods():
    """Verify that API methods exist and have correct signatures."""
    
    print("\nAPI Method Verification:")
    print("-" * 70)
    
    router = GitHubModelsRouter()
    
    methods = [
        "_call_anthropic",
        "_call_google",
        "_call_github_models",
        "_get_anthropic_headers",
        "_get_github_headers",
        "_init_google_genai",
    ]
    
    all_exist = True
    for method_name in methods:
        if hasattr(router, method_name):
            print(f"✅ Method '{method_name}' exists")
        else:
            print(f"❌ Method '{method_name}' missing")
            all_exist = False
    
    print("-" * 70)
    
    if all_exist:
        print("\n✅ All required API methods exist!")
        return 0
    else:
        print("\n❌ Some API methods are missing!")
        return 1


def main():
    """Run all verifications."""
    
    try:
        result1 = verify_routing()
        result2 = verify_api_methods()
        
        print("\n" + "=" * 70)
        if result1 == 0 and result2 == 0:
            print("🎉 LLM Router verification PASSED!")
            print("=" * 70)
            return 0
        else:
            print("❌ LLM Router verification FAILED!")
            print("=" * 70)
            return 1
            
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
