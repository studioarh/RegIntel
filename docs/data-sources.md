# Data Sources

## Initial domain

UK consumer-credit regulatory intelligence.

## Allowed publishers

- Financial Conduct Authority (FCA)
- UK Government / GOV.UK
- Legislation.gov.uk

## Initial corpus

The planned source corpus is recorded in `config/source_manifest.csv`.

The Week 2 initial ingestion target is 50–100 documents. The first ingestion
batch will use high-priority sources, then add medium-priority sources after
parser, metadata, chunking, and retrieval checks pass.

## Evidence hierarchy

1. Current legislation and FCA Handbook instruments or rules.
2. FCA policy statements and finalised guidance.
3. FCA consultations, clearly labelled as proposals.
4. FCA supervisory publications, Dear CEO letters, and regulatory-priority reports.
5. GOV.UK policy announcements and press releases, clearly labelled as policy context.
6. Discovery pages, used only to locate primary documents and not as evidence for
   substantive regulatory claims.

## Exclusions

- Commercial law-firm summaries as answer evidence.
- Unverified third-party commentary.
- Social-media content.
- Documents outside the approved publisher allow-list.
- Pages that cannot be retrieved or whose publisher cannot be verified.