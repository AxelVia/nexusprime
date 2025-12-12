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

## Phase 5: Governance (The Council - Multi-LLM Review)
1.  **Phase 1 - Independent Reviews**: The code is sent to three independent AI judges:
    *   **Grok 3** (xAI): Provides creative and critical analysis
    *   **Gemini 2.5 Pro** (Google): Focuses on technical accuracy and security
    *   **Claude Sonnet 4** (Anthropic): Evaluates quality and best practices
    
    Each judge independently assigns:
    - A score (0-100) based on Clarity, Security, Robustness, and Completeness
    - Detailed reasoning for their score
    - List of specific concerns (if any)

2.  **Phase 2 - Arbitration**: Claude Sonnet 4 acts as the lead arbitrator:
    - Reviews all three independent opinions
    - Considers areas of agreement and disagreement
    - Weighs the severity of concerns raised
    - Synthesizes opinions into a final definitive score (0-100)

3.  **Decision**:
    *   **Score > 75 (DEV) / 95 (PROD)**: ✅ Approved → Proceed to Delivery
    *   **Score < Threshold**: ❌ Rejected → Sent back to Dev Squad for retry (Loop, max 5 iterations)

### Example Council Report

```
======================================================================
COUNCIL MULTI-LLM REVIEW REPORT
======================================================================

INDIVIDUAL REVIEWS:
----------------------------------------------------------------------
Reviewer        Model                Score    Concerns
----------------------------------------------------------------------
Grok            grok-3                 82/100      1
Gemini          gemini-2.5-pro         85/100      0
Claude          claude-sonnet-4        88/100      1
----------------------------------------------------------------------

DETAILED OPINIONS:
----------------------------------------------------------------------

Grok (grok-3):
  Score: 82/100
  Reasoning: Specification is mostly clear with good structure. Minor 
             ambiguity in error handling scenarios.
  Concerns: Error handling edge cases not fully specified

Gemini (gemini-2.5-pro):
  Score: 85/100
  Reasoning: Strong technical foundation with proper security 
             considerations. Well-structured approach.
  Concerns: None

Claude (claude-sonnet-4):
  Score: 88/100
  Reasoning: High-quality specification with clear requirements. 
             Excellent attention to robustness.
  Concerns: Could benefit from more detailed logging strategy

----------------------------------------------------------------------
FINAL ARBITRATION (Claude):
----------------------------------------------------------------------
Final Score: 85/100
Reasoning: Strong consensus among reviewers with minor concerns that 
           don't significantly impact overall quality. Specification 
           meets high standards for clarity and completeness.
======================================================================
```

## Phase 6: Delivery
1.  **Learning**: If successful, a "Lesson" is extracted and saved to `nexus_memory.json` for future agents.
2.  **Deployment**: The file is pushed to GitHub via the API.
3.  **Notification**: The Dashboard shows "DONE" and the Quality Score turns Green.
