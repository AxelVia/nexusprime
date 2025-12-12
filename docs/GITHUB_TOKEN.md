# 🔑 Configuration du GitHub Token pour NexusPrime

## Prérequis

- Un compte GitHub avec **GitHub Copilot** activé (Pro, Business ou Enterprise)
- Accès à **GitHub Models** (inclus avec Copilot)

## Obtenir un Personal Access Token (PAT)

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
  - ✅ `copilot` (accès à GitHub Copilot/Models)

### Étape 4 : Copier le token

⚠️ **IMPORTANT** : Copie le token immédiatement ! Il ne sera plus visible après.

Le token ressemble à : `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Configurer NexusPrime

### Option A : Fichier .env (Local)

Crée un fichier `.env` à la racine du projet :

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Option B : Variable d'environnement (Terminal)

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Option C : GitHub Codespaces

Le token est **automatiquement disponible** ! Rien à configurer.

### Option D : GitHub Actions

Utilise le secret automatique `${{ secrets.GITHUB_TOKEN }}` ou configure un secret personnalisé.

## Vérifier que ça fonctionne

```bash
python -c "from nexusprime.core import get_llm_router; r = get_llm_router(); print('✅ Router OK')"
```

## Modèles disponibles

| Modèle | ID | Usage dans NexusPrime |
|--------|----|-----------------------|
| Claude Sonnet 4 | `anthropic/claude-sonnet-4` | Product Owner, Dev Squad, Council |
| Gemini 2.5 Pro | `google/gemini-2.5-pro` | Tech Lead, Council |
| GPT-4o | `openai/gpt-4o` | Council |
| GPT-4o Mini | `openai/gpt-4o-mini` | Disponible |

## Dépannage

### Erreur 401 Unauthorized
- Vérifie que ton token est valide
- Vérifie que tu as GitHub Copilot activé

### Erreur 403 Forbidden
- Vérifie les scopes de ton token
- Vérifie que tu as accès à GitHub Models

### Erreur 429 Rate Limit
- Tu as dépassé ta limite de requêtes
- Attends quelques minutes et réessaie

## Plus d'informations

- [GitHub Models Documentation](https://docs.github.com/en/github-models)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
