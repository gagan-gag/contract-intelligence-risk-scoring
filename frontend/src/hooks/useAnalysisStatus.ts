import { useEffect, useState } from 'react'
import { getAnalysisResult } from '../api/client'
import type { AnalysisResult, RiskScore } from '../mocks/api'

export function useAnalysisStatus(documentId: string | null) {
  const [status, setStatus] = useState<'idle' | 'processing' | 'complete' | 'failed'>('idle')
  const [risk, setRisk] = useState<RiskScore | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!documentId) {
      setStatus('idle')
      setRisk(null)
      setAnalysis(null)
      setError(null)
      return
    }

    let active = true
    let intervalId: number | undefined

    async function pollAnalysis() {
      try {
        const result: AnalysisResult = await getAnalysisResult(documentId!)

        if (!active) return

        setAnalysis(result)
        setRisk(result.risk)
        setStatus('complete')
        setError(null)
        window.clearInterval(intervalId)
      } catch (err) {
        if (!active) return

        const message = err instanceof Error ? err.message : 'Analysis failed'
        if (message.includes('not complete') || message.includes('409')) {
          setStatus('processing')
          setError(null)
          return
        }

        setStatus('failed')
        setError(message)
        window.clearInterval(intervalId)
      }
    }

    setStatus('processing')
    setError(null)
    pollAnalysis()
    intervalId = window.setInterval(pollAnalysis, 2000)

    return () => {
      active = false
      if (intervalId) window.clearInterval(intervalId)
    }
  }, [documentId])

  return { status, risk, analysis, error }
}
