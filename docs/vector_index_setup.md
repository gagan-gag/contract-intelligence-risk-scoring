# Local Vector Index Setup and Week 1 Demo

This guide documents the local Chroma vector index used by the Contract Intelligence & Risk Scoring backend. It covers installation, initialization, development reset, and evidence collection for the Week 1 vector workflow.

The local setup is filesystem-backed and does not require Chroma Cloud credentials.

## 1. Architecture and Defaults

The vector workflow is split across these modules:

| Responsibility | Module |
| --- | --- |
| Application paths and settings | `backend/app/config.py` |
| Persistent Chroma client and collection factory | `backend/app/vector/client.py` |
| Chroma lifecycle, upsert, and semantic search | `backend/app/vector/chroma_adapter.py` |
| Sentence-transformer embedding adapter | `backend/app/vector/embeddings.py` |
| Chunk metadata validation and Chroma flattening | `backend/app/vector/schemas.py` |
| Automated vector tests | `backend/tests/` and `tests/` |

By default, Chroma persists to:

```text
backend/chroma_db/
```

This path comes from `Settings.chroma_persist_dir`. A custom path can be passed to `create_chroma_client()` or `ChromaAdapter()` for tests and isolated development runs.

## 2. Prerequisites

Use Python 3.11 and run commands from the repository root:

```bash
cd /workspaces/contract-intelligence-risk-scoring
python3.11 --version
```

Create and activate a virtual environment if one is not already active:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the repository dependencies:

```bash
python -m pip install -r requirements.txt
```

Chroma is included in `requirements.txt`. The `EmbeddingAdapter` loads `sentence-transformers` lazily, so install it separately when running a live embedding demo:

```bash
python -m pip install sentence-transformers
```

The first live embedding run may download the configured model. The default model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Override it with an environment variable when needed:

```bash
export VECTOR_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 3. Initialize the Local Index

### 3.1 Create the client and collection

The client factory creates the persistence directory automatically. A collection is created on first use and reused on subsequent calls:

```python
from backend.app.vector.client import (
    create_chroma_client,
    get_or_create_collection,
)

client = create_chroma_client()
collection = get_or_create_collection(
    client,
    collection_name="contract_chunks",
    metadata={
        "description": "Contract chunks for semantic retrieval",
        "environment": "local",
    },
)

print(f"persisted at: {client}")
print(f"collection: {collection.name}")
print(f"records: {collection.count()}")
```

A convenient shell smoke check is:

```bash
python - <<'PY'
from backend.app.vector.client import create_chroma_client, get_or_create_collection
from backend.app.config import get_settings

settings = get_settings()
client = create_chroma_client()
collection = get_or_create_collection(client, "contract_chunks")
print(f"persist_directory={settings.chroma_persist_dir}")
print(f"collection={collection.name}")
print(f"count={collection.count()}")
PY
```

Expected behavior:

- The `backend/chroma_db/` directory exists after the command.
- The `contract_chunks` collection exists.
- The initial count is `0`, unless the collection already contains data.
- Running the command again reuses the same collection and data.

### 3.2 Prepare validated chunk metadata

Every chunk should be validated with `VectorChunkMetadata` before storage. The model requires stable `document_id` and `chunk_id` values, page information, clause classification, source offsets, provenance, and a document hash.

```python
from datetime import datetime, timezone

from backend.app.vector.schemas import (
    CharOffset,
    ClauseLabel,
    ExtractionMethod,
    PageRange,
    VectorChunkMetadata,
)

chunk_metadata = VectorChunkMetadata(
    document_id="demo-contract-0001",
    chunk_id="demo-chunk-000001",
    page_number=1,
    page_range=PageRange(start=1, end=1),
    char_offset=CharOffset(start_char=0, end_char=72),
    text_offset=CharOffset(start_char=0, end_char=72),
    clause_label=ClauseLabel.CONFIDENTIALITY,
    confidence_score=0.95,
    chunk_text_length=72,
    document_hash="a" * 64,
    ingested_at=datetime.now(timezone.utc),
    extraction_method=ExtractionMethod.PDF_TEXT_EXTRACTION,
)
```

`to_chroma_metadata()` flattens nested page and offset objects. The adapter removes optional `None` values and converts quality flags to scalar storage values because Chroma metadata values must be scalar-compatible.

### 3.3 Generate embeddings and upsert chunks

Use the same embedding model for ingestion and querying. The embedding adapter supports both a single string and a batch of strings:

```python
from backend.app.vector.embeddings import EmbeddingAdapter
from backend.app.vector.chroma_adapter import ChromaAdapter

text_chunks = [
    "The receiving party shall protect confidential information.",
]
embedding_adapter = EmbeddingAdapter()
embeddings = embedding_adapter.encode(text_chunks)

adapter = ChromaAdapter()
ids = adapter.upsert_chunks(
    collection,
    text_chunks,
    embeddings,
    [chunk_metadata],
)
print(ids)
```

`upsert_chunks()` uses each metadata object's `chunk_id` as the Chroma ID. Repeating the operation with the same IDs replaces the records rather than creating duplicates.

## 4. Semantic Query

Encode the input query with the same embedding adapter, then call `semantic_search()`:

```python
results = adapter.semantic_search(
    collection,
    "confidentiality obligations",
    embedding_adapter,
    top_k=5,
    where={"document_id": "demo-contract-0001"},
)

for chunk_id, document, metadata, distance in zip(
    results["ids"][0],
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0],
):
    print(chunk_id, distance, metadata["clause_label"])
    print(document)
```

Notes:

- `top_k` controls the maximum number of nearest chunks returned.
- `where` is optional and uses Chroma metadata filters, for example filtering by `document_id` or `clause_label`.
- Chroma returns result fields grouped by query. For one query, the relevant result lists are at index `0`.
- Lower distance means a closer vector match for the collection's configured distance metric.
- Query and indexed embeddings must have the same dimension and should come from the same model.

## 5. Development Reset Procedure

Reset is destructive. Stop the FastAPI process and any scripts using the local database before deleting data.

### 5.1 Wipe the complete local database

From the repository root, this removes every local collection and all persisted vectors:

```bash
rm -rf backend/chroma_db
```

Recreate the empty database and default collection:

```bash
python - <<'PY'
from backend.app.vector.client import create_chroma_client, get_or_create_collection

client = create_chroma_client()
collection = get_or_create_collection(client, "contract_chunks")
print(f"reinitialized collection={collection.name} count={collection.count()}")
PY
```

Expected output includes `count=0`.

### 5.2 Delete one collection and preserve others

Use the Chroma client API when only one collection should be reset:

```bash
python - <<'PY'
from backend.app.vector.client import create_chroma_client

collection_name = "contract_chunks"
client = create_chroma_client()

try:
    client.delete_collection(name=collection_name)
    print(f"deleted collection={collection_name}")
except ValueError:
    print(f"collection did not exist={collection_name}")
PY
```

Recreate it when needed:

```bash
python - <<'PY'
from backend.app.vector.client import create_chroma_client, get_or_create_collection

client = create_chroma_client()
collection = get_or_create_collection(client, "contract_chunks")
print(f"collection={collection.name} count={collection.count()}")
PY
```

Do not run the full-directory deletion in an environment containing data that must be retained. The local `backend/chroma_db/` directory is development state, not a backup.

## 6. Week 1 Demo Evidence Template

Use this section as the handoff record for the Week 1 demonstration. Replace bracketed values with the actual run details and attach terminal output or screenshots where appropriate.

### Environment record

- Date: `[YYYY-MM-DD]`
- Branch/commit: `[branch and short SHA]`
- Python: `[output of python --version]`
- Chroma package: `[output of python -m pip show chromadb]`
- Embedding model: `[VECTOR_EMBEDDING_MODEL or default model]`
- Persist directory: `[backend/chroma_db or custom path]`
- Collection name: `[contract_chunks]`

### Verification checklist

| Area | Command or action | Expected evidence | Result |
| --- | --- | --- | --- |
| Dependencies | `python -m pip install -r requirements.txt` | Installation completes successfully | `[ ]` |
| Chroma setup | Run the initialization smoke check in Section 3.1 | Collection exists and reports a count | `[ ]` |
| Embedding adapter | `pytest -q backend/tests/test_embeddings.py` | Both single-text and batch embedding tests pass | `[ ]` |
| Upsert | `pytest -q backend/tests/test_upsert.py` | Chunks and metadata are stored; repeated IDs keep the count unchanged | `[ ]` |
| Semantic query | `pytest -q backend/tests/test_semantic_query.py` | Relevant fixture chunk is ranked first with expected metadata | `[ ]` |
| Full regression | `pytest -q` | Entire suite passes | `[ ]` |

### Live end-to-end evidence

For a live demo, record the output of these stages in order:

1. **Embedding:** show that `EmbeddingAdapter.encode()` returns a non-empty numeric vector and record its dimension.
2. **Upsert:** show the IDs returned by `upsert_chunks()` and the collection count after insertion.
3. **Idempotency:** run the same upsert again and show that the count does not increase.
4. **Query:** submit a natural-language query using the same embedding adapter and show the top result ID, distance, document text, clause label, page, and source offsets.
5. **Filtering:** repeat the query with `where={"document_id": "..."}` and show that only the requested document's chunks are returned.

Suggested evidence capture:

```text
[Embedding]
model=[...]
dimension=[...]
vector_preview=[...]

[Upsert]
ids=[...]
count_after_first_upsert=[...]
count_after_retry=[...]

[Semantic query]
query=[...]
top_k=[...]
filter=[...]
top_chunk_id=[...]
distance=[...]
clause_label=[...]
page_number=[...]
char_offset=[start, end]
```

### Acceptance criteria

The Week 1 vector demo is complete when all of the following are true:

- The local Chroma client initializes without cloud credentials.
- The embedding adapter produces vectors successfully.
- Chunks are upserted with stable IDs and flattened metadata.
- Retrying an upsert with the same IDs does not increase the collection count.
- A query about a known clause retrieves the expected fixture chunk in the top results.
- Returned metadata includes at least `document_id`, `chunk_id`, `page_number`, `clause_label`, and source offsets.
- A basic `document_id` filter limits results to the requested contract.
- The automated test suite passes.

## 7. Troubleshooting

### `chromadb is not installed`

Activate the expected virtual environment and install the requirements:

```bash
python -m pip install -r requirements.txt
```

### `sentence-transformers is not installed`

Install the optional live embedding dependency:

```bash
python -m pip install sentence-transformers
```

### Model download or network failure

The first live embedding run may require network access to download the model. Use the deterministic unit tests for offline verification; they mock the embedding model and do not require a model download.

### Collection already contains unexpected records

Check the count and collection name. For disposable development data, use the reset procedure in Section 5. Avoid deleting `backend/chroma_db/` if the data is needed for another local workflow.

### Query returns no results

Confirm that:

- The collection contains records (`collection.count()`).
- The query embedding was generated by the same model and has the same dimension as stored embeddings.
- The `where` filter uses metadata keys and scalar values that were actually stored.
- `top_k` is at least `1`.
