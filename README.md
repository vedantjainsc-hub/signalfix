# SignalFix

**Turn complaint signals into approved fixes.**

SignalFix is an AI-assisted decision workflow for customer-operations teams. It combines real public CFPB complaint signals with clearly labeled synthetic internal service data for a fictional bank, then moves an issue through classification, trend detection, evidence review, remediation ranking, human approval, and an auditable decision log.

> Status: Week 1 foundation complete. The first clustering spike failed its quality gate, so the MVP now uses a controlled taxonomy and deterministic trends.

## The problem

Complaint analytics often stops at dashboards, summaries, or chat. Operations leaders still need to decide:

- What changed?
- Is the signal credible?
- Does it appear in our own operations?
- What action should we test?
- Who approved it and why?
- Did the intervention work?

SignalFix is designed around that full decision loop.

## Data boundary

- **Real external signal:** public CFPB Consumer Complaint Database records.
- **Synthetic internal signal:** fictional Northstar Bank service cases, costs, owners, and operating assumptions.
- **No claim of prevalence:** CFPB complaints are not a statistical sample of all consumer experiences.
- **No automated consumer decisions:** SignalFix is an internal investigation and remediation aid.

See [`docs/data-card.md`](docs/data-card.md) and [`docs/limitations.md`](docs/limitations.md).

## Planned user flow

```text
Ingest → Validate/Privacy Check → Classify → Cluster/Detect
      → Show Evidence → Map Remediations → Rank → Human Approval
      → Audit → Measure Outcome
```

## Repository structure

```text
docs/          Product, data, architecture, evaluation, and limitations
services/api/  Python/FastAPI ingestion and decision pipeline
apps/web/      Next.js reviewer-facing product
data/          Small test fixtures and documented seed inputs
evals/         Reproducible model and workflow evaluations
```

## Build principles

1. Evidence is selected from sources, never invented.
2. Deterministic code handles trends, scores, and workflow state.
3. AI handles ambiguous language under typed schemas and can abstain.
4. Real and synthetic data remain visibly separate.
5. Every consequential mutation creates an audit event.
6. A simpler supervised fallback beats incoherent clustering.

## Official data sources

- [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/)
- [CFPB complaint data-use explanation](https://www.consumerfinance.gov/complaint/data-use/)
- [CFPB API documentation](https://cfpb.github.io/ccdb5-api/documentation/)

## License

MIT for project code. Source datasets retain their own terms and attribution; see the data card.
