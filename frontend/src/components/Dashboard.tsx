import { useState } from 'react'
import { UploadScreen } from './UploadScreen'
import { RiskResults } from './RiskResults'
import { SemanticSearch } from './SemanticSearch'
import { useAnalysisStatus } from '../hooks/useAnalysisStatus'
import type { AnalysisResponse, RiskScore } from '../api/client'

const SAMPLE_DEMO_RISK: RiskScore = {
  score: 78,
  level: 'high',
  reasons: [
    'Uncapped indemnification obligations detected without reciprocal liability protection.',
    'Automatic renewal clause with restrictive 90-day written cancellation notice requirement.',
    'Broad unilateral termination without notice penalty provisions.',
    'Governing jurisdiction specified in Bengaluru, Karnataka with INR 1.5 Crore exposure.',
  ],
}

const SAMPLE_DEMO_ANALYSIS: AnalysisResponse = {
  document: {
    document_id: 'contract-demo-2026-001',
    filename: 'Master_Services_Agreement_HighRisk.pdf',
    file_type: 'pdf',
    page_count: 6,
  },
  risk: SAMPLE_DEMO_RISK,
  entities: [
    { text: 'Tata Consultancy Solutions Pvt Ltd', entity_type: 'party', page_number: 1, confidence: 0.98 },
    { text: 'Apex Cloud Technologies Ltd', entity_type: 'party', page_number: 1, confidence: 0.96 },
    { text: 'October 15, 2026', entity_type: 'date', page_number: 1, confidence: 0.94 },
    { text: 'INR 1,50,00,000', entity_type: 'money', page_number: 2, confidence: 0.95 },
    { text: 'Rs. 37,50,000 quarterly', entity_type: 'money', page_number: 2, confidence: 0.93 },
    { text: 'Rs. 25,00,000 penalty', entity_type: 'money', page_number: 4, confidence: 0.91 },
    { text: 'Bengaluru, Karnataka', entity_type: 'jurisdiction', page_number: 5, confidence: 0.97 },
  ],
  clauses: [
    {
      clause_type: 'indemnification',
      text: 'Vendor shall fully defend, indemnify, and hold harmless Customer, its directors, officers, and affiliates from and against any and all claims, liabilities, losses, damages, penalties, and expenses regarding all indemnification obligations without limitation of liability.',
      page_number: 3,
      confidence: 0.96,
      risk_mitigation: 'Cap indemnification liability to 1x annual contract value (₹1.5 Cr) and make obligation mutual.',
      redline_suggestion: 'Each party agrees to defend, indemnify, and hold harmless the other party from third-party claims arising out of gross negligence or willful misconduct, provided aggregate indemnification liability shall not exceed the total fees paid under this Agreement in the preceding twelve (12) months.',
    },
    {
      clause_type: 'auto_renewal',
      text: 'This Agreement shall automatically renew for successive twelve (12) month periods unless either party delivers written notice of non-renewal at least 90 days prior to expiration. Failure to provide timely notice results in unconditional lock-in for the renewal term.',
      page_number: 2,
      confidence: 0.94,
      risk_mitigation: 'Replace automatic lock-in with standard affirmative written renewal or a 30-day notice window.',
      redline_suggestion: 'This Agreement shall renew for successive one (1) year periods only upon mutual written agreement of the parties executed at least thirty (30) days prior to the expiration of the then-current term.',
    },
    {
      clause_type: 'liability_cap',
      text: 'The parties expressly agree to unlimited liability regarding all indemnification obligations, intellectual property infringement, and data breach claims without any financial cap.',
      page_number: 3,
      confidence: 0.92,
      risk_mitigation: 'Insert a clear reciprocal aggregate liability ceiling equal to 12 months fees paid.',
      redline_suggestion: "Except for breach of confidentiality obligations, neither party's aggregate liability arising under or related to this Agreement shall exceed the total amounts actually paid by Customer in the twelve (12) months preceding the event giving rise to liability.",
    },
    {
      clause_type: 'termination',
      text: 'Customer may terminate without notice in case of performance variance, or terminate for convenience upon thirty (30) days prior written notice subject to early termination liquidated damages of Rs. 25,00,000.',
      page_number: 4,
      confidence: 0.93,
      risk_mitigation: 'Require a 30-day cure period for material breach and mutual termination for convenience without penalty.',
      redline_suggestion: 'Either party may terminate this Agreement: (a) for material breach upon thirty (30) days prior written notice if such breach remains uncured; or (b) for convenience upon sixty (60) days prior written notice without penalty or early termination fee.',
    },
  ],
}

export function Dashboard() {
  const [activeTab, setActiveTab] = useState<'analysis' | 'search'>('analysis')
  const [currentDocId, setCurrentDocId] = useState<string | null>(null)
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isDemoMode, setIsDemoMode] = useState(false)

  const {
    status,
    riskData,
    analysisData,
    errorMessage,
    setRiskData,
    setAnalysisData,
    setStatus,
  } = useAnalysisStatus(isDemoMode ? null : currentDocId)

  const handleUploadSuccess = (docId: string, filename: string) => {
    setIsDemoMode(false)
    setCurrentDocId(docId)
    setUploadedFileName(filename)
  }

  const handleLoadDemo = () => {
    setIsDemoMode(true)
    setCurrentDocId('contract-demo-2026-001')
    setUploadedFileName('Master_Services_Agreement_HighRisk.pdf')
    setRiskData(SAMPLE_DEMO_RISK)
    setAnalysisData(SAMPLE_DEMO_ANALYSIS)
    setStatus('complete')
  }

  const handleReset = () => {
    setCurrentDocId(null)
    setUploadedFileName(null)
    setIsDemoMode(false)
    setRiskData(null)
    setAnalysisData(null)
    setStatus('idle')
  }

  const handlePrintReport = () => {
    window.print()
  }

  const displayRisk = isDemoMode ? SAMPLE_DEMO_RISK : riskData
  const displayAnalysis = isDemoMode ? SAMPLE_DEMO_ANALYSIS : analysisData

  return (
    <div className="app-layout">
      {/* Top Header */}
      <header className="app-header no-print">
        <div className="header-brand">
          <span className="logo-icon">⚖️</span>
          <div className="brand-titles">
            <h1>
              Contract Intelligence
              <span className="brand-badge">NLP & Risk</span>
            </h1>
            <p className="tagline">Enterprise Clause Extraction, Risk Scoring & AI Redline Assistant</p>
          </div>
        </div>

        <div className="header-actions">
          <div className="nav-tabs">
            <button
              type="button"
              className={`tab-btn ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('analysis')}
            >
              📊 Risk Analysis
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              🔍 Vector Search
            </button>
          </div>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleLoadDemo}
            title="Load demonstration contract data"
          >
            ⚡ Load Sample Demo
          </button>

          {displayRisk && (
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={handlePrintReport}
              title="Print or export PDF executive report"
            >
              📄 Export Audit Report
            </button>
          )}

          {(currentDocId || isDemoMode) && (
            <button type="button" className="btn btn-outline btn-sm" onClick={handleReset}>
              Reset
            </button>
          )}
        </div>
      </header>

      {/* Main Content View */}
      {activeTab === 'analysis' ? (
        <main className="main-content">
          {/* Left Column: Upload */}
          <section className="section-card no-print">
            <div className="section-title">
              <div>
                <h2>1. Upload Agreement</h2>
                <p>Upload a PDF or Word document for automated legal analysis.</p>
              </div>
            </div>

            <UploadScreen
              onUploadSuccess={handleUploadSuccess}
              isUploading={isUploading}
              setIsUploading={setIsUploading}
            />

            <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--color-surface-border)', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
              🔒 <strong>Confidentiality Notice:</strong> Documents are processed in-memory and vectorized in local ChromaDB storage.
            </div>
          </section>

          {/* Right Column: Risk & Results */}
          <section className="section-card print-full-width">
            <div className="section-title no-print">
              <div>
                <h2>2. Intelligence & Risk Findings</h2>
                <p>Real-time NLP evaluation, clause risk breakdown, and AI mitigation.</p>
              </div>
            </div>

            {status === 'processing' && (
              <div className="status-banner status-processing no-print">
                <div className="spinner"></div>
                <div>
                  <strong>Analyzing Contract Intelligence...</strong>
                  <p>Extracting text, running spaCy NER, classifying liability clauses, and generating embeddings.</p>
                </div>
              </div>
            )}

            {status === 'failed' && (
              <div className="status-banner status-error no-print">
                <strong>Analysis Notice:</strong> {errorMessage || 'Failed to complete analysis.'}
              </div>
            )}

            <RiskResults
              risk={displayRisk}
              analysis={displayAnalysis}
              filename={uploadedFileName}
            />
          </section>
        </main>
      ) : (
        <main>
          <SemanticSearch activeDocumentId={currentDocId} />
        </main>
      )}

      {/* Footer */}
      <footer className="app-footer no-print">
        <p className="footer-credits">
          <strong>AI-Powered Contract Intelligence & Risk Scoring</strong> &bull; Phase 1 Architecture
        </p>
        <p>Built with FastAPI, Hugging Face Transformers, spaCy Legal NER, ChromaDB & React</p>
      </footer>
    </div>
  )
}

export default Dashboard
