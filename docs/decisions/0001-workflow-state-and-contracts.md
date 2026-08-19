# ADR 0001: Workflow State and Contracts

- **Status:** Accepted
- **Date:** 2026-08-19
- **Decision makers:** RegIntel project

## Context

RegIntel currently ingests regulatory documents and answers user questions using retrieval-augmented generation (RAG) with citations.

Week 3 introduces a controlled workflow that processes an already-ingested document into a traceable regulatory-intelligence briefing. The workflow must:

1. Load a document and validate that it can be processed.
2. Locate a prior version where one exists.
3. Produce a deterministic text diff.
4. Retrieve supporting source chunks.
5. Extract structured regulatory facts.
6. Generate a cited briefing.
7. Apply explicit quality rules.
8. Either approve the briefing or create a human-review task.

The workflow needs stable contracts before LangGraph nodes, database persistence, or LLM extraction are implemented. Without explicit contracts, the system could produce unverifiable claims, allow schema drift, or make inconsistent approval decisions.

## Decision

Use Pydantic v2 models for all important workflow artifacts and use a typed LangGraph workflow state as the shared container passed between nodes.

The initial contracts are:

- `EvidenceCitation`
- `RegulatoryFact`
- `QualityDecision`
- `DocumentDiff`
- `ChangeExtraction`
- `BriefingClaim`
- `RegulatoryBriefing`
- `WorkflowState`

All API-facing and LLM-produced artifact models must reject unknown fields with `extra="forbid"`.

## Evidence contract

`EvidenceCitation` represents a source chunk retrieved during the current workflow run. It contains the chunk ID, document ID, title, URL, source excerpt, publication date where available, and retrieval relevance score.

A citation is valid for a workflow run only when:

- Its `chunk_id` belongs to a chunk actually retrieved in that run.
- Its `document_id` identifies the source document containing the chunk.
- Its excerpt is non-empty.
- Its source URL is valid.

The system must not create a factual briefing claim without one or more valid citation chunk IDs.

## Fact contract

`RegulatoryFact` represents an evidence-backed extracted fact, such as an obligation, deadline, scope change, effective date, enforcement statement, or consultation detail.

Every fact must contain:

- A supported, non-empty statement.
- A known fact type.
- A sector classification of `consumer_lending` or `unknown`.
- At least one citation chunk ID.

Uncertainty is captured explicitly in the optional `uncertainty` field. The system must not silently remove uncertainty that is present in the source material or introduced by incomplete evidence.

## Quality-decision contract

`QualityDecision` is a rule-based workflow outcome with one of two states:

- `approved`: The output passed all configured quality gates.
- `review_required`: A human must review the candidate result before it can be relied upon.

For the initial implementation, a workflow is approved only when all of the following are true:

- Structured extraction validates against its Pydantic schema.
- Every factual claim references one or more allowed citation chunk IDs.
- Citation coverage is exactly `1.0` for factual claims.
- The configured minimum retrieval-quality signal is met.
- No critical uncertainty flag is present.

`review_required` must include at least one human-readable reason. `approved` must not contain review reasons.

Retrieval scores are internal quality signals, not calibrated probabilities. They will be evaluated and calibrated, if appropriate, during Week 4.

## Briefing contract

The system produces a structured `RegulatoryBriefing` rather than relying only on free-form Markdown. The presentation layer may render this object as Markdown or HTML.

Briefing claims are classified as either:

- `source_fact`: A statement directly supported by a cited source passage.
- `analyst_interpretation`: A clearly labelled inference that remains linked to the cited factual basis.

The briefing includes:

- Document title, source URL, and publication date where available.
- What changed.
- Why the change may matter to consumer-lending firms.
- Key dates.
- Source citations for factual claims.
- Explicit uncertainty flags.
- The final approval or review status.

If the available evidence is weak, incomplete, contradictory, or cannot establish sector relevance, the workflow must return `review_required` rather than present a confident conclusion.

## Workflow-state contract

`WorkflowState` is a typed shared state container used by LangGraph. It carries the identifiers, intermediate artifacts, configuration versions, final result, and any failure information for one workflow run.

The workflow state is not the source of truth for all persistence. Important records will also be stored in PostgreSQL. In particular, future `workflow_runs` and `review_tasks` tables will support audit, filtering, replay, and human review.

Each LangGraph node returns only a partial update to the state. Nodes must not perform unrelated work or overwrite fields owned by another node.

### Field ownership

| State field or artifact | Owner |
|---|---|
| `workflow_run_id`, `trace_id`, configuration versions | Workflow application service |
| Document text and document metadata | `load_document` node |
| Prior-document identifier and `diff` | `locate_prior_version` and `create_diff` nodes |
| `evidence` | `retrieve_evidence` node |
| `extraction` | `extract_facts` node |
| `briefing` | `generate_briefing` node |
| `quality_decision` | `quality_gate` node |
| Approved briefing persistence | `persist_approved_briefing` node |
| Review task persistence | `create_review_task` node |
| `status` and `error_message` | Workflow service and explicit failure handling |

## Consequences

### Positive

- Workflow inputs, outputs, and quality decisions are explicit and testable.
- LLM extraction output can be validated before it affects a briefing.
- Every factual claim can be checked against retrieved evidence.
- LangGraph orchestration stays thin because business artifacts already have stable types.
- The same contracts can be reused by FastAPI routes, services, workers, database persistence, and evaluation scripts.
- A review-required outcome is a normal safe outcome rather than an unhandled error.

### Trade-offs

- The initial models add implementation effort before visible workflow features are available.
- Strict schemas may route malformed or incomplete model output to review more often at first.
- Contract changes require migrations to tests, prompt schemas, API models, and persistence code.

These trade-offs are accepted because RegIntel prioritises traceability and safe evidence-backed outputs over unrestricted generation.

## Alternatives considered

### Free-form LLM output

Rejected. Free-form prose is difficult to validate, cannot reliably enforce citations per claim, and makes quality gating inconsistent.

### One untyped dictionary for all workflow data

Rejected. Untyped dictionaries allow silent key mistakes, schema drift, unclear field ownership, and weak API and test contracts.

### An autonomous agent loop

Rejected for the first version. RegIntel will use an explicit graph with fixed nodes and conditional routing. This makes workflow decisions inspectable, repeatable, and easier to test.

### Immediate human interrupt and resume

Deferred. Week 3 will create persistent database review tasks and end the workflow with `review_required`. Durable LangGraph checkpointing and interrupt/resume may be introduced later when reviewer input must alter state and resume a paused run.

## Implementation notes

- Store artifact models in `src/agents/schemas.py`.
- Store `WorkflowState` in `src/agents/state.py`.
- Add unit tests in `tests/unit/agents/test_schemas.py`.
- Use `UUID` identifiers for documents, chunks, workflow runs, and review tasks.
- Use `AnyHttpUrl` for source URLs.
- Use constrained fields for non-empty text and bounded quality signals.
- Set `extra="forbid"` on external and LLM-facing Pydantic models.
- Run Ruff, mypy, and pytest before opening the pull request.

## Review triggers

The workflow must create a review task, rather than approve a briefing, when any of the following occurs:

- A document cannot be loaded or validated.
- No prior version can be resolved when comparison is required, or comparison input is malformed.
- Diff input is truncated in a way that could affect the result.
- Structured extraction fails validation.
- A fact has no citation or cites a chunk not retrieved for this run.
- Citation coverage is below 100% for factual claims.
- Retrieval-quality signal is below the configured threshold.
- Evidence is contradictory, insufficient, or outside the supported document corpus.
- A critical uncertainty flag is present.
- An LLM, retrieval, parsing, or persistence failure occurs.

## Status and next step

This decision is accepted for Week 3 Issue 1. Once the schemas, state definition, and unit tests are merged, the next issue is workflow and review persistence: introduce `workflow_runs` and `review_tasks` tables, an Alembic migration, repository methods, and PostgreSQL integration tests.