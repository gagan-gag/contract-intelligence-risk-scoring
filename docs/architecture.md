# Project Architecture

## Goal
Build an API that accepts contract files, extracts text, identifies entities and clauses, calculates an explainable risk score, and supports semantic search.

## Current flow
User -> React Frontend -> FastAPI -> File Validation -> Document Processing -> NLP/Risk Engine -> Chroma Vector Database -> API Response

## Current components
- FastAPI health and root endpoints
- Pydantic API schemas
- Upload response/status schemas
- PDF/DOCX file validation
- Baseline rule-based risk engine
- GitHub Actions CI with pytest

## Team module ownership
- Gagan: FastAPI, API contracts, validation, risk rules, integration
- Ayushi: NER, clause classification, model evaluation
- Karthika: PDF/DOCX extraction, OCR, data validation, chunking
- Charan: embeddings, Chroma vector database, semantic search API
- Srinivas: frontend dashboard, QA, tests, documentation

## Week 1 decisions
- Python 3.11+ and FastAPI are used for the backend.
- Pydantic defines shared API contracts.
- PDF and DOCX are the only allowed upload formats.
- The maximum upload size is 10 MB.
- Rule-based risk scoring is the baseline before ML integration.
- Chroma will be used locally for vector search.
- Every code change must have tests and pass GitHub Actions CI.