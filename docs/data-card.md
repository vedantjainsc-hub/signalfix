# Data Card

## Dataset A: CFPB Consumer Complaint Database

**Purpose:** Real external market signal and evaluation labels.

**Official sources:**

- https://www.consumerfinance.gov/data-research/consumer-complaints/
- https://www.consumerfinance.gov/complaint/data-use/
- https://cfpb.github.io/ccdb5-api/documentation/

**Initial reproducible slice:**

- Product: `Credit card`
- Received on or after: `2024-01-01`
- Received before: `2025-01-01`
- Narrative present: `true`
- Hosted demo maximum: 5,000 sampled records

**Fields used:** complaint ID, received date, product, sub-product, issue, sub-issue, narrative where published, response category, timely-response flag, state at reduced granularity, and source lineage.

**Important limitations:**

- The CFPB states that the database is not a statistical sample of consumer experiences.
- Complaint counts should not be interpreted as customer incident rates.
- Company comparisons require exposure or market-share context that this prototype does not have.
- Narratives are published only when consumers opt in; the CFPB says it takes reasonable steps to scrub personal information.
- SignalFix applies an additional privacy/quality gate and does not display full ZIP codes.

## Dataset B: Northstar Bank synthetic service cases

**Purpose:** Demonstrate internal operational corroboration, ownership, costs, and remediation workflow without confidential data.

**Generation rules:**

- Reproducible random seed.
- Synthetic text generated from original templates, not copied CFPB narratives.
- No real customers, accounts, employees, or companies.
- Fields include case date, channel, process stage, handle time, repeat-contact flag, escalation flag, SLA breach, cost estimate, and fictional process owner.
- Statistical recipe and seed version will be committed.

## Separation policy

Every row and every UI evidence card carries a `source` field:

- `cfpb` = real public external signal
- `northstar_synthetic` = fictional internal signal

The application never silently merges or relabels the two sources.

## Reproducibility

Every ingestion/generation run records query parameters, row count, run time, snapshot hash, schema version, and source metadata. Unit tests use small committed fixtures rather than remote data.
