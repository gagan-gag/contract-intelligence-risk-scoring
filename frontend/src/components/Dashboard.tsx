import { useEffect, useMemo, useState } from 'react'
import { uploadDocument } from '../api/client'
import { useAnalysisStatus } from '../hooks/useAnalysisStatus'
import type { AnalysisResult, RiskScore } from '../mocks/api'
import { LoadingSkeleton } from './LoadingSkeleton'
import { RiskResults } from './RiskResults'
import { UploadScreen } from './UploadScreen'

export function Dashboard() {
  const [risk, setRisk] = useState<RiskScore | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [filename, setFilename] = useState('')
  const [documentId, setDocumentId] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { status, risk: liveRisk, analysis: liveAnalysis, error: analysisError } = useAnalysisStatus(documentId)

  useEffect(() => {
    if (liveAnalysis) {
      setAnalysis(liveAnalysis)
      setRisk(liveAnalysis.risk)
      setIsAnalyzing(false)
    } else if (liveRisk) {
      setRisk(liveRisk)
      setIsAnalyzing(false)
    }
  }, [liveRisk, liveAnalysis])

  useEffect(() => {
    if (status === 'failed') {
      setError(analysisError ?? 'Risk analysis failed')
      setIsAnalyzing(false)
    }
    if (status === 'processing') {
      setIsAnalyzing(true)
    }
  }, [analysisError, status])

  const statCards = useMemo(
    () => [
      { label: 'Contracts reviewed', value: '1,284', tone: 'sky' },
      { label: 'Avg. risk score', value: '37/100', tone: 'indigo' },
      { label: 'Clause alerts', value: '48', tone: 'violet' },
    ],
    [],
  )

  async function handleUpload(file: File) {
    setError(null)
    setDocumentId(null)
    setRisk(null)
    setAnalysis(null)
    setIsAnalyzing(true)

    try {
      const response = await uploadDocument(file)
      setDocumentId(response.document_id)
      setFilename(file.name)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed'
      setError(message)
      setIsAnalyzing(false)
    }
  }

  function handleClear() {
    setError(null)
    setDocumentId(null)
    setRisk(null)
    setAnalysis(null)
    setFilename('')
    setIsAnalyzing(false)
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="glass-panel flex items-center justify-between rounded-2xl px-5 py-4 shadow-soft">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-violet-500 text-lg font-bold text-white">
              CI
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.35em] text-slate-400">Platform</p>
              <h1 className="text-lg font-semibold text-white">Contract Intelligence</h1>
            </div>
          </div>

          <div className="hidden items-center gap-3 md:flex">
            <div className="rounded-full border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-sm text-slate-200">
              Enterprise AI review
            </div>
            <div className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1.5 text-sm font-medium text-emerald-300">
              Live
            </div>
          </div>
        </header>

        <section className="mt-8 grid gap-4 md:grid-cols-3">
          {statCards.map(card => (
            <div key={card.label} className="glass-panel rounded-2xl p-4 shadow-soft">
              <p className="text-xs font-medium uppercase tracking-[0.25em] text-slate-400">{card.label}</p>
              <p className="mt-4 text-3xl font-semibold text-white">{card.value}</p>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="space-y-6">
            <UploadScreen
              onFileSelected={setFilename}
              onAnalyzingChange={setIsAnalyzing}
              onUpload={handleUpload}
              onClear={handleClear}
              selectedFile={filename || null}
            />

            {isAnalyzing && (
              <div className="surface-panel p-6">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-xs font-medium uppercase tracking-[0.28em] text-sky-300">Processing</p>
                  <span className="text-sm text-slate-300">{filename || 'contract.pdf'}</span>
                </div>
                <LoadingSkeleton />
              </div>
            )}

            {error && (
              <div role="alert" className="status-alert flex items-start justify-between gap-3">
                <span>{error}</span>
                <button
                  type="button"
                  onClick={() => setError(null)}
                  className="shrink-0 text-rose-300 hover:text-white"
                  aria-label="Dismiss error"
                >
                  ✕
                </button>
              </div>
            )}
          </div>

          <div>
            <RiskResults risk={risk} analysis={analysis} />
          </div>
        </section>
      </div>
    </main>
  )
}
