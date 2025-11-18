import type { SessionSummary } from '../types'
import { formatDate, formatDuration } from '../utils/format'
import AnomalyBadge from './AnomalyBadge'

type Props = {
  sessions: SessionSummary[]
  selected?: string
  onSelect: (sessionId: string) => void
}

const SessionTable = ({ sessions, selected, onSelect }: Props) => {
  if (!sessions.length) return <div className="card">No sessions found</div>

  return (
    <div className="card overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="text-slate-400">
          <tr>
            <th className="px-2 py-2 font-medium">User</th>
            <th className="px-2 py-2 font-medium">Start</th>
            <th className="px-2 py-2 font-medium">Duration</th>
            <th className="px-2 py-2 font-medium">Events</th>
            <th className="px-2 py-2 font-medium">Click rate</th>
            <th className="px-2 py-2 font-medium">Anomaly</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((session) => (
            <tr
              key={session.session_id}
              onClick={() => onSelect(session.session_id)}
              className={`cursor-pointer border-t border-slate-800 hover:bg-slate-900/60 ${
                selected === session.session_id ? 'bg-slate-900/80' : ''
              }`}
            >
              <td className="px-2 py-3 font-mono text-xs">{session.user_id}</td>
              <td className="px-2 py-3">{formatDate(session.start_ts)}</td>
              <td className="px-2 py-3">{formatDuration(session.metrics.duration_seconds)}</td>
              <td className="px-2 py-3">{session.metrics.event_count}</td>
              <td className="px-2 py-3">{(session.metrics.click_rate * 100).toFixed(1)}%</td>
              <td className="px-2 py-3">
                <AnomalyBadge isAnomalous={session.is_anomalous} score={session.anomaly_score} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default SessionTable

