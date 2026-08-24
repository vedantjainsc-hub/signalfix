# Limitations and Safety Boundaries

## Interpretation

1. CFPB complaints are observed signals, not a representative sample.
2. Raw complaint counts do not establish customer prevalence, company quality, or causality.
3. External signal must be corroborated by internal data before receiving a high remediation priority.
4. The deployed showcase uses synthetic Northstar economics; projected ROI is not demonstrated client savings.

## AI boundaries

- AI may classify ambiguous language and draft plain-language explanations under a typed schema.
- AI may not invent evidence, costs, owners, customer counts, legal conclusions, or impact values.
- Low-confidence records are labeled `unknown` or `needs_review`.
- Evidence spans must be exact substrings of source text.

## Privacy

- Public narratives receive a second-pass privacy check.
- Suspicious records are quarantined, not shown or embedded.
- Full ZIP codes are not shown in the product.
- The fixed reviewer dataset is inspected before deployment.

## Clustering

Unsupervised clusters can be unstable or semantically incoherent. A Week 1 feasibility gate determines whether clustering remains in the MVP. The fallback is a controlled taxonomy plus deterministic issue/sub-issue and weekly trend analysis.

## Decision support

SignalFix recommends a bounded investigation or pilot. A human approves, rejects, or requests more evidence. It does not autonomously change a customer-facing process.
