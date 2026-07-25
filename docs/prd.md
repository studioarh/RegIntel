# RegIntel Product Requirements Document

## Product

RegIntel is a traceable regulatory-intelligence application for UK consumer-credit
monitoring. It ingests allow-listed public documents, retrieves source passages,
and generates evidence-cited answers or escalates work for human review.

## Problem

UK consumer-credit firms must monitor regulatory publications, consultations,
policy statements, Handbook changes, and government announcements. These materials
are distributed across long and frequently updated public documents. Teams need a
repeatable way to identify relevant changes and inspect the exact source evidence.

## Primary user

A compliance analyst at a UK consumer-lending firm.

## Primary user job

Identify new or changed regulatory material that may affect consumer-credit
operations, then review the source passages before deciding whether specialist
legal or compliance action is needed.

## First release

The first release will:
- Ingest selected public FCA and GOV.UK documents.
- Store document metadata, text, chunks, and source provenance.
- Retrieve relevant evidence for a user question.
- Generate an answer only from retrieved evidence.
- Attach citations to every factual claim.
- Return insufficient evidence or create a review task when evidence is weak,
  contradictory, missing, or uncited.

## Non-goals

- Legal advice.
- Automated compliance decisions.
- Automatic emails or changes to external systems.
- General web search.
- Autonomous agents that can take external actions.
- Supporting every UK regulator or financial sector in the first version.

## Success criteria

A user can submit a supported question and receive:
1. An answer based only on stored source passages.
2. A citation for every factual claim.
3. Source title, URL, publication date, source type, excerpt, and page or section.
4. An uncertainty statement where the source is a proposal, incomplete, or conflicting.

A user asking a question not supported by retrieved evidence receives:
- `insufficient_evidence`, or
- `human_review_required`.

## Constraints

- Only allow-listed primary public sources may be ingested.
- Retrieved document text is untrusted data and cannot act as instructions.
- Prompts, retrieval settings, model configuration, and source versions must be stored.
- The system must not make regulated decisions or external changes.
