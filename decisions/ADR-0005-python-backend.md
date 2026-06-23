# ADR-0005: Python Backend

- Status: Accepted (frozen 2026-06-23)
- Context: ThesisOS spans backend APIs, a LangGraph orchestrator, multiple agents, retrieval, ingestion, and ML-adjacent work. The richest ecosystem for orchestration, retrieval, embeddings, and document processing — LangGraph, LiteLLM, pgvector tooling, docling/marker/pymupdf — is Python. The frontend, by contrast, is a Next.js ChatGPT-style UI that is naturally TypeScript.
- Decision: We use Python everywhere on the server side — backend, orchestrator, agents, and retrieval — and TypeScript only in the Next.js frontend.
- Consequences: A single server-side language keeps shared schemas, tooling, and developer context unified, and aligns the stack with the LangGraph/ML ecosystem. The boundary is clean: the contract between Python backend and TS frontend is the OpenAPI/REST surface, with no language sprawl in between.
- Alternatives considered: A TypeScript backend or polyglot services were rejected because they add operational and cognitive complexity and pull away from the Python-centric ecosystem fit for LangGraph and ML workloads.
