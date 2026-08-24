import type { RiskScore } from '../mocks/api'

export function RiskResults({ risk }: { risk: RiskScore | null }) {
  if (!risk) return <p>No results yet.</p>
  return (
    <div>
      <h2>Risk Level: {risk.level.toUpperCase()}</h2>
      <p>Score: {risk.score}</p>
      <ul>{risk.reasons.map(r => <li key={r}>{r}</li>)}</ul>
    </div>
  )
}
