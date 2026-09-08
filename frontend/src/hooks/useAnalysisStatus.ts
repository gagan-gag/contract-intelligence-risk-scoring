import { useEffect, useState } from 'react'
import { getDocumentAnalysis, type AnalysisResponse, type RiskScore } from '../api/client'

export type AnalysisState = 'idle' | 'processing' | 'complete' | 'failed'

export function useAnalysisStatus(documentId: string | null) {
  const [status, setStatus] = useState<AnalysisState>('idle')
  const [riskData, setRiskData] = useState<RiskScore | null>(null)
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!documentId) {
      setStatus('idle')
      setRiskData(null)
      setAnalysisData(null)
      setErrorMessage(null)
      return
    }

    setStatus('processing')
    setErrorMessage(null)

    let attempts = 0
    const maxAttempts = 30 // up to 60 seconds

    const interval = setInterval(async () => {
      attempts += 1
      try {
        const analysis = await getDocumentAnalysis(documentId)
        setAnalysisData(analysis)
        setRiskData(analysis.risk)
        setStatus('complete')
        clearInterval(interval)
      } catch (err: any) {
        if (err.message && err.message.includes('in progress')) {
          // Still processing, continue polling
          if (attempts >= maxAttempts) {
            setStatus('failed')
            setErrorMessage('Analysis timed out. Please try again.')
            clearInterval(interval)
          }
        } else {
          // Check if retry is needed or if failed
          if (attempts >= maxAttempts) {
            setStatus('failed')
            setErrorMessage(err.message || 'Failed to complete document analysis.')
            clearInterval(interval)
          }
        }
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [documentId])

  return {
    status,
    riskData,
    analysisData,
    errorMessage,
    setStatus,
    setRiskData,
    setAnalysisData,
  }
}
