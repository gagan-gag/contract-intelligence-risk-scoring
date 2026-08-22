# Day 13 - Integration Handoff Log

## M4 (Vector/Search) - backend-vector-api branch
Status: Integrated and passing.

Issues found during integration:
1. Import convention mismatch: multiple app and test files used absolute
   imports rooted at repo root (`from backend.app....`) instead of the
   project's established convention (`from app....` with PYTHONPATH=backend).
   Fixed in: main.py, routers/search.py, vector/chroma_adapter.py,
   vector/client.py, vector/store.py, tests/test_store.py,
   tests/test_search_router.py, tests/test_upsert.py.

2. Missing dependencies not present in requirements.txt: chromadb, numpy,
   sentence-transformers. Installed and added to requirements.txt.

3. Silent dependency-override failure in test_search_router.py: the test
   imported `app`, `search router`, and vector client helpers via
   `backend.app....` while the actual application used `app....`. Since
   Python treated these as separate module instances, FastAPI's
   dependency_overrides silently failed to match, causing the test to
   fall through to the real sentence-transformers model (triggering a
   live Hugging Face Hub download) instead of the intended fixture
   adapter. Fixed by aligning all imports to the `app....` convention.

4. Related identity bug: the same import split caused two independent
   copies of the RiskLevel enum to exist in memory, so `is` comparisons
   between values built from different import paths failed despite
   matching values. Resolved by the same import-path fix.

Result: All 45 backend tests pass after integration.

## M2 (NLP/ML)
Status: Not yet available. No branch/PR with usable code as of Day 13.
Currently using rule-based risk_engine.py as a placeholder for the
future ML classifier. No action possible until M2 hands off.

## M3 (Parsing/OCR)
Status: Not yet available. No branch/PR with usable code as of Day 13.
Currently using static text fixtures in place of real PDF/DOCX
extraction. No action possible until M3 hands off.