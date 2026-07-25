# Architecture

## Version 1

RegIntel is an evidence-bound RAG service. It does not use an autonomous agent.

```text
Public FCA / GOV.UK documents
          |
          v
Ingestion worker
fetch -> validate -> parse -> normalize -> hash -> chunk -> embed
          |
          v
PostgreSQL + pgvector
documents -> versions -> chunks -> embeddings -> audit records
          |
          v
FastAPI service
validate question -> retrieve -> rerank -> generate structured answer
          |
          +--> answered with citations
          +--> insufficient evidence
          +--> human review required
```

## Components

| Component | Responsibility |
|---|---|
| FastAPI | Typed HTTP API and OpenAPI documentation |
| PostgreSQL | Relational metadata, audit records, feedback, and query history |
| pgvector | Semantic retrieval over document chunks |
| Redis | Queue broker and short-lived operational state |
| Celery worker | Ingestion and later scheduled collection |
| Object storage | Raw files and extracted-document artifacts |
| OpenAI adapter | Embeddings and structured answer generation |
| Pydantic | Request, response, tool, and extraction validation |
| Pytest | Unit, integration, and evaluation regression tests |
| Docker Compose | Reproducible local development environment |

## Trust boundaries

1. Public documents are untrusted input.
2. The application validates URLs against an allow-list.
3. Extracted source text is evidence, never executable instruction.
4. Model output is untrusted until schema and citation validation succeeds.
5. Secrets are supplied by environment variables and are never committed.
