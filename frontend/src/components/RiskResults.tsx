import type { AnalysisResult, RiskScore } from '../mocks/api'

const levelStyles = {
  low: {
    badge: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
    glow: 'from-emerald-500 to-teal-400',
    ring: 'bg-emerald-500/20',
  },
  medium: {
    badge: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
    glow: 'from-amber-400 to-orange-400',
    ring: 'bg-amber-500/20',
  },
  high: {
    badge: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
    glow: 'from-rose-500 to-red-400',
    ring: 'bg-rose-500/20',
  },
} as const

const entityBadgeColors: Record<string, string> = {
  party: 'border-sky-500/30 bg-sky-500/10 text-sky-300',
  date: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
  money: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  jurisdiction: 'border-purple-500/30 bg-purple-500/10 text-purple-300',
}

export function RiskResults({
  risk,
  analysis,
}: {
  risk: RiskScore | null
  analysis?: AnalysisResult | null
}) {
  const activeRisk = analysis?.risk ?? risk

  if (!activeRisk) {
    return (
      <div className="surface-panel flex min-h-[382px] flex-col items-center justify-center border-dashed bg-slate-900/60 p-6 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl text-slate-300">
          ✓
        </div>
        <p className="mt-4 text-base font-semibold leading-6 text-white">No contract analyzed yet</p>
        <p className="mt-2 max-w-xs text-sm leading-5 text-slate-400">Upload a PDF or DOCX to see a live risk summary, extracted entities, and detected clauses.</p>
      </div>
    )
  }

  const palette = levelStyles[activeRisk.level]
  const ringStyle = {
    background: `conic-gradient(#f8fafc 0deg, ${
      activeRisk.score > 60 ? '#f43f5e' : activeRisk.score > 35 ? '#f59e0b' : '#34d399'
    } ${activeRisk.score * 3.6}deg, rgba(148,163,184,0.12) 0deg)`,
  }

  const entities = analysis?.entities ?? []
  const clauses = analysis?.clauses ?? []

  return (
    <div className="surface-panel min-h-[382px] p-6 space-y-6">
      <div>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.35em] text-slate-400">Assessment</p>
            <p className="mt-3 text-sm text-slate-300">Risk Level: {activeRisk.level.toUpperCase()}</p>
            <h2 className="mt-1 text-3xl font-semibold text-white">{activeRisk.level.toUpperCase()}</h2>
          </div>
          <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${palette.badge}`}>
            {activeRisk.score}/100
          </span>
        </div>

        <p className="mt-4 text-sm text-slate-300">Score: {activeRisk.score}</p>

        <div className="mt-6 flex items-center gap-5">
          <div className="relative h-24 w-24 shrink-0 rounded-full p-2" style={ringStyle}>
            <div className="flex h-full w-full items-center justify-center rounded-full bg-slate-950 text-xl font-bold text-white">
              {activeRisk.score}
            </div>
          </div>

          <div className="flex-1">
            <div className="mb-3 h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${palette.glow}`}
                style={{ width: `${Math.min(activeRisk.score, 100)}%` }}
              />
            </div>
            <p className="text-sm text-slate-300">
              {activeRisk.level === 'high'
                ? 'High risk clauses were detected in the agreement.'
                : activeRisk.level === 'medium'
                  ? 'Several moderate-risk provisions warrant review.'
                  : 'Most clauses appear balanced and low-risk.'}
            </p>
          </div>
        </div>
      </div>

      {activeRisk.reasons.length > 0 && (
        <div className="border-t border-slate-800 pt-5">
          <h3 className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Key findings</h3>
          <ul className="mt-4 space-y-3">
            {activeRisk.reasons.map(reason => (
              <li key={reason} className="flex items-start gap-3 text-sm text-slate-200">
                <span className={`mt-1 h-2.5 w-2.5 rounded-full ${palette.ring}`} />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {clauses.length > 0 && (
        <div className="border-t border-slate-800 pt-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Detected Clauses ({clauses.length})</h3>
            <span className="text-xs text-sky-400 font-mono">NLP extraction</span>
          </div>
          <div className="mt-3 space-y-2 max-h-48 overflow-y-auto pr-1">
            {clauses.map((c, i) => (
              <div key={`${c.clause_type}-${i}`} className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5 text-xs">
                <div className="flex items-center justify-between font-semibold text-slate-200">
                  <span className="capitalize">{c.clause_type.replace(/_/g, ' ')}</span>
                  <span className="text-[10px] text-slate-400 font-mono">{(c.confidence * 100).toFixed(0)}% conf</span>
                </div>
                {c.text && (
                  <p className="mt-1 line-clamp-2 text-slate-400 italic">
                    "{c.text}"
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {entities.length > 0 && (
        <div className="border-t border-slate-800 pt-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-400">Extracted Entities ({entities.length})</h3>
            <span className="text-xs text-indigo-400 font-mono">spaCy NER</span>
          </div>
          <div className="mt-3 flex flex-wrap gap-2 max-h-40 overflow-y-auto pr-1">
            {entities.map((e, i) => {
              const badgeStyle = entityBadgeColors[e.entity_type] || 'border-slate-700 bg-slate-800 text-slate-300'
              return (
                <div
                  key={`${e.text}-${i}`}
                  className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs ${badgeStyle}`}
                  title={`${e.entity_type.toUpperCase()} (p. ${e.page_number}) - ${(e.confidence * 100).toFixed(0)}%`}
                >
                  <span className="font-medium text-white">{e.text}</span>
                  <span className="text-[10px] opacity-75 uppercase font-mono">[{e.entity_type}]</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
