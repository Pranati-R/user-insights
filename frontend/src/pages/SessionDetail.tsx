import { useQuery } from '@tanstack/react-query'
import type { SessionSummary } from '../types'
import { formatDate, formatDuration } from '../utils/format'
import AnomalyBadge from '../components/AnomalyBadge'
import { fetchSessionAnomaly } from '../services/analytics'

type Props = {
  session?: SessionSummary
}

const SessionDetail = ({ session }: Props) => {
  const sessionId = session?.session_id
  const { data: anomaly, isLoading } = useQuery({
    enabled: Boolean(sessionId),
    queryKey: ['session-anomaly', sessionId],
    queryFn: () => fetchSessionAnomaly(sessionId as string),
  })

  if (!session) return <div className="card">Select a session to inspect metrics.</div>

  const { metrics } = session
  const metricEntries = [
    ['Duration', formatDuration(metrics.duration_seconds)],
    ['Events', metrics.event_count.toString()],
    ['Click rate', `${(metrics.click_rate * 100).toFixed(1)}%`],
    ['Unique pages', metrics.unique_pages.toString()],
    ['Action diversity', metrics.action_diversity.toString()],
    ['Avg interval', formatDuration(metrics.avg_inter_event_seconds)],
  ]

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-400">Session</div>
          <div className="font-mono text-xs text-slate-200">{session.session_id}</div>
          <div className="text-sm text-slate-400 mt-1">
            {formatDate(session.start_ts)} → {formatDate(session.end_ts)}
          </div>
        </div>
        <AnomalyBadge
          isAnomalous={anomaly?.is_anomalous ?? session.is_anomalous}
          score={anomaly?.score ?? session.anomaly_score}
        />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {metricEntries.map(([label, value]) => (
          <div key={label} className="rounded-lg border border-slate-800 p-3">
            <div className="text-xs uppercase text-slate-500">{label}</div>
            <div className="mt-1 text-xl text-slate-50">{value}</div>
          </div>
        ))}
      </div>
      <div className="rounded-lg border border-slate-800 p-3">
        <div className="text-xs uppercase text-slate-500">Anomaly insights</div>
        {isLoading ? (
          <div className="mt-2 text-sm text-slate-400">Fetching anomaly score...</div>
        ) : anomaly ? (
          <div className="mt-2 text-sm text-slate-300">
            Score: <span className="font-semibold">{anomaly.score.toFixed(2)}</span>{' '}
            {anomaly.is_anomalous ? (
              <span className="text-rose-300">flagged as anomalous</span>
            ) : (
              <span className="text-emerald-300">considered normal</span>
            )}
         
          </div>
        ) : (
          <div className="mt-2 text-sm text-slate-400">No anomaly data available.</div>
        )}
      </div>
    </div>
  )
}

export default SessionDetail


