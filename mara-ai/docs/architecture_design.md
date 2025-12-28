# Mara AI: Technical Architecture Design

## Executive Summary
This document outlines the proposed technical architecture for Mara AI. The design prioritizes **reliability, traceability, and scalability**, ensuring that long-running agentic workflows are durable and deterministic. We leverage **Temporal** for orchestration to handle the complexity of stateful missions and retries, ensuring that no "decision" or "action" is ever lost.

## High-Level Architecture

```mermaid
graph TD
    User[User / Client App] -->|SSE / WebSocket| API[API Gateway / Mission OS]
    
    subgraph "Mission OS (Orchestration Layer)"
        API -->|Trigger| Temporal[Temporal Server]
        Temporal -->|Execute Activity| Worker[Worker Nodes]
        Worker -->|State| DB[(Postgres)]
        Worker -->|Cache/Queue| Redis[(Redis)]
    end
    
    subgraph "Multi-Agent Runtime"
        Worker -->|Route| Router[Router Agent]
        Router -->|Plan| Planner[Planner Agent]
        Router -->|Execute| Executor[Tool-Use Agents]
        Executor -->|Verify| Critic[Verifier Agent]
    end
    
    subgraph "Knowledge & Retrieval"
        Executor -->|Search| WebSearch[Web Search APIs]
        Executor -->|Vector Query| VectorDB[(Weaviate/Pinecone)]
        Executor -->|Crawl| Crawler[Headless Browser / Scraper]
    end
    
    subgraph "LLM Gateway"
        Router & Planner & Executor & Critic -->|Inference| LLM[LLM Router (OpenAI/Anthropic/Local)]
    end
```

## Core Components

### 1. Mission OS (The "Brain")
*   **Technology**: Python (FastAPI) + Temporal.io
*   **Role**: The central nervous system. It does not just "run" code; it manages the *lifecycle* of a mission.
*   **Key Feature: Durable Execution**:
    *   Every step (Plan -> Search -> Decide -> Act) is a Temporal Activity.
    *   If a worker crashes or an API fails, Temporal retries automatically with exponential backoff.
    *   **"Time Travel" Debugging**: We can replay the exact history of a mission to understand why a decision was made.

### 2. Multi-Agent Runtime
*   **Pattern**: Supervisor-Worker or Hierarchical Teams (using LangGraph or custom Temporal workflows).
*   **Agents**:
    *   **Planner**: Decomposes the high-level goal into a DAG of steps.
    *   **Retriever**: Specialized in formulating search queries and extracting "nuggets" of evidence.
    *   **Synthesizer**: Combines evidence into coherent answers.
    *   **Critic/Verifier**: A separate LLM call that specifically looks for hallucinations or logical fallacies in the Synthesizer's output.
*   **Schema Enforcement**: All tool outputs are validated against Pydantic models (JSON Schema) before being passed to the next step.

### 3. Evidence-Backed Search
*   **Hybrid Retrieval**:
    *   **Keyword**: For specific entities ("Project X budget").
    *   **Vector**: For semantic concepts ("Risks associated with Project X").
*   **Source Scoring**:
    *   We will implement a `CredibilityScore` for each URL/Snippet based on domain authority and cross-referencing.
    *   **Conflict Resolution**: If Source A says "X" and Source B says "Y", the Synthesizer agent is prompted to highlight the conflict rather than hallucinate a middle ground.

### 4. Data Layer
*   **Postgres**:
    *   `Missions`: Stores high-level mission metadata and final outputs.
    *   `AuditLogs`: Immutable log of every tool call and user approval.
*   **Vector DB (Weaviate/Pinecone)**:
    *   Stores "Knowledge Artifacts" extracted from web search or uploaded documents for long-term memory.
*   **Redis**:
    *   Hot cache for active user sessions and real-time UI updates (Pub/Sub).

## Handling Failure & Risk

| Failure Mode | Mitigation Strategy |
| :--- | :--- |
| **LLM Hallucination** | 1. **Grounding**: All claims must cite a retrieved snippet ID.<br>2. **Verifier Loop**: A separate "Critic" agent reviews the output against the sources before showing it to the user. |
| **Workflow Crash** | **Temporal Workflows**: The state is persisted. If the server restarts, the workflow resumes exactly where it left off (no data loss). |
| **Infinite Loops** | **Step Limits & Budgeting**: Each mission has a max "step budget" and max "retry count". |
| **Bad Tool Output** | **Strict Schemas**: Pydantic validation ensures tools return data in the expected format, or raise a structured error for the LLM to handle. |

## Why This Stack?
*   **Temporal**: Essential for "long-running" (minutes/hours) workflows. Standard queues (Celery) are insufficient for complex state management and parent/child workflows.
*   **FastAPI**: High performance, native async support (great for LLM streaming), and auto-generated OpenAPI docs for the frontend.
*   **Python**: The native language of AI. Allows seamless integration with LlamaIndex/LangChain/DSPy if needed.
