import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { uploadEventsFile } from '../services/analytics'
import SummaryCards from '../components/SummaryCards'
import AnomalyBreakdownCard from '../components/AnomalyBreakdownCard'
import { CheckCircle, XCircle, TrendingUp } from 'lucide-react'

const MAX_FILE_SIZE_MB = 50 // Increased limit for larger log files

const SUPPORTED_EXTENSIONS = ['.csv', '.json', '.psi', '.tsv', '.txt', '.log']

const FileUploadPage = () => {
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: uploadEventsFile,
    onError: (error: any) => {
      const errorMsg = error?.response?.data?.detail || error?.message || "Unable to parse file"
      setError(`Upload failed: ${errorMsg}`)
    }
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    setError(null)

    if (!selected) return

    // Validate file type - check extension
    const fileName = selected.name.toLowerCase()
    const hasValidExtension = SUPPORTED_EXTENSIONS.some(ext => fileName.endsWith(ext))
    
    if (!hasValidExtension) {
      setError(`Unsupported file type. Supported formats: ${SUPPORTED_EXTENSIONS.join(', ')}`)
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
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">Upload historical events</h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Import logs in multiple formats (CSV, JSON, PSI, TSV, TXT, LOG) with AI-powered parsing.
          The system intelligently detects delimiters and normalizes different log structures.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-6 shadow-sm"
      >
        <div className="space-y-2">
          <input
            type="file"
            accept=".csv,.json,.psi,.tsv,.txt,.log"
            onChange={handleFileSelect}
            className="block w-full rounded-lg border border-slate-300 dark:border-slate-700 
                       bg-slate-50 dark:bg-slate-800 px-4 py-2 text-sm 
                       text-slate-700 dark:text-slate-300 file:mr-4 file:rounded-md file:border-0 
                       file:bg-rose-500 file:px-4 file:py-2 file:text-sm file:font-semibold 
                       file:text-white hover:file:bg-rose-400 transition-colors"
          />
          <p className="text-xs text-slate-500">
            Supported: CSV (comma), PSI (pipe), TSV (tab), JSON, and custom delimiters
          </p>
        </div>

        {file && <p className="mt-2 text-xs text-slate-600 dark:text-slate-500">Selected: {file.name}</p>}

        {error && (
          <div className="rounded-lg bg-rose-500/10 border border-rose-500/20 p-4">
            <p className="text-sm text-rose-600 dark:text-rose-300">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || mutation.isPending}
          className="w-full rounded-lg bg-rose-500 px-4 py-2 font-semibold text-white hover:bg-rose-400 
                     disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center 
                     transition-all shadow-sm hover:shadow-md"
        >
          {mutation.isPending ? (
            <span className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
          ) : (
            "Upload & process"
          )}
        </button>
      </form>

      {mutation.data && !mutation.isError && (
        <div className="space-y-6">
          {/* Processing Stats */}
          {mutation.data.processing_stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <p className="text-sm text-slate-600 dark:text-slate-400">Successfully Processed</p>
                </div>
                <p className="text-3xl font-semibold text-slate-900 dark:text-white">
                  {mutation.data.processing_stats.successfully_inserted.toLocaleString()}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  {mutation.data.processing_stats.success_rate.toFixed(1)}% success rate
                </p>
              </div>

              {mutation.data.processing_stats.failed_events > 0 && (
                <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <XCircle className="w-4 h-4 text-rose-400" />
                    <p className="text-sm text-slate-600 dark:text-slate-400">Failed Events</p>
                  </div>
                  <p className="text-3xl font-semibold text-rose-400">
                    {mutation.data.processing_stats.failed_events.toLocaleString()}
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-500 mt-1">
                    Check data format
                  </p>
                </div>
              )}

              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-blue-400" />
                  <p className="text-sm text-slate-600 dark:text-slate-400">Total in File</p>
                </div>
                <p className="text-3xl font-semibold text-blue-400">
                  {mutation.data.processing_stats.total_events_in_file.toLocaleString()}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Events detected
                </p>
              </div>
            </div>
          )}

          {/* Anomaly Breakdown */}
          {mutation.data.anomaly_breakdown && (
            <AnomalyBreakdownCard breakdown={mutation.data.anomaly_breakdown} />
          )}

          {/* Summary Cards */}
          <SummaryCards summary={mutation.data.summary} />
        </div>
      )}
    </div>
  )
}

export default FileUploadPage
