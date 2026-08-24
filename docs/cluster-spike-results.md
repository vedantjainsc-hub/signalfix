# Complaint-Clustering Feasibility Spike

## Decision

**Do not ship unsupervised HDBSCAN clustering in the MVP.** Use the controlled complaint taxonomy plus deterministic weekly trend detection. Keep clustering as a later research track after entity masking, stronger embeddings, and a human-labeled coherence set exist.

## What was tested

- Source: CFPB Consumer Complaint Database API
- Period: 2024
- Product: Credit card
- Narrative required: yes
- Final test scope: 1,000 unique complaints within `Problem with a purchase shown on your statement`
- Privacy screen: 1,000 accepted, 0 quarantined
- Representation: TF-IDF 1–2 grams, 75-dimensional TruncatedSVD, L2 normalization
- Clusterer: HDBSCAN parameter grid

The final spike first removes common CFPB redaction placeholders and numbers. It also uses `search_after` pagination and verifies complaint IDs are unique.

## Final result

Selected quantitative result:

| Metric | Result | Gate |
|---|---:|---:|
| Clusters | 2 | 3–20 |
| Noise | 88.5% | ≤65% |
| Silhouette | 0.1109 | ≥0.15 |
| Gate | **Failed** | All criteria required |

The two surviving clusters were dominated by company names such as Wells Fargo and American Express rather than distinct process failure modes. That is not the product behavior we need.

## Quality-control lesson

An initial exploratory run appeared to pass because offset-only API pagination returned overlapping records. The script now uses the CFPB `search_after` cursor, records the page position, and fails if duplicate complaint IDs appear. After correcting pagination, global clusters were broad and low-purity. A second, more faithful test constrained records to one issue family and removed placeholder tokens; it still failed because clusters captured entities, not remediation-relevant failure modes.

This is why the feasibility gate existed. The spike prevented a visually impressive but misleading feature from entering the product.

## MVP replacement

1. Map CFPB issue/sub-issue to a small process-stage taxonomy.
2. Use structured classification to identify failure mode and harm type.
3. Require exact evidence spans and allow abstention.
4. Detect trends at issue, sub-issue, process-stage, and failure-mode level.
5. Show representative and counter-evidence within those controlled groups.

## Future clustering research

Reconsider only after:

- organization and merchant entity masking;
- sentence embeddings tuned for complaint semantics;
- clustering within a validated process/failure bucket;
- a human-labeled coherence and distinctiveness set;
- stability testing across samples and time windows;
- an explicit outlier/abstention policy.

The reproducible script is `evals/cluster_spike.py`; machine-readable results are in `evals/cluster_spike_results.json`.
