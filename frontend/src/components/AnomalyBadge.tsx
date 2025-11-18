type Props = {
  isAnomalous?: boolean
  score?: number
}

const AnomalyBadge = ({ isAnomalous, score }: Props) => {
  if (isAnomalous === undefined) return null
  if (!isAnomalous)
    return (
      <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-xs text-emerald-300">
        Normal
      </span>
    )
  return (
    <span className="rounded-full bg-rose-500/10 px-2 py-1 text-xs text-rose-300">
      Anomaly {score ? `(${score.toFixed(2)})` : null}
    </span>
  )
}

export default AnomalyBadge


