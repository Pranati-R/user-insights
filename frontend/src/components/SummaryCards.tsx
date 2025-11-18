import type { AnalyticsSummary } from '../types'
import { formatDate } from '../utils/format'

const SummaryCards = ({ summary }: { summary: AnalyticsSummary }) => {
  const cards = [
    { label: 'Total events', value: summary.total_events.toLocaleString() },
    { label: 'Total sessions', value: summary.total_sessions.toLocaleString() },
    { label: 'Anomaly rate', value: `${summary.anomaly_rate.toFixed(1)}%` },
    {
      label: 'Last event',
      value: summary.last_event_at ? formatDate(summary.last_event_at) : 'n/a',
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="card">
          <p className="text-xs uppercase tracking-widest text-slate-400">{card.label}</p>
          <p className="mt-2 text-3xl font-semibold text-white">{card.value}</p>
        </div>
      ))}
      <div className="card md:col-span-4">
        <p className="text-xs uppercase tracking-widest text-slate-400">Top pages</p>
        <div className="mt-3 grid gap-3 text-sm md:grid-cols-2 lg:grid-cols-3">
          {summary.top_pages.length === 0 ? (
            <p className="text-slate-400">Not enough traffic yet.</p>
          ) : (
            summary.top_pages.map((page) => (
              <div key={page.page} className="rounded-lg border border-slate-800 px-3 py-2">
                <p className="truncate text-slate-200">{page.page}</p>
                <p className="text-xs text-slate-500">{page.count} hits</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default SummaryCards

