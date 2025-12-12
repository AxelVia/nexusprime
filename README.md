# 🏭 NexusPrime: Autonomous AI Software Factory

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

NexusPrime is a state-of-the-art **AI Software Factory** designed to autonomously generate, refine, code, and validate software projects. Built on **LangGraph** and powered by a **Multi-API Architecture** (Anthropic, Google AI, GitHub Models), it simulates a full agile team (Product Owner, Tech Lead, Dev Squad, Review Council) to deliver production-ready code.

## 🧠 Core Architecture

The system is composed of specialized AI Agents working in a directed graph:

1.  **🕵️ Product Owner** (Powered by **Claude Sonnet 4** via **Anthropic API**): Analyzes user prompts, refines requirements, and generates a strict `SPEC.md`.
2.  **🌐 Tech Lead** (Powered by **Gemini 3 Pro** via **Google AI API**): Sets up the environment (DEV/PROD), manages memory (RAG), and initializes the workspace.
3.  **⚡ Dev Squad** (Powered by **Claude Sonnet 4** via **Anthropic API**): Writes the actual code based on the spec, adhering to strict coding standards.
4.  **⚖️ The Council** (Multi-LLM Debate System): Performs a rigorous code audit with four independent judges:
    - **Grok 3** (via **GitHub Models API**) - Creative & Critical Analysis
    - **Gemini 3 Pro** (via **Google AI API**) - Technical & Security Review
    - **Claude Sonnet 4** (via **Anthropic API**) - Quality & Best Practices Assessment
    - **GPT-5** (via **GitHub Models API**) - Advanced reasoning & validation
    - **Final Arbitration** by Claude synthesizes all opinions into a definitive Quality Score (0-100)
5.  **📂 Git Integrator**: Once validated, the code is automatically pushed to this repository.

## 🎯 Multi-API Architecture

NexusPrime leverages the strengths of multiple AI models through **three separate APIs**:

```
┌─────────────────────────────────────────────────────────────────┐
│                         NexusPrime Factory                      │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Product    │    │  Tech Lead   │    │  Dev Squad   │      │
│  │    Owner     │───▶│              │───▶│              │      │
│  │ (Claude)     │    │  (Gemini)    │    │  (Claude)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Anthropic    │    │  Google AI   │    │ Anthropic    │      │
│  │    API       │    │    API       │    │    API       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
│                      ┌──────────────────────┐                   │
│                      │     The Council      │                   │
│                      │    (4 Judges)        │                   │
│                      │                      │                   │
│                      │  ┌────────────────┐  │                   │
│                      │  │ Claude │ Gemini│  │                   │
│                      │  │ (Anthr)│(Google)│  │                   │
│                      │  └────────────────┘  │                   │
│                      │  ┌────────────────┐  │                   │
│                      │  │ Grok 3 │ GPT-5 │  │                   │
│                      │  │(GitHub)│(GitHub)│  │                   │
│                      │  └────────────────┘  │                   │
│                      └──────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Agent → Model Mapping

| Agent | Model | API | Temperature | Purpose |
|-------|-------|-----|-------------|---------|
| Product Owner | Claude Sonnet 4 | Anthropic | 0.3 | Requirement analysis & specification |
| Tech Lead | Gemini 3 Pro | Google AI | 0.2 | Architecture & environment setup |
| Dev Squad | Claude Sonnet 4 | Anthropic | 0.1 | Precise code generation |
| Council Judge 1 | Claude Sonnet 4 | Anthropic | 0.4 | Quality & best practices assessment |
| Council Judge 2 | Gemini 3 Pro | Google AI | 0.4 | Technical & security audit |
| Council Judge 3 | Grok 3 | GitHub Models | 0.4 | Creative & critical review |
| Council Judge 4 | GPT-5 | GitHub Models | 0.4 | Advanced reasoning & validation |

### The Council: Multi-LLM Debate System

The Council uses a unique **debate and arbitration** process:

1. **Phase 1: Independent Reviews** - Each of the 4 judges (Claude, Gemini, Grok, GPT-5) independently evaluates the specification based on:
   - Clarity: Is the spec clear and unambiguous?
   - Security: Does it address security concerns?
   - Robustness: Is it designed for reliability?
   - Completeness: Are all details included?

2. **Phase 2: Arbitration** - Claude acts as the lead arbitrator, synthesizing all opinions:
   - Considers areas of agreement and disagreement
   - Weighs severity of concerns raised
   - Provides final definitive score (0-100)

3. **Decision** - Based on environment thresholds:
   - **DEV**: Approved if score > 75
   - **PROD**: Approved if score > 95
   - If rejected, code loops back to Dev Squad for revision

## 🚀 Features

*   **Multi-API Intelligence**: Harnesses three separate APIs (Anthropic, Google AI, GitHub Models) for optimal results
*   **Council Debate System**: Four independent AI judges review every output with final arbitration
*   **Real-Time Dashboard**: Monitor the factory's internal state, active agents, and token usage via a futuristic Streamlit interface
*   **Persistent Memory**: The system "learns" from successful projects using a JSON-based RAG system (`nexus_memory.json`)
*   **Dual Environment**: Automatically detects if a request needs a "Prototype" (DEV) or "Production" (PROD) approach
*   **Self-Healing**: "The Council" node loops back to development until quality criteria are met (max 5 iterations)
*   **Automated Git Sync**: Projects are pushed to GitHub upon approval
*   **Best-in-Class Models**: Leverages Claude Sonnet 4, Gemini 3 Pro, Grok 3, and GPT-5

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/AxelVia/nexusprime.git
    cd nexusprime
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file with your API keys:
    ```ini
    GITHUB_TOKEN=your_github_token_here
    ANTHROPIC_API_KEY=your_anthropic_key_here
    GOOGLE_API_KEY=your_google_key_here
    ```
    
    **Required API Keys**:
    - `GITHUB_TOKEN`: GitHub personal access token (for GitHub Models API - Grok 3, GPT-5)
    - `ANTHROPIC_API_KEY`: Anthropic API key (for Claude Sonnet 4)
    - `GOOGLE_API_KEY`: Google AI API key (for Gemini 3 Pro)

## 🎮 Usage

1.  **Launch the Dashboard & Daemon**:
    ```bash
    streamlit run dashboard.py
    ```
    *In a separate terminal, ensure `nexus_daemon.py` is running if not launched automatically.*

2.  **Submit a Request**:
    *   Open the Dashboard (http://localhost:8501).
    *   Expand **"🚀 Lancer un Nouveau Projet"**.
    *   Describe your need (e.g., *"Create a secure Python calculator library"*).
    *   Click **"Démarrer l'Usine"**.

3.  **Watch it Build**:
    Follow the agents in real-time on the "SYSTEM MONITOR" tab. The final code will appear in the `workspace/` folder and be pushed to GitHub.

## 📁 Project Structure

*   `nexusprime/`: Main package
    *   `agents/`: Specialized AI agents (Product Owner, Tech Lead, Dev Squad, Council)
    *   `core/`: Core functionality (LLM Router, State Management, Graph)
    *   `integrations/`: External integrations (GitHub, Memory/RAG)
    *   `utils/`: Utilities (Logging, Tokens, Status, Security)
    *   `ui/`: Dashboard UI components and styles
*   `dashboard.py`: The control center UI
*   `nexus_factory.py`: Legacy entry point
*   `workspace/`: Directory where AI generates the output

---

## 🤖 Powered By

<div align="center">

**Multi-API Architecture**

| Claude Sonnet 4 | Gemini 3 Pro | Grok 3 | GPT-5 |
|:---:|:---:|:---:|:---:|
| Anthropic API | Google AI API | GitHub Models | GitHub Models |
| Requirements & Code | Architecture & Review | Creative Analysis | Advanced Reasoning |

*Orchestrated through dedicated API integrations*

</div>

---

*Built with ❤️ by the NexusPrime Team*
