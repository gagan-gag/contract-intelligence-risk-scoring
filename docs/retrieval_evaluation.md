# Day 13: Retrieval Relevance Evaluation

## Purpose

This evaluation checks whether the local Chroma vector index returns contract
chunks whose metadata matches the intent of a small documented query set. It
uses the same embedding adapter and `ChromaAdapter.semantic_search` path as the
FastAPI search endpoint.

The evaluation is a lightweight relevance smoke test, not a statistically
representative benchmark. The gold standard is the expected `clause_label` for
each query. A result is relevant when its stored `clause_label` is one of the
query's expected labels.

## Query Set

| Name | Sample query | Expected relevant label |
| --- | --- | --- |
| confidentiality | What obligations protect confidential information? | `confidentiality` |
| liability | What limits or exclusions apply to liability? | `liability` |
| termination | How can the agreement be terminated and with what notice? | `term_termination` |
| payment | When are invoices due and what payment terms apply? | `consideration` |
| governing-law | Which law governs this agreement? | `governing_law` |

These labels follow `ClauseLabel` in `backend/app/vector/schemas.py`. If a
query genuinely spans multiple categories, add more labels to its evaluation
case rather than changing the scoring logic.

## Procedure

Install the project dependencies, ensure the local Chroma collection contains
embedded chunks, and run from the repository root:

```bash
python scripts/evaluate_retrieval.py --top-k 3
```

Useful overrides:

```bash
python scripts/evaluate_retrieval.py \
  --persist-directory backend/chroma_db \
  --collection contract_chunks \
  --top-k 5
```

The model is selected by `VECTOR_EMBEDDING_MODEL`; the collection is selected
by `VECTOR_COLLECTION_NAME`. Neither setting requires a cloud key. The default
model is `sentence-transformers/all-MiniLM-L6-v2`.

## Metrics

For each query, the script reports:

- **Precision@k:** relevant retrieved chunks divided by chunks returned.
- **Recall@k:** relevant retrieved chunks divided by all chunks in the current
  collection carrying an expected label.

Recall is deliberately collection-relative. It describes retrieval over the
loaded local corpus, not recall against documents that have not been indexed.
When the collection is empty, the script reports zero scores and the collection
size makes the missing fixture data visible.

## Findings Template

Record the command output for each indexed corpus revision. Use this table to
track changes in retrieval quality:

| Run/date | Collection size | k | Mean precision@k | Mean recall@k | Observation |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline |  | 3 |  |  |  |

Interpretation guidance:

- High precision with low recall suggests `k` is too small or chunks are too
  granular; inspect missed chunks and consider a larger `k`.
- Low precision suggests embedding ambiguity, noisy chunks, or incorrect clause
  labels; inspect returned text and distances before changing the model.
- Scores of zero with an empty collection indicate missing local test data, not
  an embedding failure.
- Compare scores only when the collection contents, embedding model, and query
  set are held constant.

## Day 13 Baseline Findings

The evaluator is now available, but no fixed score is claimed in this document:
the checked-in local Chroma database may contain a different corpus or no
`contract_chunks` records depending on the environment. Run the command above
against the intended indexed corpus and record its output in the findings table.
