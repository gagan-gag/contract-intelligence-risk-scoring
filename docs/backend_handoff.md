# Backend Handoff: Vector Search and Chroma

**Project:** Contract Intelligence & Risk Scoring (NLP)  
**Day:** 14  
**Runtime:** Python 3.11, FastAPI, local persistent Chroma

This document is the implementation handoff for running the backend locally,
initializing the vector index, and calling the currently available API. The
current branch exposes health and search over HTTP. Vector collection creation
and chunk ingestion are Python library operations; an HTTP ingestion endpoint
has not been registered yet.

## 1. Quick Start

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

export VECTOR_COLLECTION_NAME=contract_chunks
export VECTOR_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

uvicorn backend.app.main:app --reload
```

Verify the service:

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{"status":"ok"}
```

Interactive API documentation is available at
`http://127.0.0.1:8000/docs` while the server is running.

## 2. HTTP API

### `GET /health`

Returns a simple service readiness response. This endpoint does not verify that
the embedding model has loaded or that the Chroma collection contains data.

```bash
curl --fail http://127.0.0.1:8000/health
```

```json
{"status":"ok"}
```

### `GET /search`

Searches the configured Chroma collection using a sentence-transformers query
embedding.

Query parameters:

| Parameter | Required | Default | Constraints | Description |
| --- | --- | --- | --- | --- |
| `query` | yes | none | 1-2000 characters | Natural-language search text |
| `top_k` | no | `5` | 1-100 | Maximum number of results |
| `document_id` | no | none | 16-36 allowed characters | Restrict results to one contract |
| `clause_label` | no | none | Day 2 `ClauseLabel` value | Restrict results by clause type |

Example: broad semantic search

```bash
curl --get 'http://127.0.0.1:8000/search' \
  --data-urlencode 'query=What obligations protect confidential information?' \
  --data-urlencode 'top_k=3'
```

Example: filtered search

```bash
curl --get 'http://127.0.0.1:8000/search' \
  --data-urlencode 'query=What limits or exclusions apply to liability?' \
  --data-urlencode 'top_k=5' \
  --data-urlencode 'document_id=contract-2024-000001' \
  --data-urlencode 'clause_label=liability'
```

Successful response:

```json
{
  "query": "What obligations protect confidential information?",
  "top_k": 3,
  "results": [
    {
      "chunk_id": "contract-2024-000001-chunk-004",
      "document_id": "contract-2024-000001",
      "chunk_text": "The receiving party shall protect confidential information...",
      "distance": 0.1842,
      "metadata": {
        "document_id": "contract-2024-000001",
        "chunk_id": "contract-2024-000001-chunk-004",
        "clause_label": "confidentiality",
        "page_number": 4,
        "char_offset_start": 800,
        "char_offset_end": 875
      }
    }
  ]
}
```

`distance` is a Chroma distance; lower values indicate greater similarity.
The API returns an empty `results` array when the collection has no matching
chunks. Invalid query parameters return FastAPI validation errors with HTTP
status `422`.

## 3. Local Chroma Collection Setup

### Default storage and collection

- Persistent database directory: `backend/chroma_db`
- Default collection: `contract_chunks`
- Override the collection with `VECTOR_COLLECTION_NAME`
- No Chroma Cloud account, API key, or external service is required

The search dependency creates the directory and gets or creates the configured
collection on the first request. For explicit initialization, use the client
factory:

```python
from backend.app.vector.client import (
    create_chroma_client,
    get_or_create_collection,
)

client = create_chroma_client()  # uses Settings.chroma_persist_dir
collection = get_or_create_collection(client, "contract_chunks")
print(collection.name, collection.count())
```

For an isolated smoke-test collection:

```python
from backend.app.vector.client import create_chroma_client, get_or_create_test_collection

client = create_chroma_client("backend/chroma_db")
collection = get_or_create_test_collection(client)
print(collection.name)
```

The helper is idempotent: calling it again with the same client and name returns
the existing collection rather than creating a duplicate.

### Add a vector chunk

Chunks must have matching IDs, documents, embeddings, and metadata. The
production adapter accepts validated `VectorChunkMetadata` objects and flattens
them to Chroma-compatible scalar metadata:

```python
from backend.app.vector.chroma_adapter import ChromaAdapter
from backend.app.vector.client import create_chroma_client, get_or_create_collection

client = create_chroma_client()
collection = get_or_create_collection(client, "contract_chunks")

collection.upsert(
    ids=["contract-2024-000001-chunk-004"],
    embeddings=[[0.01, 0.02, 0.03]],  # use the configured model's full dimension
    documents=["The receiving party shall protect confidential information."],
    metadatas=[
        {
            "document_id": "contract-2024-000001",
            "chunk_id": "contract-2024-000001-chunk-004",
            "clause_label": "confidentiality",
            "page_number": 4,
            "char_offset_start": 800,
            "char_offset_end": 875,
        }
    ],
)
```

For validated production ingestion, use `ChromaAdapter.upsert_chunks()` with
`VectorChunkMetadata` instances. Reusing a chunk ID is an idempotent upsert.
Embeddings stored in a collection must all have the same dimension as query
embeddings.

### Generate embeddings before ingestion

```python
from backend.app.vector.embeddings import EmbeddingAdapter

embedder = EmbeddingAdapter()
texts = [
    "The receiving party shall protect confidential information.",
    "The customer shall pay invoices within thirty days.",
]
embeddings = embedder.encode(texts)
```

`EmbeddingAdapter.encode()` returns one `list[float]` for a string and one
`list[list[float]]` for a sequence of strings. The default
`all-MiniLM-L6-v2` model produces 384-dimensional vectors. Confirm dimensions
when changing models before reusing an existing collection.

## 4. Configuration and Dependencies

### Python packages

Install the pinned and minimum dependencies from [requirements.txt](../requirements.txt):

- `fastapi==0.115.6`: HTTP API and request validation
- `uvicorn[standard]==0.34.0`: local ASGI server
- `httpx==0.28.1`: FastAPI test client support
- `pytest==8.3.4`: test runner
- `chromadb>=0.4.0`: persistent local vector database
- `sentence-transformers>=3.0.0`: local text embedding model

The application is written for Python 3.11. The current CI/container may use a
newer Python version, but team development should standardize on 3.11 for
repeatable dependency resolution.

### Environment variables

| Variable | Default | Used by | Notes |
| --- | --- | --- | --- |
| `VECTOR_COLLECTION_NAME` | `contract_chunks` | Search route | Chroma collection to query |
| `VECTOR_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | `EmbeddingAdapter` | Hugging Face model identifier or local model path |

The first use of a model identifier may download model files and therefore needs
network access. After download, sentence-transformers loads the model locally;
no application cloud key is needed. In restricted environments, pre-download
the model or set `VECTOR_EMBEDDING_MODEL` to an available local model path.

Do not commit secrets or model caches. Chroma data is persisted under
`backend/chroma_db`; treat that directory as local runtime state unless the team
explicitly chooses to version a fixture database.

## 5. Testing and Operations

Run all tests from the repository root:

```bash
pytest -q
```

Run the Day 13 retrieval relevance evaluation against the same local collection:

```bash
python scripts/evaluate_retrieval.py --top-k 3
```

The evaluator reports precision@k and collection-relative recall@k for sample
confidentiality, liability, termination, payment, and governing-law queries.
See [retrieval_evaluation.md](retrieval_evaluation.md) for the gold-label
assumptions and interpretation guidance.

Before handing off a populated index, verify:

1. The collection name and embedding model are the same for ingestion and search.
2. Every stored embedding has the model's expected dimension.
3. Stored metadata includes at least `document_id`, `chunk_id`, and
   `clause_label` for useful filtering and evaluation.
4. The retrieval evaluation has been run against the intended corpus.
5. The service starts and `GET /health` returns HTTP 200.

## 6. Current Scope and Follow-up

The current backend does not expose a POST endpoint for document upload or
chunk ingestion. Ingestion is performed through the Python vector adapter and
Chroma client helpers. A future API layer should validate the same metadata
schema, generate embeddings with the configured model, and call
`ChromaAdapter.upsert_chunks()` while preserving the stable `chunk_id` values.
