# AI-Powered Contract Intelligence & Risk Scoring

A team-based NLP project that will analyse legal contracts, extract important information, identify risky clauses, and support semantic search.

## Current Status

Week 1 foundation is complete:

- FastAPI backend created
- Health and API-information endpoints added
- Pydantic schemas added
- PDF/DOCX upload validation added
- Baseline rule-based risk scoring added
- Automated tests and GitHub Actions CI added

## Features

- Accepts PDF and DOCX contract files
- Validates allowed file type and maximum file size
- Extracts entities, clauses, and contract metadata
- Calculates explainable contract risk scores
- Supports semantic search using Chroma Vector Database
- Provides FastAPI endpoints and automated testing

## Architecture

```text
User -> React Frontend -> FastAPI Backend
     -> File Validation
     -> Document Processing and OCR
     -> Text Chunking
     -> NER and Clause Classification
     -> Explainable Risk Engine
     -> Chroma Vector Database
     -> API Response
```

## Technology Stack

| Area | Technology |
|------|------------|
| Backend | Python, FastAPI, Uvicorn |
| Data validation | Pydantic |
| NLP | spaCy, Hugging Face Transformers |
| OCR | Tesseract OCR |
| Document parsing | PyMuPDF, python-docx |
| Vector database | Chroma |
| Frontend | React, Vite, TypeScript |
| Testing | pytest |
| CI | GitHub Actions |
| Deployment | Docker |

## Project Structure

```
backend/
  app/
    main.py                 # FastAPI application
    schemas.py              # Pydantic API contracts
    services/
      file_validation.py    # PDF/DOCX validation
      risk_engine.py        # Baseline risk rules
  tests/                    # Unit tests

docs/
  architecture.md
  daily-log.md

.github/workflows/
  ci.yml
```

## Setup

**Clone the repository:**
```bash
git clone https://github.com/gagan-gag/contract-intelligence-risk-scoring.git
cd contract-intelligence-risk-scoring
```

**Create and activate a virtual environment:**
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run tests:**
```bash
$env:PYTHONPATH="backend"
pytest backend/tests -q
```

**Run the API:**
```bash
uvicorn app.main:app --app-dir backend --reload
```

**Open:**
```
http://127.0.0.1:8000/docs
```

## Current API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /` | API information |
| `GET /health` | Service health check |

## Team Members

| Member | Responsibility |
|--------|-----------------|
| Gagan | FastAPI, architecture, integration, risk engine |
| Ayushi | NLP, NER, clause classification, model evaluation |
| Karthika | Document parsing, OCR, data validation, chunking |
| Charan | Chroma vector database, embeddings, semantic search |
| Srinivas | Frontend dashboard, QA, testing, documentation |

## Development Rules

- Work only on your personal branch
- Do not push directly to main
- Create a Pull Request for each completed task
- Run tests before pushing code
- Never commit passwords, API keys, `.env` files, or sensitive contract documents
- Push meaningful work to GitHub every day

## Disclaimer

This project is for educational and demonstration purposes only. It does not provide legal advice.
