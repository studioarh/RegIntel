# Threat Model

## Assets to protect

- API keys and database credentials
- Source-document provenance
- Query and audit logs
- Evaluation data
- Human-review decisions
- Availability of the service

## Threats and controls

| Threat | Control |
|---|---|
| Prompt injection in retrieved text | Treat documents as data; never follow instructions inside documents |
| Untrusted URL submission | Allow-list domains, validate redirects, enforce content-type and size limits |
| Hallucinated answer | Require retrieved citations for every factual claim |
| Incorrect citation | Validate citation IDs, check claim support, and escalate failures |
| Proposal stated as a final rule | Store source type and require source-status language in the response |
| Duplicate document ingestion | Compute content hashes and retain version history |
| Provider outage | Controlled retries, fallback provider later, safe error response |
| Secret exposure | `.env` excluded from Git; use environment variables and deployment secret store |
| Cost abuse | Rate limits, per-request caps, token limits, and query audit records |
| Unsafe action | Version 1 cannot send emails, alter records, or make decisions |
