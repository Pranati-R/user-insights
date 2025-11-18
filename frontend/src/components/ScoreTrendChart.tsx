import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { SessionSummary } from '../types'

type Props = {
  sessions: SessionSummary[]
}

const ScoreTrendChart = ({ sessions }: Props) => {
  if (!sessions.length) return <div className="card">No session data yet.</div>

  const data = sessions.map((session) => ({
    name: new Date(session.start_ts).toLocaleTimeString(),
    score: session.anomaly_score ?? 0,
  }))

  return (
    <div className="card h-64">
      <div className="mb-2 text-sm text-slate-400">Anomaly score trend</div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="name" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" domain={[0, 'dataMax']} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
            labelStyle={{ color: '#cbd5f5' }}
          />
          <Line type="monotone" dataKey="score" stroke="#f43f5e" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ScoreTrendChart


