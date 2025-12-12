# 🚶 NexusPrime Walkthrough

This document guides you through the lifecycle of a request within the NexusPrime factory.

## Phase 1: Ingestion (The User)
1.  **User Input**: You type a request into the Dashboard (e.g., "Build a Flask API for a Todo App").
2.  **Daemon**: The `nexus_daemon.py` script picks up this request from `request.json` and initializes the LangGraph pipeline.

## Phase 2: Refinement (Product Owner)
1.  **Analysis**: The Product Owner agent reads your vague request.
2.  **Spec Generation**: It uses Gemini to expand this into a technical `SPEC.md`, converting "Todo App" into "Flask Application with endpoints /add, /delete, using SQLite...".
3.  **Output**: `state['spec_document']` is updated.

## Phase 3: Architecture (Tech Lead)
1.  **Memory Check**: The Tech Lead queries `nexus_memory.json` to see if we've built similar apps before. "Ah, we learned last time that Flask needs `app.run(debug=True)` in DEV".
2.  **Environment Decision**: Based on the spec, it decides if this is a `PROD` (strict security, logging) or `DEV` (speed, debug) build.
3.  **Repo Check**: Connects to GitHub to ensure the repository exists.

## Phase 4: Implementation (Dev Squad)
1.  **Coding**: The Dev Squad agent takes the *Spec*, the *Memory Context*, and the *Environment* to write the code.
2.  **File Generation**: It writes the code to `workspace/app_dev.py` (or `_prod.py`).
3.  **Token Tracking**: Costs are calculated and logged.

## Phase 5: Governance (The Council)
1.  **Audit**: The compiled code is sent to The Council (a specialized prompting mode of Gemini).
2.  **Scoring**: It assigns a score (0-100) based on Clarity, Security, and Robustness.
3.  **Decision**:
    *   **Score > 75 (DEV) / 95 (PROD)**: ✅ Approved.
    *   **Score < Threshold**: ❌ Rejected -> Sent back to Dev Squad for retry (Loop).

## Phase 6: Delivery
1.  **Learning**: If successful, a "Lesson" is extracted and saved to `nexus_memory.json` for future agents.
2.  **Deployment**: The file is pushed to GitHub via the API.
3.  **Notification**: The Dashboard shows "DONE" and the Quality Score turns Green.
