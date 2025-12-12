# 🔑 Configuration des clés API pour NexusPrime

NexusPrime utilise **3 APIs différentes** pour accéder aux meilleurs modèles d'IA.

## Prérequis

- Un compte **Anthropic** avec accès à l'API Claude
- Un compte **Google** avec accès à l'API Google AI
- Un compte **GitHub** pour l'API GitHub Models

## 1. Anthropic API Key (Claude Sonnet 4)

### Obtenir la clé

1. Crée un compte sur [console.anthropic.com](https://console.anthropic.com/)
2. Va dans **API Keys** dans le menu
3. Clique sur **Create Key**
4. Copie la clé (format: `sk-ant-...`)

### Utilisation

Cette clé est utilisée pour :
- **Product Owner** : Analyse et génération de spécifications
- **Dev Squad** : Génération de code précise
- **Council Judge (Claude)** : Évaluation qualité

## 2. Google API Key (Gemini 3 Pro)

### Obtenir la clé

1. Va sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique sur **Get API Key**
3. Crée une nouvelle clé ou utilise une existante
4. Copie la clé (format: `AIza...`)

### Utilisation

Cette clé est utilisée pour :
- **Tech Lead** : Architecture et setup d'environnement
- **Council Judge (Gemini)** : Revue technique et sécurité

## 3. GitHub Token (GitHub Models API)

### Obtenir un Personal Access Token (PAT)

### Étape 1 : Accéder aux paramètres

1. Connecte-toi sur [github.com](https://github.com)
2. Clique sur ton **avatar** (en haut à droite)
3. Va dans **Settings**

### Étape 2 : Créer le token

1. Dans le menu de gauche, clique sur **Developer settings** (tout en bas)
2. Clique sur **Personal access tokens** → **Tokens (classic)**
3. Clique sur **Generate new token** → **Generate new token (classic)**

### Étape 3 : Configurer les permissions

- **Note** : `NexusPrime Factory`
- **Expiration** : 90 jours (ou plus selon tes besoins)
- **Scopes** à cocher :
  - ✅ `repo` (accès aux repositories)
  - ✅ `read:org` (si tu utilises une organisation)

### Étape 4 : Copier le token

⚠️ **IMPORTANT** : Copie le token immédiatement ! Il ne sera plus visible après.

Le token ressemble à : `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Utilisation

Ce token est utilisé pour :
- **Council Judge (Grok 3)** : Analyse créative et critique
- **Council Judge (GPT-5)** : Raisonnement avancé et validation

## Configurer NexusPrime

### Option A : Fichier .env (Recommandé)

Crée un fichier `.env` à la racine du projet :

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Option B : Variables d'environnement (Terminal)

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Option C : GitHub Codespaces

Le token est **automatiquement disponible** ! Rien à configurer.

### Option D : GitHub Actions

Utilise le secret automatique `${{ secrets.GITHUB_TOKEN }}` ou configure un secret personnalisé.

## Vérifier que ça fonctionne

```bash
python -c "from nexusprime.core.llm_router import get_llm_router; r = get_llm_router(); print('✅ Router OK - 3 APIs configurées')"
```

## Modèles disponibles par API

### Anthropic API
| Modèle | ID | Usage dans NexusPrime |
|--------|----|-----------------------|
| Claude Sonnet 4 | `claude-sonnet-4-20250514` | Product Owner, Dev Squad, Council Judge |

### Google AI API
| Modèle | ID | Usage dans NexusPrime |
|--------|----|-----------------------|
| Gemini 3 Pro | `gemini-3-pro-preview` | Tech Lead, Council Judge |

### GitHub Models API
| Modèle | ID | Usage dans NexusPrime |
|--------|----|-----------------------|
| Grok 3 | `azureml-xai/grok-3` | Council Judge |
| GPT-5 | `azure-openai/gpt-5` | Council Judge |

## Dépannage

### Erreur 401 Unauthorized (Anthropic)
- Vérifie que `ANTHROPIC_API_KEY` est correcte
- Vérifie que tu as des crédits API disponibles
- Consulte : https://console.anthropic.com/

### Erreur 401 Unauthorized (Google)
- Vérifie que `GOOGLE_API_KEY` est correcte
- Vérifie que l'API Google AI est activée
- Consulte : https://makersuite.google.com/

### Erreur 401 Unauthorized (GitHub)
- Vérifie que `GITHUB_TOKEN` est valide
- Vérifie les scopes de ton token
- Consulte : https://github.com/settings/tokens

### Erreur 403 Forbidden
- Vérifie que tu as accès au modèle demandé
- Certains modèles nécessitent un accès spécial
- Contacte le support de l'API concernée

### Erreur 429 Rate Limit
- Tu as dépassé ta limite de requêtes pour cette API
- Attends quelques minutes et réessaie
- Considère upgrader ton plan API

## Plus d'informations

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Google AI Documentation](https://ai.google.dev/)
- [GitHub Models Documentation](https://github.com/marketplace/models)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
