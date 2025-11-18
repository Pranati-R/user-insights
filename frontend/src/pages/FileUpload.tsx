import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { uploadEventsFile } from '../services/analytics'
import SummaryCards from '../components/SummaryCards'

const FileUploadPage = () => {
  const [file, setFile] = useState<File | null>(null)
  const mutation = useMutation({
    mutationFn: uploadEventsFile,
  })

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    if (file) {
      mutation.mutate(file)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Upload historical events</h2>
        <p className="text-sm text-slate-400">
          Import CSV or JSON exports to backfill analytics and anomaly detection.
        </p>
      </div>
      <form
        onSubmit={handleSubmit}
        className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/60 p-6"
      >
        <input
          type="file"
          accept=".csv,.json"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="block w-full text-sm text-slate-200 file:mr-4 file:rounded-full file:border-0 file:bg-rose-500 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-rose-400"
        />
        <button
          type="submit"
          disabled={!file || mutation.isPending}
          className="mt-4 rounded-lg bg-rose-500 px-4 py-2 font-semibold text-white hover:bg-rose-400 disabled:opacity-50"
        >
          {mutation.isPending ? 'Uploading...' : 'Upload & process'}
        </button>
      </form>

      {mutation.isError && (
        <p className="text-sm text-rose-400">Unable to parse file. Ensure it is valid CSV/JSON.</p>
      )}

      {mutation.data && (
        <div className="space-y-4">
          <div className="card">
            <p className="text-sm text-slate-400">Ingested events</p>
            <p className="mt-2 text-3xl font-semibold text-white">
              {mutation.data.ingested_events.toLocaleString()}
            </p>
          </div>
          <SummaryCards summary={mutation.data.summary} />
        </div>
      )}
    </div>
  )
}

export default FileUploadPage

