"""Evaluate semantic retrieval against a small documented contract query set.

Run from the repository root:
    python scripts/evaluate_retrieval.py --top-k 3

The evaluator uses the configured local Chroma collection and the same
``ChromaAdapter.semantic_search`` path used by the API. Relevance is defined by
whether a returned chunk's ``clause_label`` matches the labels documented in
``docs/retrieval_evaluation.md``.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Allow direct execution from the repository root without installing the app.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.vector.chroma_adapter import ChromaAdapter
from backend.app.vector.client import create_chroma_client, get_or_create_collection
from backend.app.vector.embeddings import EmbeddingAdapter


@dataclass(frozen=True)
class EvaluationQuery:
    """A natural-language query and its expected relevant clause labels."""

    name: str
    text: str
    relevant_labels: frozenset[str]


EVALUATION_QUERIES = (
    EvaluationQuery(
        "confidentiality",
        "What obligations protect confidential information?",
        frozenset({"confidentiality"}),
    ),
    EvaluationQuery(
        "liability",
        "What limits or exclusions apply to liability?",
        frozenset({"liability"}),
    ),
    EvaluationQuery(
        "termination",
        "How can the agreement be terminated and with what notice?",
        frozenset({"term_termination"}),
    ),
    EvaluationQuery(
        "payment",
        "When are invoices due and what payment terms apply?",
        frozenset({"consideration"}),
    ),
    EvaluationQuery(
        "governing-law",
        "Which law governs this agreement?",
        frozenset({"governing_law"}),
    ),
)


def _labels_in_collection(collection: Any) -> dict[str, int]:
    """Count labeled chunks in the collection for collection-relative recall."""
    records = collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for metadata in records.get("metadatas", []) or []:
        if metadata and metadata.get("clause_label"):
            label = str(metadata["clause_label"])
            counts[label] = counts.get(label, 0) + 1
    return counts


def evaluate_collection(collection: Any, embedding_adapter: Any, top_k: int) -> dict[str, Any]:
    """Run all evaluation queries and return per-query and aggregate metrics.

    Recall is collection-relative: the denominator is the number of chunks in
    the current collection carrying one of the query's expected labels. This
    makes the result honest when only a subset of a contract corpus is loaded.
    """
    label_counts = _labels_in_collection(collection)
    collection_size = collection.count()
    evaluations: list[dict[str, Any]] = []

    for evaluation_query in EVALUATION_QUERIES:
        result_count = min(top_k, collection_size)
        raw_results = (
            ChromaAdapter.semantic_search(
                collection,
                evaluation_query.text,
                embedding_adapter,
                top_k=result_count,
            )
            if result_count
            else {"ids": [[]], "metadatas": [[]], "distances": [[]]}
        )
        ids = raw_results.get("ids", [[]])[0]
        metadatas = raw_results.get("metadatas", [[]])[0]
        retrieved_labels = [
            str(metadata.get("clause_label", "")) if metadata else ""
            for metadata in metadatas
        ]
        relevant_retrieved = sum(
            label in evaluation_query.relevant_labels for label in retrieved_labels
        )
        relevant_in_collection = sum(
            label_counts.get(label, 0) for label in evaluation_query.relevant_labels
        )
        precision = relevant_retrieved / len(ids) if ids else 0.0
        recall = (
            relevant_retrieved / relevant_in_collection if relevant_in_collection else 0.0
        )
        evaluations.append(
            {
                "name": evaluation_query.name,
                "query": evaluation_query.text,
                "expected_labels": sorted(evaluation_query.relevant_labels),
                "retrieved_ids": ids,
                "retrieved_labels": retrieved_labels,
                "precision_at_k": round(precision, 3),
                "recall_at_k": round(recall, 3),
                "relevant_in_collection": relevant_in_collection,
            }
        )

    return {
        "collection_size": collection_size,
        "top_k": top_k,
        "queries": evaluations,
        "mean_precision_at_k": round(
            sum(item["precision_at_k"] for item in evaluations) / len(evaluations), 3
        ),
        "mean_recall_at_k": round(
            sum(item["recall_at_k"] for item in evaluations) / len(evaluations), 3
        ),
    }


def main() -> None:
    """Run the evaluation against the configured local Chroma collection."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-k", type=int, default=3, choices=range(1, 101))
    parser.add_argument(
        "--persist-directory",
        default=None,
        help="Override the local Chroma directory from application settings.",
    )
    parser.add_argument(
        "--collection",
        default=os.getenv("VECTOR_COLLECTION_NAME", "contract_chunks"),
        help="Chroma collection name (default: VECTOR_COLLECTION_NAME or contract_chunks).",
    )
    args = parser.parse_args()

    client = create_chroma_client(persist_directory=args.persist_directory)
    collection = get_or_create_collection(client, args.collection)
    report = evaluate_collection(collection, EmbeddingAdapter(), args.top_k)

    print(f"Collection: {args.collection} ({report['collection_size']} chunks)")
    print(f"Precision@{args.top_k}: {report['mean_precision_at_k']:.3f}")
    print(f"Recall@{args.top_k}:    {report['mean_recall_at_k']:.3f}")
    for item in report["queries"]:
        print(
            f"{item['name']}: precision={item['precision_at_k']:.3f}, "
            f"recall={item['recall_at_k']:.3f}, ids={item['retrieved_ids']}"
        )


if __name__ == "__main__":
    main()
