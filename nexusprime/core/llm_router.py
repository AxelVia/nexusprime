"""
Multi-LLM Router via GitHub Models API.
Utilise GITHUB_TOKEN pour accéder à Claude, Gemini, GPT-4o.
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


class LLMProvider(Enum):
    """Modèles disponibles via GitHub Models API."""
    CLAUDE_SONNET = "anthropic/claude-sonnet-4"
    GEMINI_PRO = "google/gemini-2.5-pro" 
    GPT4O = "openai/gpt-4o"
    GPT4O_MINI = "openai/gpt-4o-mini"


@dataclass
class LLMConfig:
    """Configuration pour un modèle spécifique."""
    provider: LLMProvider
    temperature: float = 0.2
    max_tokens: int = 8192


class GitHubModelsRouter:
    """
    Router Multi-LLM utilisant GitHub Models API.
    
    Authentification via GITHUB_TOKEN.
    Endpoint: https://models.github.ai/inference/chat/completions
    """
    
    GITHUB_MODELS_URL = "https://models.github.ai/inference/chat/completions"
    
    # Mapping Agent → Modèle optimal
    AGENT_MODEL_MAP: Dict[str, LLMConfig] = {
        # Claude pour l'analyse et le code (meilleur en coding)
        "product_owner": LLMConfig(LLMProvider.CLAUDE_SONNET, temperature=0.3),
        "dev_squad": LLMConfig(LLMProvider.CLAUDE_SONNET, temperature=0.1),
        
        # Gemini pour l'architecture
        "tech_lead": LLMConfig(LLMProvider.GEMINI_PRO, temperature=0.2),
        
        # Council : 3 juges différents
        "council_claude": LLMConfig(LLMProvider.CLAUDE_SONNET, temperature=0.4),
        "council_gemini": LLMConfig(LLMProvider.GEMINI_PRO, temperature=0.4),
        "council_gpt4": LLMConfig(LLMProvider.GPT4O, temperature=0.4),
    }
    
    # Alias pour compatibilité
    AGENT_MODEL_MAPPING = AGENT_MODEL_MAP
    
    def __init__(self):
        """Initialise le router avec le token GitHub."""
        self.github_token = get_required_env("GITHUB_TOKEN")
        self._client = httpx.Client(timeout=120.0)
        logger.info("🔌 GitHub Models Router initialisé")
    
    def _get_headers(self) -> Dict[str, str]:
        """Retourne les headers pour l'API GitHub Models."""
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def call(
        self,
        prompt: str,
        agent_name: str,
        system_prompt: str = "You are a helpful assistant.",
        custom_config: LLMConfig | None = None,
        override_model: Optional[LLMProvider] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Appelle le LLM approprié via GitHub Models API.
        
        Args:
            prompt: Le prompt utilisateur
            agent_name: Nom de l'agent (product_owner, dev_squad, etc.)
            system_prompt: Le prompt système
            custom_config: Configuration personnalisée (optionnel, legacy)
            override_model: Forcer un modèle spécifique (optionnel)
            
        Returns:
            Tuple (réponse, usage_metadata)
            
        Raises:
            httpx.HTTPStatusError: Si l'API retourne une erreur
        """
        # Get configuration - custom_config has priority for backward compatibility
        if custom_config:
            config = custom_config
        elif override_model:
            base_config = self.AGENT_MODEL_MAP.get(
                agent_name, 
                LLMConfig(LLMProvider.CLAUDE_SONNET)
            )
            config = LLMConfig(override_model, base_config.temperature)
        else:
            config = self.AGENT_MODEL_MAP.get(
                agent_name, 
                LLMConfig(LLMProvider.CLAUDE_SONNET)
            )
        
        logger.info(f"🤖 Agent '{agent_name}' → Modèle: {config.provider.value}")
        
        payload = {
            "model": config.provider.value,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        
        try:
            response = self._client.post(
                self.GITHUB_MODELS_URL,
                headers=self._get_headers(),
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
                f"✅ Réponse de {config.provider.value} "
                f"({usage_formatted.get('total_token_count', 0)} tokens)"
            )
            
            return content, usage_formatted
            
        except httpx.HTTPStatusError as e:
            logger.error(
                f"❌ Erreur GitHub Models API: {e.response.status_code} - "
                f"{e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            raise

    def list_available_models(self) -> list[str]:
        """Retourne la liste des modèles disponibles."""
        return [p.value for p in LLMProvider]
    
    def get_model_for_agent(self, agent_name: str) -> str:
        """Retourne le modèle configuré pour un agent."""
        config = self.AGENT_MODEL_MAP.get(agent_name)
        if config:
            return config.provider.value
        return LLMProvider.CLAUDE_SONNET.value


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
