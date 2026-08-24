# Architecture

## Product flow

```mermaid
flowchart TD
    A[Real CFPB complaint API] --> C[Ingestion and snapshot]
    B[Synthetic Northstar cases] --> C
    C --> D{Schema and privacy checks pass?}
    D -- No --> E[Quarantine with reason]
    D -- Yes --> F[Complaint classification]
    F --> G[Controlled taxonomy and failure modes]
    G --> H[Deterministic weekly trend detection]
    H --> I[Representative evidence]
    I --> J{Internal corroboration?}
    J -- No --> K[Monitor or request evidence]
    J -- Yes --> L[Controlled remediation playbook]
    L --> M[Transparent priority ranking]
    M --> N[Human review]
    N -- Reject --> O[Record rationale]
    N -- Request evidence --> I
    N -- Approve --> P[30/60/90-day pilot]
    P --> Q[Audit versions assumptions and KPIs]
    Q --> R[Measure outcome]
```

## Technical boundaries

- **Next.js web application:** five reviewer-facing screens.
- **FastAPI service:** typed APIs and workflow orchestration.
- **PostgreSQL:** normalized complaints, model runs, signals, plans, and audit events.
- **Model boundary:** structured classification under a controlled taxonomy.
- **MVP decision:** unsupervised clustering failed the feasibility gate; deterministic taxonomy trends replace it.
- **Deterministic boundary:** validation, privacy rules, trend calculations, ranking, state transitions, and audit writes.
- **Demo reliability:** fixed snapshot and precomputed seeded run; live refresh is optional.

## Required lineage

Every derived object retains its data snapshot, algorithm/model version, taxonomy version, and upstream IDs. Every mutation records an audit event in the same transaction.
