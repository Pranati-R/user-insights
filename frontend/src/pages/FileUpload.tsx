import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { uploadEventsFile } from '../services/analytics'
import SummaryCards from '../components/SummaryCards'

const MAX_FILE_SIZE_MB = 10 // limit for safety

const FileUploadPage = () => {
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: uploadEventsFile,
    onError: () => {
      setError("Unable to parse file. Ensure it is valid CSV or JSON.")
    }
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    setError(null)

    if (!selected) return

    // Validate file type
    if (!["text/csv", "application/json"].includes(selected.type) &&
        !selected.name.endsWith(".csv") &&
        !selected.name.endsWith(".json")
    ) {
      setError("Only .csv or .json files are allowed.")
      return
    }

    // Validate file size
    if (selected.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError(`File too large. Max allowed is ${MAX_FILE_SIZE_MB}MB.`)
      return
    }

    setFile(selected)
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    if (file) {
      setError(null)
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
        className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/60 p-6 space-y-4"
      >
        <input
          type="file"
          accept=".csv,.json"
          onChange={handleFileSelect}
          className="block w-full text-sm text-slate-200 file:mr-4 file:rounded-full file:border-0 file:bg-rose-500 
                     file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-rose-400"
        />

        {error && <p className="text-sm text-rose-400">{error}</p>}

        <button
          type="submit"
          disabled={!file || mutation.isPending}
          className="w-full rounded-lg bg-rose-500 px-4 py-2 font-semibold text-white hover:bg-rose-400 
                     disabled:opacity-50 flex items-center justify-center"
        >
          {mutation.isPending ? (
            <span className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
          ) : (
            "Upload & process"
          )}
        </button>
      </form>

      {mutation.data && !mutation.isError && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-800 border border-slate-700">
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
