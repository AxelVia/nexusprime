"""
Multi-LLM Router supporting multiple APIs.
Routes to Anthropic API, Google AI API, and GitHub Models API based on model.
"""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Tuple, Optional

import httpx

from ..utils.logging import get_logger
from ..utils.security import get_required_env

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """Modèles disponibles via différentes APIs."""
    # Anthropic API
    CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"
    
    # Google AI API
    GEMINI_3_PRO = "gemini-3-pro-preview"
    
    # GitHub Models API
    GROK_3 = "azureml-xai/grok-3"
    GPT_5 = "azure-openai/gpt-5"


@dataclass
class LLMConfig:
    """Configuration pour un modèle spécifique."""
    provider: LLMProvider
    temperature: float = 0.2
    max_tokens: int = 8192


class GitHubModelsRouter:
    """
    Router Multi-LLM supportant plusieurs APIs.
    
    - Anthropic API pour Claude Sonnet 4
    - Google AI API pour Gemini 3 Pro
    - GitHub Models API pour Grok 3 et GPT-5
    """
    
    GITHUB_MODELS_URL = "https://models.github.ai/inference/chat/completions"
    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_VERSION = "2023-06-01"
    
    # Mapping Agent → Modèle optimal
    AGENT_MODEL_MAP: Dict[str, LLMConfig] = {
        # Claude Sonnet 4 (Anthropic API) pour l'analyse et le code
        "product_owner": LLMConfig(LLMProvider.CLAUDE_SONNET_4, temperature=0.3),
        "dev_squad": LLMConfig(LLMProvider.CLAUDE_SONNET_4, temperature=0.1),
        "council_claude": LLMConfig(LLMProvider.CLAUDE_SONNET_4, temperature=0.4),
        
        # Gemini 3 Pro (Google AI API) pour l'architecture
        "tech_lead": LLMConfig(LLMProvider.GEMINI_3_PRO, temperature=0.2),
        "council_gemini": LLMConfig(LLMProvider.GEMINI_3_PRO, temperature=0.4),
        
        # GitHub Models API pour le conseil
        "council_grok": LLMConfig(LLMProvider.GROK_3, temperature=0.4),
        "council_gpt": LLMConfig(LLMProvider.GPT_5, temperature=0.4),
    }
    
    # Alias pour compatibilité
    AGENT_MODEL_MAPPING = AGENT_MODEL_MAP
    
    def __init__(self):
        """Initialise le router avec les tokens nécessaires."""
        self.github_token = get_required_env("GITHUB_TOKEN")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self._client = httpx.Client(timeout=120.0)
        self._google_genai = None  # Lazy loading
        logger.info("🔌 Multi-API LLM Router initialisé")
    
    def _get_github_headers(self) -> Dict[str, str]:
        """Retourne les headers pour l'API GitHub Models."""
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _get_anthropic_headers(self) -> Dict[str, str]:
        """Retourne les headers pour l'API Anthropic."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required for Claude models")
        return {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": self.ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }
    
    def _init_google_genai(self):
        """Initialise le SDK Google Generative AI (lazy loading)."""
        if self._google_genai is None:
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini models")
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.google_api_key)
                self._google_genai = genai
                logger.info("✅ Google Generative AI SDK initialisé")
            except ImportError:
                raise ImportError("google-generativeai package is required. Install it with: pip install google-generativeai")
        return self._google_genai
    
    def _call_anthropic(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Appelle l'API Anthropic pour Claude.
        
        Args:
            prompt: Le prompt utilisateur
            system_prompt: Le prompt système
            model: Le modèle Claude à utiliser
            temperature: Température de génération
            max_tokens: Nombre maximum de tokens
            
        Returns:
            Tuple (réponse, usage_metadata)
        """
        logger.info(f"🤖 Appel Anthropic API avec modèle: {model}")
        
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = self._client.post(
                self.ANTHROPIC_API_URL,
                headers=self._get_anthropic_headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["content"][0]["text"]
            usage = data.get("usage", {})
            
            usage_formatted = {
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
                "total_token_count": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            }
            
            logger.info(
                f"✅ Réponse Anthropic ({usage_formatted['total_token_count']} tokens)"
            )
            
            return content, usage_formatted
            
        except httpx.HTTPStatusError as e:
            logger.error(
                f"❌ Erreur Anthropic API: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"❌ Erreur inattendue Anthropic: {e}")
            raise
    
    def _call_google(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Appelle l'API Google AI pour Gemini.
        
        Args:
            prompt: Le prompt utilisateur
            system_prompt: Le prompt système
            model: Le modèle Gemini à utiliser
            temperature: Température de génération
            max_tokens: Nombre maximum de tokens
            
        Returns:
            Tuple (réponse, usage_metadata)
        """
        logger.info(f"🤖 Appel Google AI API avec modèle: {model}")
        
        try:
            genai = self._init_google_genai()
            
            # Use the model directly (gemini-2.0-flash-exp is the latest available)
            model_instance = genai.GenerativeModel(model)
            
            # Combiner system_prompt et prompt
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = model_instance.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            content = response.text
            
            # Estimation des tokens (Google ne fournit pas toujours l'usage exact)
            usage_formatted = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_token_count": 0
            }
            
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                usage_formatted = {
                    "prompt_tokens": getattr(usage, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_token_count": getattr(usage, 'total_token_count', 0)
                }
            
            logger.info(
                f"✅ Réponse Google AI ({usage_formatted['total_token_count']} tokens)"
            )
            
            return content, usage_formatted
            
        except Exception as e:
            logger.error(f"❌ Erreur Google AI API: {e}")
            raise
    
    def _call_github_models(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Appelle l'API GitHub Models pour Grok et GPT.
        
        Args:
            prompt: Le prompt utilisateur
            system_prompt: Le prompt système
            model: Le modèle à utiliser
            temperature: Température de génération
            max_tokens: Nombre maximum de tokens
            
        Returns:
            Tuple (réponse, usage_metadata)
        """
        logger.info(f"🤖 Appel GitHub Models API avec modèle: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        try:
            response = self._client.post(
                self.GITHUB_MODELS_URL,
                headers=self._get_github_headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            })
            
            # Format usage for backward compatibility
            usage_formatted = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_token_count": usage.get("total_tokens", 0)
            }
            
            logger.info(
                f"✅ Réponse GitHub Models ({usage_formatted['total_token_count']} tokens)"
            )
            
            return content, usage_formatted
            
        except httpx.HTTPStatusError as e:
            logger.error(
                f"❌ Erreur GitHub Models API: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"❌ Erreur inattendue GitHub Models: {e}")
            raise
    
    def call(
        self,
        prompt: str,
        agent_name: str,
        system_prompt: str = "You are a helpful assistant.",
        custom_config: LLMConfig | None = None,
        override_model: Optional[LLMProvider] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Appelle le LLM approprié en routant vers la bonne API.
        
        Args:
            prompt: Le prompt utilisateur
            agent_name: Nom de l'agent (product_owner, dev_squad, etc.)
            system_prompt: Le prompt système
            custom_config: Configuration personnalisée (optionnel, legacy)
            override_model: Forcer un modèle spécifique (optionnel)
            
        Returns:
            Tuple (réponse, usage_metadata)
            
        Raises:
            ValueError: Si le modèle ou l'API key est invalide
            httpx.HTTPStatusError: Si l'API retourne une erreur
        """
        # Get configuration - custom_config has priority for backward compatibility
        if custom_config:
            config = custom_config
        elif override_model:
            base_config = self.AGENT_MODEL_MAP.get(
                agent_name, 
                LLMConfig(LLMProvider.CLAUDE_SONNET_4)
            )
            config = LLMConfig(override_model, base_config.temperature)
        else:
            config = self.AGENT_MODEL_MAP.get(
                agent_name, 
                LLMConfig(LLMProvider.CLAUDE_SONNET_4)
            )
        
        logger.info(f"🤖 Agent '{agent_name}' → Modèle: {config.provider.value}")
        
        model = config.provider.value
        
        # Router vers la bonne API selon le modèle
        if model == LLMProvider.CLAUDE_SONNET_4.value:
            # Anthropic API
            return self._call_anthropic(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        elif model == LLMProvider.GEMINI_3_PRO.value:
            # Google AI API
            return self._call_google(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        elif model in [LLMProvider.GROK_3.value, LLMProvider.GPT_5.value]:
            # GitHub Models API
            return self._call_github_models(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        else:
            # Fallback vers GitHub Models pour compatibilité
            logger.warning(f"Modèle inconnu '{model}', utilisation GitHub Models API")
            return self._call_github_models(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

    def list_available_models(self) -> list[str]:
        """Retourne la liste des modèles disponibles."""
        return [p.value for p in LLMProvider]
    
    def get_model_for_agent(self, agent_name: str) -> str:
        """Retourne le modèle configuré pour un agent."""
        config = self.AGENT_MODEL_MAP.get(agent_name)
        if config:
            return config.provider.value
        return LLMProvider.CLAUDE_SONNET_4.value


# Aliases pour rétrocompatibilité
CopilotLLMRouter = GitHubModelsRouter


# Singleton instance
_router_instance: GitHubModelsRouter | None = None
_router_lock = threading.Lock()


def get_llm_router() -> GitHubModelsRouter:
    """
    Retourne l'instance singleton du router (thread-safe).
    
    Returns:
        GitHubModelsRouter instance
    """
    global _router_instance
    if _router_instance is None:
        with _router_lock:
            # Double-check locking pattern
            if _router_instance is None:
                _router_instance = GitHubModelsRouter()
                logger.info("LLM router singleton created")
    return _router_instance
