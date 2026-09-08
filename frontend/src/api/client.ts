const getApiBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname || '127.0.0.1'
    return `${window.location.protocol}//${hostname}:8001`
  }
  return 'http://127.0.0.1:8001'
}

const BASE_URL = getApiBaseUrl()

export interface DocumentUploadResponse {
  document_id: string
  job_id: string
  filename: string
  status: string
}

export interface RiskScore {
  score: number
  level: 'low' | 'medium' | 'high'
  reasons: string[]
}

export interface Entity {
  text: string
  entity_type: 'party' | 'date' | 'money' | 'jurisdiction'
  page_number: number
  confidence: number
}

export interface Clause {
  clause_type: string
  text: string
  page_number: number
  confidence: number
  redline_suggestion?: string
  risk_mitigation?: string
}

export interface DocumentInfo {
  document_id: string
  filename: string
  file_type: string
  page_count: number
}

export interface AnalysisResponse {
  document: DocumentInfo
  entities: Entity[]
  clauses: Clause[]
  risk: RiskScore
}

export interface SearchResult {
  chunk_id: string
  document_id: string
  chunk_text: string
  distance: number
  metadata: Record<string, any>
}

export interface SearchResponse {
  query: string
  top_k: number
  results: SearchResult[]
}

export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let errorMsg = 'Upload failed'
    try {
      const err = await response.json()
      errorMsg = err.detail || errorMsg
    } catch {
      // fallback
    }
    throw new Error(errorMsg)
  }

  return response.json()
}

export async function getDocumentRisk(documentId: string): Promise<RiskScore> {
  const response = await fetch(`${BASE_URL}/documents/${documentId}/risk`)
  if (!response.ok) {
    if (response.status === 404) throw new Error('Document not found')
    if (response.status === 409) throw new Error('Analysis still in progress')
    throw new Error(`Failed to fetch risk score (${response.status})`)
  }
  return response.json()
}

export async function getDocumentAnalysis(documentId: string): Promise<AnalysisResponse> {
  const response = await fetch(`${BASE_URL}/documents/${documentId}/analysis`)
  if (!response.ok) {
    const risk = await getDocumentRisk(documentId)
    return {
      document: {
        document_id: documentId,
        filename: 'contract.pdf',
        file_type: 'pdf',
        page_count: 1,
      },
      entities: [],
      clauses: [],
      risk,
    }
  }
  return response.json()
}

export async function searchChunks(
  query: string,
  topK: number = 5,
  documentId?: string
): Promise<SearchResponse> {
  const url = new URL(`${BASE_URL}/search`)
  url.searchParams.set('query', query)
  url.searchParams.set('top_k', String(topK))
  if (documentId) {
    url.searchParams.set('document_id', documentId)
  }

  const response = await fetch(url.toString())
  if (!response.ok) {
    throw new Error(`Search request failed (${response.status})`)
  }
  return response.json()
}
