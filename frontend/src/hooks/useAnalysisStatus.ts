import { useEffect, useState } from 'react'

export function useAnalysisStatus(documentId: string | null) {
  const [status, setStatus] = useState('idle')

  useEffect(() => {
    if (!documentId) return
    setStatus('processing')
    const interval = setInterval(async () => {
      try {
        const res = await fetch(\/documents/\/risk\)
        if (res.status === 200) { setStatus('complete'); clearInterval(interval) }
      } catch { setStatus('failed'); clearInterval(interval) }
    }, 2000)
    return () => clearInterval(interval)
  }, [documentId])

  return status
}
