import { ResponsiveContainer, LineChart, Line, YAxis, XAxis, Tooltip } from 'recharts'
import type { EventDTO } from '../types'

const EventsTrendChart = ({ events }: { events: EventDTO[] }) => {
  if (!events.length) return <div className="card">No events to display.</div>

  const buckets = events.reduce<Record<string, number>>((acc, event) => {
    const date = new Date(event.timestamp)
    date.setSeconds(0, 0)
    const key = date.toISOString()
    acc[key] = (acc[key] ?? 0) + 1
    return acc
  }, {})

  const data = Object.entries(buckets)
    .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
    .slice(-20)
    .map(([iso, count]) => {
      const date = new Date(iso)
      const label = `${date.getHours().toString().padStart(2, '0')}:${date
        .getMinutes()
        .toString()
        .padStart(2, '0')}`
      return { time: label, count }
    })

  return (
    <div className="card h-64">
      <p className="text-sm text-slate-400">Events per minute</p>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="time" stroke="#64748b" />
          <YAxis stroke="#64748b" allowDecimals={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
            labelStyle={{ color: '#f8fafc' }}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={{ r: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default EventsTrendChart

