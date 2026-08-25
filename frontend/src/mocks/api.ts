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
}

export interface AnalysisResult {
  document: {
    document_id: string
    filename: string
    file_type: string
    page_count: number
  }
  entities: Entity[]
  clauses: Clause[]
  risk: RiskScore
  nlp_backend?: string
}

export const mockRiskResponse: RiskScore = {
  score: 65,
  level: 'high',
  reasons: ['Auto-renewal detected.', 'Indemnification detected.'],
}
