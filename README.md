# ⚖️ AI-Powered Contract Intelligence & Risk Scoring

> Enterprise-grade NLP pipeline for legal contract analysis — clause extraction, explainable risk scoring, AI redline negotiation playbook, and semantic vector search.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org)
[![Tests](https://img.shields.io/badge/Tests-45%20passed-brightgreen.svg)](#testing)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)](#disclaimer)

---

## 📌 What It Does

Upload any **PDF or DOCX** contract and instantly receive:

- 📊 **Explainable Risk Score** (0–100) with High / Medium / Low classification
- 🏢 **Extracted Legal Entities** — Parties, Dates, Financial Values (₹ INR), Jurisdictions
- ⚖️ **Classified Risky Clauses** — Indemnification, Auto-Renewal, Liability Cap, Termination
- 💡 **AI Redline Negotiation Playbook** — Safe counter-proposal for every risky clause with 1-click copy
- 📄 **Export Audit Report** — Browser-printable 2-page executive PDF summary
- 🔍 **Semantic Vector Search** — Query contract clauses in natural language via ChromaDB embeddings

---

## 🖼️ Demo

Click **⚡ Load Sample Demo** in the UI to instantly see a full intelligence report — no upload needed.

| Tab | Description |
|-----|-------------|
| 📊 Risk Analysis | Upload contract → get risk score, entities, clause cards, AI redlines |
| 🔍 Vector Search | Natural language semantic search over indexed contract chunks |

---

## 🏗️ Architecture

```
User → React Frontend (Vite + TypeScript)
          ↓
     FastAPI Backend (Python)
          ├── File Validation (PDF/DOCX, 10MB limit)
          ├── Text Extraction (pypdf / python-docx)
          ├── Legal NER (spaCy + rule-based)
          ├── Clause Classification (keyword + confidence scoring)
          ├── Explainable Risk Engine (weighted scoring)
          ├── ChromaDB Vector Index (all-MiniLM-L6-v2 embeddings)
          └── Background Task Queue (FastAPI BackgroundTasks)
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI 0.115, Uvicorn |
| **NLP** | spaCy, Hugging Face sentence-transformers |
| **Document Parsing** | pypdf, python-docx, PyMuPDF |
| **Vector Database** | ChromaDB (local persistent) |
| **Embeddings** | all-MiniLM-L6-v2 |
| **Frontend** | React 18, Vite 8, TypeScript 5 |
| **Styling** | Vanilla CSS — Premium Light UI, Plus Jakarta Sans |
| **Testing** | pytest (45 tests), Vitest (frontend) |
| **CI/CD** | GitHub Actions |
| **Deployment** | Docker + Docker Compose |

---

## 📁 Project Structure

```
contract-intelligence-risk-scoring/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app + CORS middleware
│   │   ├── schemas.py               # Pydantic models
│   │   ├── routers/
│   │   │   ├── upload.py            # POST /documents/upload
│   │   │   ├── risk.py              # GET /documents/{id}/risk & /analysis
│   │   │   └── search.py            # GET /search (vector similarity)
│   │   ├── services/
│   │   │   ├── analysis_service.py  # NER + clause classification + risk scoring
│   │   │   ├── file_validation.py   # File type & size validation
│   │   │   └── job_service.py       # In-memory job store
│   │   └── vector/
│   │       ├── chroma_adapter.py    # ChromaDB upsert / query
│   │       ├── embeddings.py        # sentence-transformers encoder
│   │       └── schemas.py           # VectorChunkMetadata
│   └── tests/                       # 45 pytest tests
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Dashboard.tsx        # Tab layout, demo loader, export
│       │   ├── UploadScreen.tsx     # Drag-and-drop upload zone
│       │   ├── RiskResults.tsx      # Score dial, entities, AI redlines
│       │   └── SemanticSearch.tsx   # Vector search UI
│       ├── api/client.ts            # Typed fetch API client
│       ├── hooks/useAnalysisStatus.ts  # Polling hook
│       └── index.css                # Premium light design system
├── examples/
│   └── sample_contracts/
│       ├── Master_Services_Agreement_HighRisk.pdf    # 🔴 High risk
│       ├── Non_Disclosure_Agreement_LowRisk.pdf      # 🟢 Low risk
│       ├── Software_License_Agreement_MediumRisk.docx # 🟡 Medium risk
│       └── Vendor_Supply_Agreement_HighRisk.docx     # 🔴 High risk
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Quick Start (Local Dev)

### 1. Clone & Setup Backend

```powershell
git clone https://github.com/gagan-gag/contract-intelligence-risk-scoring.git
cd contract-intelligence-risk-scoring
git checkout Gagan/ml-system-integration

# Create virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Backend

```powershell
uvicorn app.main:app --app-dir backend --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Run Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: [http://localhost:5173](http://localhost:5173)

---

## 🐳 Docker (1-Command Start)

```powershell
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info |
| `GET` | `/health` | Health check |
| `POST` | `/documents/upload` | Upload PDF/DOCX contract |
| `GET` | `/documents/{id}/status` | Check processing status |
| `GET` | `/documents/{id}/risk` | Get risk score (0–100) |
| `GET` | `/documents/{id}/analysis` | Full intelligence report |
| `GET` | `/search?query=...&top_k=5` | Semantic vector search |

---

## 🧪 Testing

```powershell
# Backend — 45 tests
pytest backend/tests -q

# Frontend
cd frontend
npx vitest run

# Production build check
npm run build
```

**Latest results:** `45 passed, 0 failed` · Frontend: `1 passed, 0 failed` · Build: `✓ 0 errors`

---

## 📄 Example Contracts

Ready-to-use sample contracts in [`examples/sample_contracts/`](examples/sample_contracts/):

| File | Format | Risk | Key Issues |
|------|--------|------|------------|
| `Master_Services_Agreement_HighRisk.pdf` | PDF | 🔴 High | Uncapped indemnity, auto-renewal 90-day lock |
| `Non_Disclosure_Agreement_LowRisk.pdf` | PDF | 🟢 Low | Standard mutual NDA terms |
| `Software_License_Agreement_MediumRisk.docx` | DOCX | 🟡 Medium | Unilateral modification rights |
| `Vendor_Supply_Agreement_HighRisk.docx` | DOCX | 🔴 High | Unlimited liability, unfair termination |

All financial values are in **Indian Rupees (₹ / INR)**.

---

## 👥 Team Members

| Member | Responsibility |
|--------|---------------|
| **Gagan** | FastAPI backend, architecture, risk engine, integration, Docker |
| **Ayushi** | NLP, spaCy NER, clause classification, model evaluation |
| **Karthika** | Document parsing, OCR, data validation, text chunking |
| **Charan** | ChromaDB vector database, embeddings, semantic search |
| **Srinivas** | React frontend dashboard, QA, testing, documentation |

---

## 📋 Development Rules

- Work only on your personal branch
- Never push directly to `main` — create a Pull Request
- Run tests before every push: `pytest backend/tests -q`
- Never commit `.env` files, API keys, or real contract documents
- Push meaningful progress to GitHub every day

---

## ⚠️ Disclaimer

This project is for **educational and demonstration purposes only**.
It does not constitute legal advice. Always consult a qualified legal professional before making decisions based on contract analysis.
