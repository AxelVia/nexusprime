# 🏭 NexusPrime: Autonomous AI Software Factory

NexusPrime is a state-of-the-art **AI Software Factory** designed to autonomously generate, refine, code, and validate software projects. Built on **LangGraph** and powered by **Google Gemini Pro**, it simulates a full agile team (Product Owner, Tech Lead, Dev Squad, Review Council) to deliver production-ready code.

## 🧠 Core Architecture

The system is composed of specialized AI Agents working in a directed graph:

1.  **🕵️ Product Owner**: Analyzes user prompts, refines requirements, and generates a strict `SPEC.md`.
2.  **🌐 Tech Lead**: Sets up the environment (DEV/PROD), manages memory (RAG), and initializes the workspace.
3.  **⚡ Dev Squad**: Writes the actual code based on the spec, adhering to strict coding standards.
4.  **⚖️ The Council**: Performs a rigorous code audit (Quality Score 0-100). If the score is low, it rejects the code and sends it back for refactoring.
5.  **📂 Git Integrator**: Once validated, the code is automatically pushed to this repository.

## 🚀 Features

*   **Real-Time Dashboard**: Monitor the factory's internal state, logs, and token usage via a futuristic Streamlit interface.
*   **Persistent Memory**: The system "learns" from successful projects using a JSON-based RAG system (`nexus_memory.json`).
*   **Dual Environment**: Automatically detects if a request needs a "Prototype" (DEV) or "Production" (PROD) approach.
*   **Self-Healing**: "The Council" node loops back to development until quality criteria are met.
*   **Automated Git Sync**: Projects are pushed to GitHub upon completion.

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
    GOOGLE_API_KEY=your_gemini_key
    GITHUB_TOKEN=your_github_token_with_repo_scope
    ```

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

*   `nexus_factory.py`: The brain. Contains LangGraph nodes and agent logic.
*   `dashboard.py`: The control center UI.
*   `nexus_memory.py`: The RAG memory module.
*   `nexus_daemon.py`: Background service watching for new requests.
*   `workspace/`: Directory where AI generates the output.

---
*Built with ❤️ by Antigravity & Gemini*
