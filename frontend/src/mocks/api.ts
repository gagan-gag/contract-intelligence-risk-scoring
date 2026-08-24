export interface RiskScore {
  score: number
  level: 'low' | 'medium' | 'high'
  reasons: string[]
}

export const mockRiskResponse: RiskScore = {
  score: 65,
  level: 'high',
  reasons: ['Auto-renewal detected.', 'Indemnification detected.'],
}
