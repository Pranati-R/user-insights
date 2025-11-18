import { useMemo } from 'react'
import { useAuth } from '../hooks/useAuth'

const TrackingScriptPage = () => {
  const { user } = useAuth()
  const base = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000')
    .replace(/\/api$/, '')
    .replace(/\/$/, '')

  const snippet = useMemo(() => {
    if (!user) return ''
    return `<script src="${base}/track.js?uid=${user.id}"></script>`
  }, [base, user])

  if (!user) return null

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold text-white">Install tracking script</h2>
        <p className="text-sm text-slate-400">
          Paste this snippet before the closing <code>&lt;/head&gt;</code> tag on your site to
          capture events automatically.
        </p>
      </div>
      <div className="relative rounded-2xl border border-slate-800 bg-slate-900/80 p-4 font-mono text-sm text-rose-200">
        <button
          className="absolute right-4 top-4 rounded-lg border border-rose-400 px-3 py-1 text-xs text-rose-200"
          onClick={() => navigator.clipboard.writeText(snippet)}
        >
          Copy
        </button>
        <pre className="whitespace-pre-wrap break-all">{snippet}</pre>
      </div>
      <ol className="space-y-2 text-sm text-slate-300">
        <li>1. Paste the snippet on every page of your site.</li>
        <li>2. Deploy and visit your site to verify events appear in the dashboard.</li>
        <li>3. Use the File Upload page to backfill historical events if needed.</li>
      </ol>
    </div>
  )
}

export default TrackingScriptPage

