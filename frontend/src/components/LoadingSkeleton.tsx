export function LoadingSkeleton() {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950/60 p-5">
      <div className="mb-5 flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-2.5 w-20 animate-pulse rounded-full bg-slate-700" />
          <div className="h-2.5 w-28 animate-pulse rounded-full bg-slate-700" />
        </div>
        <div className="h-10 w-24 animate-pulse rounded-xl bg-slate-700" />
      </div>

      <div className="space-y-3">
        <div className="h-3 w-full animate-pulse rounded-full bg-slate-700" />
        <div className="h-3 w-5/6 animate-pulse rounded-full bg-slate-700" />
        <div className="h-3 w-4/5 animate-pulse rounded-full bg-slate-700" />
        <div className="h-3 w-2/3 animate-pulse rounded-full bg-slate-700" />
      </div>
    </div>
  )
}
