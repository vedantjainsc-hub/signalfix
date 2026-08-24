# SignalFix Data

This repository does not commit the complete CFPB complaint download or generated production-size datasets.

## Real public source

The ingestion client requests a bounded CFPB API slice and records a deterministic snapshot manifest. Unit tests use small inline fixtures so CI does not depend on a government API.

## Northstar synthetic source

`services/api/app/ingestion/synthetic_generator.py` produces fictional credit-card service cases using:

- an explicit random seed;
- bounded dates;
- original narrative templates;
- documented process stages and failure modes;
- synthetic handle times, repeat contacts, escalations, SLA breaches, costs, and owners;
- an optional, declared surge used to test whether trend detection can find an emerging internal signal.

The generator never copies or relabels CFPB narratives. `northstar_synthetic` is retained as the source on every case.
