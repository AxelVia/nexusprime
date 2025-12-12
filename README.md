# 🏭 NexusPrime: Autonomous AI Software Factory

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

NexusPrime is a state-of-the-art **AI Software Factory** designed to autonomously generate, refine, code, and validate software projects. Built on **LangGraph** and powered by a **Multi-LLM Architecture** (Claude, Gemini, Grok), it simulates a full agile team (Product Owner, Tech Lead, Dev Squad, Review Council) to deliver production-ready code.

## 🧠 Core Architecture

The system is composed of specialized AI Agents working in a directed graph:

1.  **🕵️ Product Owner** (Powered by **Claude Sonnet 4**): Analyzes user prompts, refines requirements, and generates a strict `SPEC.md`.
2.  **🌐 Tech Lead** (Powered by **Gemini 2.5 Pro**): Sets up the environment (DEV/PROD), manages memory (RAG), and initializes the workspace.
3.  **⚡ Dev Squad** (Powered by **Claude Sonnet 4**): Writes the actual code based on the spec, adhering to strict coding standards.
4.  **⚖️ The Council** (Multi-LLM Debate System): Performs a rigorous code audit with three independent judges:
    - **Grok 3** - Creative & Critical Analysis
    - **Gemini 2.5 Pro** - Technical & Security Review
    - **Claude Sonnet 4** - Quality & Best Practices Assessment
    - **Final Arbitration** by Claude synthesizes all opinions into a definitive Quality Score (0-100)
5.  **📂 Git Integrator**: Once validated, the code is automatically pushed to this repository.

## 🎯 Multi-LLM Architecture

NexusPrime leverages the strengths of multiple AI models through the **GitHub Copilot API**:

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM ROUTER                               │
│  (GitHub Copilot Chat Completions API)                     │
└─────────────────────────────────────────────────────────────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
┌──────────┐         ┌──────────┐        ┌──────────┐
│ Claude   │         │ Gemini   │        │  Grok    │
│ Sonnet 4 │         │ 2.5 Pro  │        │    3     │
└──────────┘         └──────────┘        └──────────┘
     │                    │                    │
     ▼                    ▼                    ▼
Product Owner       Tech Lead           Council Judge
Dev Squad           Council Judge      Council Judge
Arbitrator
```

### Agent → Model Mapping

| Agent | Model | Temperature | Purpose |
|-------|-------|-------------|---------|
| Product Owner | Claude Sonnet 4 | 0.3 | Requirement analysis & specification |
| Tech Lead | Gemini 2.5 Pro | 0.2 | Architecture & environment setup |
| Dev Squad | Claude Sonnet 4 | 0.1 | Precise code generation |
| Council (Grok) | Grok 3 | 0.4 | Creative & critical review |
| Council (Gemini) | Gemini 2.5 Pro | 0.4 | Technical & security audit |
| Council (Claude) | Claude Sonnet 4 | 0.3 | Quality assessment & arbitration |

### The Council: Multi-LLM Debate System

The Council uses a unique **debate and arbitration** process:

1. **Phase 1: Independent Reviews** - Each of the 3 judges (Grok, Gemini, Claude) independently evaluates the specification based on:
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

*   **Multi-LLM Intelligence**: Harnesses the unique strengths of Claude, Gemini, and Grok for optimal results
*   **Council Debate System**: Three independent AI judges review every output with final arbitration
*   **Real-Time Dashboard**: Monitor the factory's internal state, active agents, and token usage via a futuristic Streamlit interface
*   **Persistent Memory**: The system "learns" from successful projects using a JSON-based RAG system (`nexus_memory.json`)
*   **Dual Environment**: Automatically detects if a request needs a "Prototype" (DEV) or "Production" (PROD) approach
*   **Self-Healing**: "The Council" node loops back to development until quality criteria are met (max 5 iterations)
*   **Automated Git Sync**: Projects are pushed to GitHub upon approval
*   **GitHub Copilot Powered**: Leverages GitHub Copilot API for seamless multi-model access

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
    Create a `.env` file with your keys:
    ```ini
    GOOGLE_API_KEY=your_gemini_key_here
    GITHUB_TOKEN=your_github_token_with_copilot_access
    ```
    
    **Note**: Your `GITHUB_TOKEN` must have GitHub Copilot access enabled to use the Multi-LLM features.

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

**Multi-LLM Architecture via GitHub Copilot**

| Claude Sonnet 4 | Gemini 2.5 Pro | Grok 3 |
|:---:|:---:|:---:|
| Anthropic | Google DeepMind | xAI |
| Requirements & Code | Architecture & Review | Creative Analysis |

*Orchestrated through the GitHub Copilot Chat Completions API*

</div>

---

*Built with ❤️ by the NexusPrime Team*
