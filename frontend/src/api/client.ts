export const API_BASE_URLS = [
  'http://127.0.0.1:8010',
  'http://localhost:8010',
  import.meta.env.VITE_API_BASE_URL,
  '',
  'http://127.0.0.1:8000',
  'http://localhost:8000',
].filter((value): value is string => value !== undefined && value !== null)

async function fetchWithFallback(path: string, init?: RequestInit) {
  let lastError: Error | null = null

  for (const baseUrl of API_BASE_URLS) {
    try {
      const url = baseUrl ? `${baseUrl}${path}` : path
      const response = await fetch(url, init)
      // Only accept if backend answered with ok, 400 (validation error), or 409 (in-progress)
      if (response.ok || response.status === 400 || response.status === 409) {
        return response
      }
      // If backend returned 404 or 500, check if it's a JSON response from our FastAPI backend
      const contentType = response.headers.get('content-type') || ''
      if (contentType.includes('application/json')) {
        return response
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Request failed')
    }
  }

  throw lastError ?? new Error('Failed to connect to the backend server. Please verify the backend is running on port 8010.')
}

export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetchWithFallback('/documents/upload', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.detail ?? `Upload failed (HTTP ${response.status})`)
  }

  return response.json()
}

export async function getDocumentRisk(documentId: string) {
  const response = await fetchWithFallback(`/documents/${documentId}/risk`)

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.detail ?? 'Risk lookup failed')
  }

  return response.json()
}

export async function getAnalysisResult(documentId: string) {
  const response = await fetchWithFallback(`/documents/${documentId}/analysis`)

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    if (response.status === 409) {
      throw new Error(payload.detail ?? 'Analysis not complete')
    }
    throw new Error(payload.detail ?? 'Analysis lookup failed')
  }

  return response.json()
}
