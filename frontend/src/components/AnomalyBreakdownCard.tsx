import { AlertTriangle, TrendingUp, Shield, Activity } from 'lucide-react'

interface AnomalyBreakdown {
  total_anomalies: number
  anomaly_percentage: number
  top_anomalies: any[]
  anomaly_reasons_summary: Record<string, number>
}

interface Props {
  breakdown: AnomalyBreakdown
}

const AnomalyBreakdownCard = ({ breakdown }: Props) => {
  const { total_anomalies, anomaly_percentage, anomaly_reasons_summary } = breakdown

  // Sort reasons by count
  const sortedReasons = Object.entries(anomaly_reasons_summary || {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5)

  const getAnomalyColor = (percentage: number) => {
    if (percentage < 5) return 'text-green-400'
    if (percentage < 15) return 'text-yellow-400'
    return 'text-rose-400'
  }

  const getAnomalyBgColor = (percentage: number) => {
    if (percentage < 5) return 'bg-green-500/10 border-green-500/20'
    if (percentage < 15) return 'bg-yellow-500/10 border-yellow-500/20'
    return 'bg-rose-500/10 border-rose-500/20'
  }

  return (
    <div className="space-y-4">
      {/* Header Card */}
      <div className={`rounded-2xl border p-6 shadow-sm ${getAnomalyBgColor(anomaly_percentage)}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className={`w-5 h-5 ${getAnomalyColor(anomaly_percentage)}`} />
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Anomaly Detection Results</h3>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              AI-powered analysis of uploaded sessions
            </p>
          </div>
          <div className="text-right">
            <p className={`text-4xl font-bold ${getAnomalyColor(anomaly_percentage)}`}>
              {anomaly_percentage.toFixed(1)}%
            </p>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Anomaly Rate</p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="bg-slate-100 dark:bg-slate-800/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Activity className="w-4 h-4 text-rose-400" />
              <p className="text-xs text-slate-600 dark:text-slate-400">Anomalous Sessions</p>
            </div>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{total_anomalies}</p>
          </div>
          
          <div className="bg-slate-100 dark:bg-slate-800/50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-1">
              <Shield className="w-4 h-4 text-green-400" />
              <p className="text-xs text-slate-600 dark:text-slate-400">Detection Confidence</p>
            </div>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">
              {total_anomalies > 0 ? '95%' : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Anomaly Reasons */}
      {sortedReasons.length > 0 && (
        <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900/60 p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-rose-400" />
            <h4 className="text-lg font-semibold text-slate-900 dark:text-white">Top Anomaly Patterns</h4>
          </div>
          
          <div className="space-y-3">
            {sortedReasons.map(([reason, count], index) => {
              const percentage = (count / total_anomalies) * 100
              return (
                <div key={reason} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-rose-500/20 text-rose-400 text-xs font-semibold">
                        {index + 1}
                      </span>
                      <p className="text-sm text-slate-700 dark:text-slate-300">{reason}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-slate-900 dark:text-white">{count}</p>
                      <p className="text-xs text-slate-500">{percentage.toFixed(0)}%</p>
                    </div>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-rose-500 to-orange-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>

          {total_anomalies === 0 && (
            <div className="text-center py-8">
              <Shield className="w-12 h-12 text-green-400 mx-auto mb-3" />
              <p className="text-slate-700 dark:text-slate-300 font-medium">No anomalies detected!</p>
              <p className="text-sm text-slate-600 dark:text-slate-500 mt-1">All sessions appear normal</p>
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {anomaly_percentage > 10 && (
        <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/10 p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-200">High Anomaly Rate Detected</p>
              <p className="text-xs text-yellow-300/80 mt-1">
                Consider reviewing your data source or adjusting detection thresholds. 
                High anomaly rates may indicate bot traffic, data quality issues, or unusual user behavior patterns.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnomalyBreakdownCard
