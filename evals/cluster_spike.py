"""Feasibility spike for narrow complaint clusters.

This is an exploratory evaluation, not production pipeline code. It downloads a
bounded CFPB sample in memory, applies the same privacy screen as the product,
and compares HDBSCAN settings over TF-IDF/SVD vectors.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import hdbscan
import httpx
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import Normalizer

API_DIR = Path(__file__).resolve().parents[1] / "services" / "api"
sys.path.insert(0, str(API_DIR))

from app.privacy.scrubber import screen_narrative

CFPB_API_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
USER_AGENT = "SignalFix research prototype (GitHub: vedantjainsc-hub/signalfix)"


def fetch_sample(
    sample_size: int = 1_000,
    page_size: int = 100,
    issue: str | None = None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    search_after: str | None = None
    with httpx.Client(timeout=60, headers={"User-Agent": USER_AGENT}) as client:
        for page_number, offset in enumerate(range(0, sample_size, page_size), start=1):
            params: dict[str, Any] = {
                "product": "Credit card",
                "has_narrative": "true",
                "date_received_min": "2024-01-01",
                "date_received_max": "2025-01-01",
                "size": min(page_size, sample_size - offset),
                "frm": offset,
                "page": page_number,
                "sort": "created_date_asc",
                "no_aggs": "true",
            }
            if issue:
                params["issue"] = issue
            if search_after:
                params["search_after"] = search_after
            response = client.get(CFPB_API_URL, params=params)
            response.raise_for_status()
            payload = response.json()
            hits = payload["hits"]["hits"]
            if not hits:
                break
            records.extend(hit["_source"] for hit in hits)
            sort_value, complaint_id = hits[-1]["sort"]
            search_after = f"{sort_value}_{complaint_id}"

    complaint_ids = [str(record["complaint_id"]) for record in records]
    if len(set(complaint_ids)) != len(complaint_ids):
        raise RuntimeError("CFPB pagination returned duplicate complaint IDs")
    return records


def prepare(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    accepted: list[dict[str, Any]] = []
    texts: list[str] = []
    for record in records:
        result = screen_narrative(record.get("complaint_what_happened", ""))
        if result.status == "quarantined" or not result.sanitized_text:
            continue
        accepted.append(record)
        cleaned = re.sub(r"\b(?:x{2,}|\d+)\b", " ", result.sanitized_text, flags=re.IGNORECASE)
        texts.append(re.sub(r"\s+", " ", cleaned).strip())
    return accepted, texts


def top_terms(
    matrix: Any, labels: np.ndarray, feature_names: np.ndarray, label: int, limit: int = 8
) -> list[str]:
    indices = np.flatnonzero(labels == label)
    centroid = np.asarray(matrix[indices].mean(axis=0)).ravel()
    return feature_names[np.argsort(centroid)[-limit:][::-1]].tolist()


def evaluate_setting(
    vectors: np.ndarray,
    labels: np.ndarray,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    clustered = labels >= 0
    cluster_labels = sorted(set(labels[clustered].tolist()))
    noise_fraction = float((labels == -1).mean())
    silhouette = None
    if len(cluster_labels) > 1 and clustered.sum() > len(cluster_labels):
        silhouette = float(silhouette_score(vectors[clustered], labels[clustered]))

    weighted_purity_numerator = 0.0
    clustered_count = int(clustered.sum())
    for label in cluster_labels:
        indices = np.flatnonzero(labels == label)
        subissues = [records[index].get("sub_issue") or "unknown" for index in indices]
        weighted_purity_numerator += Counter(subissues).most_common(1)[0][1]
    weighted_subissue_purity = (
        weighted_purity_numerator / clustered_count if clustered_count else None
    )

    return {
        "cluster_count": len(cluster_labels),
        "noise_fraction": round(noise_fraction, 4),
        "silhouette": round(silhouette, 4) if silhouette is not None else None,
        "weighted_subissue_purity": (
            round(weighted_subissue_purity, 4)
            if weighted_subissue_purity is not None
            else None
        ),
    }


def run() -> dict[str, Any]:
    issue_filter = "Problem with a purchase shown on your statement"
    raw_records = fetch_sample(issue=issue_filter)
    records, texts = prepare(raw_records)
    if len(records) < 300:
        raise RuntimeError(f"Too few records passed privacy screening: {len(records)}")

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.9,
        max_features=8_000,
        sublinear_tf=True,
    )
    tfidf = vectorizer.fit_transform(texts)
    components = min(75, tfidf.shape[1] - 1, tfidf.shape[0] - 1)
    vectors = TruncatedSVD(n_components=components, random_state=42).fit_transform(tfidf)
    vectors = Normalizer(copy=False).fit_transform(vectors)

    settings: list[dict[str, Any]] = []
    candidates: list[tuple[float, np.ndarray, dict[str, Any]]] = []
    for min_cluster_size in (15, 25, 40):
        for min_samples in (5, 10):
            labels = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                metric="euclidean",
                cluster_selection_method="eom",
            ).fit_predict(vectors)
            metrics = evaluate_setting(vectors, labels, records)
            setting = {
                "min_cluster_size": min_cluster_size,
                "min_samples": min_samples,
                **metrics,
            }
            settings.append(setting)
            cluster_count = metrics["cluster_count"]
            silhouette = metrics["silhouette"] or -1.0
            acceptable = 3 <= cluster_count <= 20 and metrics["noise_fraction"] <= 0.65
            score = silhouette - metrics["noise_fraction"] * 0.2 if acceptable else -10.0
            candidates.append((score, labels, setting))

    _, best_labels, best_setting = max(candidates, key=lambda item: item[0])
    feature_names = vectorizer.get_feature_names_out()
    cluster_summaries: list[dict[str, Any]] = []
    for label in sorted(set(best_labels.tolist()) - {-1}):
        indices = np.flatnonzero(best_labels == label)
        subissues = Counter(records[index].get("sub_issue") or "unknown" for index in indices)
        cluster_summaries.append(
            {
                "cluster": int(label),
                "size": len(indices),
                "top_terms": top_terms(tfidf, best_labels, feature_names, label),
                "top_subissues": subissues.most_common(3),
                "representative_complaint_ids": [
                    str(records[index]["complaint_id"]) for index in indices[:3]
                ],
            }
        )
    cluster_summaries.sort(key=lambda cluster: cluster["size"], reverse=True)

    gate_passed = (
        3 <= best_setting["cluster_count"] <= 20
        and best_setting["noise_fraction"] <= 0.65
        and (best_setting["silhouette"] or 0) >= 0.15
    )
    return {
        "source": "CFPB Consumer Complaint Database API",
        "query": {
            "product": "Credit card",
            "has_narrative": True,
            "date_received_min": "2024-01-01",
            "date_received_max": "2025-01-01",
            "issue": issue_filter,
            "sample_size": 1_000,
            "sort": "created_date_asc",
        },
        "downloaded_records": len(raw_records),
        "privacy_accepted_records": len(records),
        "privacy_quarantined_records": len(raw_records) - len(records),
        "representation": {
            "method": "TF-IDF 1-2 grams -> 75D TruncatedSVD -> L2 normalize",
            "features": int(tfidf.shape[1]),
        },
        "settings": settings,
        "selected_setting": best_setting,
        "gate": {
            "passed": gate_passed,
            "criteria": {
                "cluster_count": "3 to 20",
                "noise_fraction": "<= 0.65",
                "silhouette": ">= 0.15",
            },
            "decision": (
                "Proceed to human coherence review; do not ship clusters yet."
                if gate_passed
                else "Use supervised taxonomy and deterministic trends for the MVP."
            ),
        },
        "largest_clusters": cluster_summaries[:10],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
