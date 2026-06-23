# ADR-0009: Async Background Jobs

- Status: Accepted (frozen 2026-06-23)
- Context: Heavy work such as document ingestion, embedding, OCR, and summarization can take far longer than an HTTP request should, risking request timeouts and a poor user experience if run inline. ThesisOS needs a way to move this work off the request path while keeping a simple interface that can scale later.
- Decision: Heavy work runs out of the request path via a job interface. M0 ships the interface and the `POST /jobs` and `GET /jobs/{id}` contracts backed by an in-process worker stub. The production target is Cloud Run Jobs / Cloud Tasks, reachable through the same interface so callers do not change.
- Consequences: Long-running operations no longer block requests, enqueue/status is contract-defined from the start, and the execution backend can evolve from in-process to durable cloud queues without touching callers. The trade-off is that the M0 in-process worker is not durable, which is acceptable for M0–M6 and revisited before M11.
- Alternatives considered: Synchronous in-request processing was rejected because it causes request timeouts and poor UX for any non-trivial ingestion or embedding workload.
