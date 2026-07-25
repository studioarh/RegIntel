# Database Design

## documents

One canonical public document source.

Key fields:
- id
- canonical_url
- publisher
- title
- source_type
- publication_date
- content_hash
- sector_tags
- status
- metadata
- created_at
- updated_at

## document_versions

A historical version of a document. This prevents later change detection from
overwriting the old source.

Key fields:
- id
- document_id
- version_number
- content_hash
- raw_storage_uri
- extracted_text
- parser_version
- created_at

## chunks

A retrievable passage with provenance.

Key fields:
- id
- document_version_id
- ordinal
- text
- token_count
- page_start
- page_end
- section_path
- embedding
- content_hash

## query_runs

A complete audit record for a question-answering attempt.

Key fields:
- id
- trace_id
- user_query
- retrieval_config_version
- prompt_version
- model_name
- status
- confidence
- latency_ms
- token counts
- estimated cost
- final answer
- created_at

## query_citations

Links a query claim to a retrieved chunk.

Key fields:
- query_run_id
- chunk_id
- claim_index
- retrieval_rank
- similarity_score
- reranker_score

## review_tasks

A human-review work item created when the quality gate fails.

Key fields:
- id
- query_run_id
- reason_codes
- evidence_summary
- status
- created_at
- resolved_at
