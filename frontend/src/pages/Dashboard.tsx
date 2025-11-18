import { useMemo, useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import SummaryCards from '../components/SummaryCards'
import EventsTrendChart from '../components/EventsTrendChart'
import TopPagesChart from '../components/TopPagesChart'
import ScoreTrendChart from '../components/ScoreTrendChart'
import SessionTable from '../components/SessionTable'
import EventsTable from '../components/EventsTable'
import SessionDetail from './SessionDetail'
import {
  fetchSummary,
  fetchEvents,
  fetchSessions,
  fetchAnomalies,
} from '../services/analytics'
import type { SessionSummary } from '../types'

const Dashboard = () => {
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['summary'],
    queryFn: fetchSummary,
  })
  const { data: events = [], isLoading: loadingEvents } = useQuery({
    queryKey: ['events'],
    queryFn: fetchEvents,
  })
  const { data: sessions = [], isLoading: loadingSessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: fetchSessions,
  })
  const { data: anomalies = [] } = useQuery({
    queryKey: ['anomalies'],
    queryFn: fetchAnomalies,
  })

  const [selectedSessionId, setSelectedSessionId] = useState<string>()

  useEffect(() => {
    if (!sessions.length) {
      setSelectedSessionId(undefined)
      return
    }
    const stillExists = sessions.some((session) => session.session_id === selectedSessionId)
    if (!selectedSessionId || !stillExists) {
      setSelectedSessionId(sessions[0].session_id)
    }
  }, [sessions, selectedSessionId])

  const selectedSession = useMemo<SessionSummary | undefined>(
    () => sessions.find((session) => session.session_id === selectedSessionId),
    [sessions, selectedSessionId],
  )

  if (loadingSummary || !summary) {
    return <div className="card">Loading analytics...</div>
  }

  return (
    <div className="space-y-6">
      <SummaryCards summary={summary} />

      <div className="grid gap-4 md:grid-cols-2">
        <EventsTrendChart events={events.slice(0, 200)} />
        <TopPagesChart summary={summary} />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <ScoreTrendChart sessions={sessions} />
        <SessionDetail session={selectedSession} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div>
          <h3 className="mb-2 text-sm uppercase tracking-widest text-slate-400">Sessions</h3>
          {loadingSessions ? (
            <div className="card">Loading sessions...</div>
          ) : (
            <SessionTable
              sessions={sessions}
              selected={selectedSessionId}
              onSelect={setSelectedSessionId}
            />
          )}
        </div>
        <div>
          <h3 className="mb-2 text-sm uppercase tracking-widest text-slate-400">Anomalies</h3>
          <SessionTable
            sessions={anomalies}
            selected={selectedSessionId}
            onSelect={setSelectedSessionId}
          />
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm uppercase tracking-widest text-slate-400">Recent events</h3>
        {loadingEvents ? <div className="card">Loading events...</div> : <EventsTable events={events} />}
      </div>
    </div>
  )
}

export default Dashboard

