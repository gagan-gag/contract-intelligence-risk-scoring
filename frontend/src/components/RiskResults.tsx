import { useState } from 'react'
import type { AnalysisResponse, RiskScore } from '../api/client'

interface RiskResultsProps {
  risk: RiskScore | null
  analysis?: AnalysisResponse | null
  filename?: string | null
}

export function RiskResults({ risk, analysis, filename }: RiskResultsProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  if (!risk) {
    return (
      <div className="empty-state">
        <div className="empty-icon">📊</div>
        <h3>No Contract Evaluated Yet</h3>
        <p>Upload a contract PDF or DOCX on the left, or click "Load Sample Demo" above to view an instant intelligence report.</p>
      </div>
    )
  }

  const handleCopyRedline = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => {
      setCopiedIndex(null)
    }, 2500)
  }

  const levelClass =
    risk.level === 'high' ? 'badge-high' : risk.level === 'medium' ? 'badge-medium' : 'badge-low'

  const dialClass =
    risk.level === 'high' ? 'dial-high' : risk.level === 'medium' ? 'dial-medium' : 'dial-low'

  // Group entities by type
  const parties = analysis?.entities.filter((e) => e.entity_type === 'party') || []
  const dates = analysis?.entities.filter((e) => e.entity_type === 'date') || []
  const money = analysis?.entities.filter((e) => e.entity_type === 'money') || []
  const jurisdictions = analysis?.entities.filter((e) => e.entity_type === 'jurisdiction') || []

  return (
    <div className="risk-results-container" id="printable-risk-report">
      <div className="risk-summary-card">
        <div className="risk-summary-header">
          <div>
            <h3>Contract Risk Intelligence Report</h3>
            {filename && (
              <div className="doc-badge-info">
                <span>Evaluated File:</span>
                <code>{filename}</code>
              </div>
            )}
          </div>
          <span className={`risk-badge ${levelClass}`}>
            ● {risk.level} Risk Exposure
          </span>
        </div>

        <div className="score-hero">
          <div className={`score-dial ${dialClass}`}>
            <span className="score-number">{risk.score}</span>
            <span className="score-total">/ 100</span>
          </div>
          <div className="score-meta">
            <h4>
              {risk.level === 'high'
                ? 'High Risk Assessment'
                : risk.level === 'medium'
                ? 'Moderate Risk Assessment'
                : 'Low Risk Assessment'}
            </h4>
            <p>
              {risk.score >= 70
                ? 'Multiple unmitigated liability, indemnification, or renewal penalty clauses detected.'
                : risk.score >= 35
                ? 'Moderate exposure clauses identified. Review recommended before execution.'
                : 'Standard commercial terms. Minimal outlier liability exposure.'}
            </p>
          </div>
        </div>

        <div className="reasons-container">
          <h4>📌 Identified Risk Drivers & Findings</h4>
          {risk.reasons.length === 0 ? (
            <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
              No critical risk triggers detected in this agreement.
            </p>
          ) : (
            <ul className="reasons-list">
              {risk.reasons.map((reason, idx) => (
                <li key={idx} className="reason-item">
                  <span className="reason-bullet">
                    {risk.level === 'high' ? '🚨' : risk.level === 'medium' ? '⚠️' : 'ℹ️'}
                  </span>
                  <div>{reason}</div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Extracted Entities */}
        {(parties.length > 0 || dates.length > 0 || money.length > 0 || jurisdictions.length > 0) && (
          <div className="entities-container">
            <h4>🏢 Extracted Legal Entities</h4>
            <div className="entities-grid">
              {parties.length > 0 && (
                <div className="entity-group">
                  <div className="entity-group-title">Parties & Organizations</div>
                  <div className="entity-chips">
                    {parties.map((p, i) => (
                      <span key={i} className="entity-chip" title={`Confidence: ${(p.confidence * 100).toFixed(0)}%`}>
                        {p.text}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {dates.length > 0 && (
                <div className="entity-group">
                  <div className="entity-group-title">Key Dates</div>
                  <div className="entity-chips">
                    {dates.map((d, i) => (
                      <span key={i} className="entity-chip">
                        📅 {d.text}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {money.length > 0 && (
                <div className="entity-group">
                  <div className="entity-group-title">Financial Values (INR / USD)</div>
                  <div className="entity-chips">
                    {money.map((m, i) => (
                      <span key={i} className="entity-chip" style={{ background: '#ecfdf5', color: '#065f46', borderColor: '#a7f3d0' }}>
                        💵 {m.text}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {jurisdictions.length > 0 && (
                <div className="entity-group">
                  <div className="entity-group-title">Governing Jurisdictions</div>
                  <div className="entity-chips">
                    {jurisdictions.map((j, i) => (
                      <span key={i} className="entity-chip" style={{ background: '#f5f3ff', color: '#5b21b6', borderColor: '#ddd6fe' }}>
                        🏛️ {j.text}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Classified Clauses with AI Redline Playbook */}
        {analysis?.clauses && analysis.clauses.length > 0 && (
          <div className="clauses-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4>⚖️ Classified Clauses & AI Redline Playbook</h4>
              <span style={{ fontSize: '0.75rem', color: '#2563eb', fontWeight: 700, background: '#eff6ff', padding: '0.2rem 0.6rem', borderRadius: '9999px', border: '1px solid #bfdbfe' }}>
                ✨ AI Counter-Proposals Enabled
              </span>
            </div>

            <div className="clauses-list">
              {analysis.clauses.map((clause, idx) => {
                const isHigh =
                  clause.clause_type.includes('liability') ||
                  clause.clause_type.includes('indemnity')
                const isMed =
                  clause.clause_type.includes('renewal') ||
                  clause.clause_type.includes('termination')
                const cardClass = isHigh
                  ? 'clause-high'
                  : isMed
                  ? 'clause-medium'
                  : ''
                return (
                  <div key={idx} className={`clause-card ${cardClass}`}>
                    <div className="clause-header">
                      <span className="clause-type">{clause.clause_type.replace('_', ' ')}</span>
                      <span className="clause-meta">
                        Page {clause.page_number} &bull; {(clause.confidence * 100).toFixed(0)}% Match
                      </span>
                    </div>
                    
                    <div className="clause-text">
                      <strong>Current Text:</strong> "{clause.text}"
                    </div>

                    {/* AI Redline Suggestion Box */}
                    {clause.redline_suggestion && (
                      <div className="redline-box">
                        <div className="redline-header">
                          <div className="redline-title">
                            💡 <strong>AI Recommended Safe Redline (Negotiation Playbook)</strong>
                          </div>
                          <button
                            type="button"
                            className="copy-btn"
                            onClick={() => handleCopyRedline(clause.redline_suggestion!, idx)}
                            title="Copy safe clause for contract markup"
                          >
                            {copiedIndex === idx ? '✓ Copied!' : '📋 Copy Safe Redline'}
                          </button>
                        </div>
                        <div className="redline-text">
                          "{clause.redline_suggestion}"
                        </div>
                        {clause.risk_mitigation && (
                          <div className="redline-mitigation">
                            🛡️ <strong>Mitigation Rationale:</strong> {clause.risk_mitigation}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
