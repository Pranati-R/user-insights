import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import type { AnalyticsSummary } from '../types'

const TopPagesChart = ({ summary }: { summary: AnalyticsSummary }) => {
  if (!summary.top_pages.length) {
    return <div className="card">No page data yet.</div>
  }

  const data = summary.top_pages.map((page) => ({
    name: page.page || '/',
    count: page.count,
  }))

  return (
    <div className="card h-64">
      <p className="text-sm text-slate-400">Top pages</p>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="name" stroke="#64748b" />
          <YAxis stroke="#64748b" />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
            labelStyle={{ color: '#f8fafc' }}
          />
          <Bar dataKey="count" fill="#f97316" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default TopPagesChart

