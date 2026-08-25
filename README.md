# AI-Powered Contract Intelligence & Risk Scoring (Legal NLP)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![spaCy](https://img.shields.io/badge/spaCy-NER-09A3D5.svg)](https://spacy.io/)
[![Transformers](https://img.shields.io/badge/🤗_Transformers-DistilBERT-FFD21E.svg)](https://huggingface.co/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Search-FC521F.svg)](https://www.trychroma.com/)

A legal NLP and contract intelligence platform engineered for enterprise legal and compliance teams. The system ingests lengthy commercial contracts (PDF / DOCX), extracts key legal entities (parties, execution/expiration dates, monetary values, jurisdictions), classifies high-risk clauses (auto-renewal, indemnity, unlimited liability, termination for convenience), computes explainable risk scores with actionable reasoning, and provides sub-second semantic search across contract repositories.

---

## 📌 Project Overview & Expected Impact

- **Primary Data Source:** **CUAD (Contract Understanding Atticus Dataset)** comprising 500+ commercial contracts with dense legal language annotated across 41 distinct legal categories.
- **Problem Solved:** Manual contract review is tedious, expensive, and error-prone. Critical liability caps or auto-renewal deadlines are often buried in 50+ page agreements.
- **Business Impact:**
  - Drastically reduces manual hours required for legal due diligence and high-volume contract review.
  - Mitigates enterprise risk by ensuring compliance teams never miss hidden liability clauses or unfavorable auto-renewal terms.
  - Standardizes risk scoring across multi-jurisdictional contracts with explainable AI findings.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Languages** | Python 3.11+, TypeScript, SQL |
| **NLP & Deep Learning** | Hugging Face Transformers (`distilbert-base-uncased`, `nli-distilroberta-base`), spaCy (`en_core_web_sm`), PyTorch |
| **Vector Search & Retrieval** | ChromaDB, `sentence-transformers/all-MiniLM-L6-v2`, LangChain-compatible indexing |
| **Backend & API** | FastAPI, Uvicorn, Pydantic v2, Python-Multipart |
| **Async Processing** | Celery / Lightweight Orchestration Service |
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons |
| **Document Ingestion** | `pypdf`, `python-docx`, Tesseract OCR pipeline |
| **Testing & CI/CD** | `pytest`, `pytest-asyncio`, `vitest`, GitHub Actions |
| **Deployment** | Docker, Docker Compose, AWS EC2 / Azure App Services |

---

## 🏗️ Architecture & NLP Pipeline

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          React Frontend (Vite)                         │
│   • Live Risk Ring Meter   • Clause Highlighting   • One-Click Clear   │
│   • Extracted Entity Badges (Parties, Dates, Money, Jurisdictions)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend API                           │
│   • /documents/upload     • /documents/{id}/analysis                   │
│   • /documents/{id}/risk  • /search (Semantic Vector Retrieval)        │
└───────────┬───────────────────────┬────────────────────────────┬───────┘
            │ Ingestion             │ NLP Analysis               │ Vector Query
            ▼                       ▼                            ▼
┌───────────────────────┐ ┌───────────────────────────┐ ┌────────────────┐
│   Document Parser     │ │     Legal NLP Engine      │ │   ChromaDB     │
│  • pypdf (PDF text)   │ │  • spaCy Legal NER        │ │  • 384-d MiniLM│
│  • python-docx (DOCX) │ │    (Party, Date, Money)   │ │    Embeddings  │
│  • File validator     │ │  • DistilBERT Classifier  │ │  • Metadata    │
│  • OCR pipeline       │ │    (10+ Clause Types)     │ │    Filtering   │
│                       │ │  • Explainable Risk Rules │ │  • Top-K chunks│
│                       │ │  • Regex Fallback Layer   │ │                │
└───────────────────────┘ └───────────────────────────┘ └────────────────┘
```

---

## 📅 4-Week Development Timeline

### **Week 1: Data Parsing & Baseline Modeling**
- **Day 1-2:** Environment setup and CUAD dataset conversion into tokenized text and spaCy binary datasets (`ml/experiments/cuad_preprocess.py`).
- **Day 3-5:** Implement document ingestion pipeline (`pypdf`, `python-docx`, OCR fallback) with file integrity and size validation.
- **Day 6-7:** Train and evaluate baseline Named Entity Recognition (NER) model using spaCy for legal organizations, dates, monetary values, and jurisdictions.

### **Week 2: Advanced NLP & Fine-Tuning**
- **Day 1-4:** Fine-tune transformer model (`distilbert-base-uncased` / `legal-roberta`) on CUAD multi-label clause classification (`ml/experiments/train_clause_classifier.py`).
- **Day 5-7:** Evaluate model precision/recall/F1 metrics (`ml/experiments/evaluate.py`) and implement post-processing confidence scoring with dual-tier regex fallback.

### **Week 3: Vector Search & API Development**
- **Day 1-3:** Implement dense chunk embeddings (`all-MiniLM-L6-v2`) and populate local ChromaDB collection for semantic clause retrieval.
- **Day 4-7:** Develop asynchronous FastAPI application endpoints (`/documents/upload`, `/documents/{id}/analysis`, `/documents/{id}/risk`, `/search`).

### **Week 4: Integration & Productionization**
- **Day 1-3:** Containerize the API, ChromaDB, and ML model services using multi-stage Dockerfiles and `docker-compose.yml`.
- **Day 4-5:** Enhance React dashboard with live risk meter, entity inspector, clause breakdown, and interactive **Clear Document** state management.
- **Day 6-7:** Full integration testing (pytest + vitest), load testing, logging configuration, and production documentation.

---

## 🤖 ML & Training Pipeline

The repository provides training and evaluation scripts in `ml/experiments/`:

### 1. Preprocess CUAD Dataset
Converts CUAD annotations into spaCy binary training datasets:
```bash
python ml/experiments/cuad_preprocess.py --cuad-json data/CUAD_v1.json --output-dir ml/data --dev-ratio 0.15
```

### 2. Train spaCy Legal NER
Trains an entity recognition pipeline to identify legal parties, dates, monetary amounts, and jurisdictions:
```bash
python ml/experiments/train_ner.py --train ml/data/train.spacy --dev ml/data/dev.spacy --output-dir ml/models/legal_ner --epochs 20
```

### 3. Fine-Tune DistilBERT Clause Classifier
Fine-tunes DistilBERT for multi-label classification across 10 core legal clauses:
```bash
python ml/experiments/train_clause_classifier.py --cuad-json data/CUAD_v1.json --output-dir ml/models/clause_classifier --epochs 3 --batch-size 8
```

### 4. Evaluate Models
Computes precision, recall, and F1 metrics on held-out test splits:
```bash
# Evaluate NER
python ml/experiments/evaluate.py ner --model ml/models/legal_ner/model-best --dev ml/data/dev.spacy

# Evaluate Clause Classifier
python ml/experiments/evaluate.py classifier --model ml/models/clause_classifier --cuad-json data/CUAD_v1.json
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm 9+
- Windows PowerShell / Linux bash

### 1. Clone & Setup Python Virtual Environment
```bash
git clone https://github.com/your-org/contract-intelligence-risk-scoring.git
cd contract-intelligence-risk-scoring

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Frontend
```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` (or use PowerShell):
```powershell
Copy-Item .env.example .env
```
Default configuration:
```env
PYTHONPATH=backend
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8010
VECTOR_COLLECTION_NAME=contract_chunks
VECTOR_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VITE_API_BASE_URL=http://localhost:8010
```

---

## 🏃 Running the Application

### Start the FastAPI Backend
```powershell
$env:PYTHONPATH = "backend"
uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```
- API Docs (Swagger UI): [http://127.0.0.1:8010/docs](http://127.0.0.1:8010/docs)
- Health Check: [http://127.0.0.1:8010/health](http://127.0.0.1:8010/health)

### Start the React Frontend
```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 4173
```
- Open Dashboard: [http://localhost:4173](http://localhost:4173)

---

## 📡 API Reference

### 1. Upload Contract Document
- **Endpoint:** `POST /documents/upload`
- **Content-Type:** `multipart/form-data`
- **Payload:** `file: <binary PDF or DOCX>`
- **Response:**
  ```json
  {
    "document_id": "8b5e9112-2d11-47fb-94a2-7fa345228a0e",
    "job_id": "fa21b920-5c68-4521-99ee-376510da89b2",
    "filename": "master_service_agreement.pdf",
    "status": "complete"
  }
  ```

### 2. Get Full Contract Analysis (NLP + Risk)
- **Endpoint:** `GET /documents/{document_id}/analysis`
- **Response:**
  ```json
  {
    "document": {
      "document_id": "8b5e9112-2d11-47fb-94a2-7fa345228a0e",
      "filename": "master_service_agreement.pdf",
      "file_type": "pdf",
      "page_count": 4
    },
    "entities": [
      {
        "text": "Acme Global Solutions Inc.",
        "entity_type": "party",
        "page_number": 1,
        "confidence": 0.94
      },
      {
        "text": "January 15, 2024",
        "entity_type": "date",
        "page_number": 1,
        "confidence": 0.98
      },
      {
        "text": "$500,000 USD",
        "entity_type": "money",
        "page_number": 2,
        "confidence": 0.91
      },
      {
        "text": "State of California",
        "entity_type": "jurisdiction",
        "page_number": 3,
        "confidence": 0.88
      }
    ],
    "clauses": [
      {
        "clause_type": "auto_renewal",
        "text": "This agreement shall automatically renew for successive 1-year terms...",
        "page_number": 1,
        "confidence": 0.89
      },
      {
        "clause_type": "indemnity",
        "text": "Vendor agrees to indemnify and hold harmless the Client...",
        "page_number": 2,
        "confidence": 0.92
      }
    ],
    "risk": {
      "score": 65,
      "level": "high",
      "reasons": [
        "Auto-renewal clause detected.",
        "Indemnification obligation detected."
      ]
    }
  }
  ```

### 3. Get Risk Score (Backward-Compatible)
- **Endpoint:** `GET /documents/{document_id}/risk`
- **Response:**
  ```json
  {
    "score": 65,
    "level": "high",
    "reasons": [
      "Auto-renewal clause detected.",
      "Indemnification obligation detected."
    ]
  }
  ```

### 4. Semantic Search Over Indexed Clauses
- **Endpoint:** `GET /search?query=indemnification%20liability%20limit&top_k=5`
- **Response:**
  ```json
  {
    "query": "indemnification liability limit",
    "top_k": 5,
    "results": [
      {
        "chunk_id": "chunk-102",
        "document_id": "8b5e9112-2d11-47fb-94a2-7fa345228a0e",
        "chunk_text": "Section 12. Limitation of Liability and Indemnification...",
        "distance": 0.231,
        "metadata": {
          "clause_label": "liability",
          "page_number": 3
        }
      }
    ]
  }
  ```

---

## 🧪 Testing

### Backend Unit & Integration Tests (pytest)
```powershell
$env:PYTHONPATH = "backend"
pytest backend/tests -v
```

### Frontend Tests (Vitest)
```bash
cd frontend
npm test
```

---

## 👥 Team Member Responsibilities

| Member | Focus Area | Key Deliverables |
|---|---|---|
| **Gagan** | Backend Architecture & Pipeline | FastAPI routers, job orchestration, synchronous upload execution, API contract consistency |
| **Ayushi** | Legal NLP & ML Modeling | spaCy NER pipeline, DistilBERT clause classification, CUAD experiment scripts, evaluation suite |
| **Karthika** | Document Ingestion & Parsing | PDF/DOCX text extraction, byte validation, OCR fallback strategies, chunking |
| **Charan** | Vector Database & Retrieval | ChromaDB integration, sentence-transformers embeddings, semantic search filtering |
| **Srinivas** | Frontend Dashboard & UX | React components, live risk visualizer, entity & clause inspectors, Clear button state, Vitest suite |

---

## ⚖️ Disclaimer

*This software is intended for educational, research, and automated due diligence assistance purposes only. It does not constitute formal legal advice or substitute for human legal review.*
