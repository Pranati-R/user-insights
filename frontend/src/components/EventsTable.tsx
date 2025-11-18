import type { EventDTO } from '../types'
import { formatDate } from '../utils/format'

type Props = {
  events: EventDTO[]
}

const EventBadge = ({ type }: { type: EventDTO['event_type'] }) => {
  const colors: Record<EventDTO['event_type'], string> = {
    page_view: 'bg-sky-500/10 text-sky-300',
    click: 'bg-emerald-500/10 text-emerald-300',
    action: 'bg-violet-500/10 text-violet-300',
    scroll: 'bg-amber-500/10 text-amber-300',
  }
  return (
    <span className={`rounded-full px-2 py-1 text-xs ${colors[type] ?? 'bg-slate-700'}`}>
      {type.replace('_', ' ')}
    </span>
  )
}

const EventsTable = ({ events }: Props) => {
  if (!events.length) {
    return <div className="card text-sm text-slate-400">No events yet.</div>
  }

  return (
    <div className="card overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="text-slate-400">
          <tr>
            <th className="px-2 py-2 font-medium">Type</th>
            <th className="px-2 py-2 font-medium">Page</th>
            <th className="px-2 py-2 font-medium">Session</th>
            <th className="px-2 py-2 font-medium">When</th>
            <th className="px-2 py-2 font-medium">Metadata</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id} className="border-t border-slate-800">
              <td className="px-2 py-3">
                <EventBadge type={event.event_type} />
              </td>
              <td className="px-2 py-3 font-mono text-xs">{event.page ?? event.website ?? '—'}</td>
              <td className="px-2 py-3 font-mono text-xs">{event.session_id}</td>
              <td className="px-2 py-3">{formatDate(event.timestamp)}</td>
              <td className="px-2 py-3 text-xs text-slate-400">
                {event.metadata
                  ? JSON.stringify(event.metadata).slice(0, 80)
                  : 'no metadata'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default EventsTable

