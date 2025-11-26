export type EventType = 'page_view' | 'click' | 'action' | 'scroll'

export interface UserPublic {
  id: string
  email: string
  name: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  user: UserPublic
}

export interface UserCredentials {
  email: string
  password: string
}

export interface UserRegistration extends UserCredentials {
  name: string
}

export interface EventDTO {
  id: string
  user_id: string
  session_id: string
  event_type: EventType
  timestamp: string
  page?: string
  website?: string
  metadata?: Record<string, unknown>
  scroll_depth?: number
}

export interface SessionMetrics {
  duration_seconds: number
  event_count: number
  click_rate: number
  unique_pages: number
  action_diversity: number
  avg_inter_event_seconds: number
  dwell_estimate_seconds: number
}

export interface SessionSummary {
  session_id: string
  user_id: string
  start_ts: string
  end_ts: string
  metrics: SessionMetrics
  anomaly_score?: number
  is_anomalous?: boolean
}

export interface AnalyticsSummary {
  total_events: number
  total_sessions: number
  anomaly_rate: number
  last_event_at: string | null
  top_pages: { page: string; count: number }[]
}

export interface AnomalyDetail {
  session_id: string
  score: number
  is_anomalous: boolean
  explanations?: Record<string, unknown>
}

export interface AnomalyBreakdown {
  total_anomalies: number
  anomaly_percentage: number
  top_anomalies: SessionSummary[]
  anomaly_reasons_summary: Record<string, number>
}

export interface ProcessingStats {
  total_events_in_file: number
  successfully_inserted: number
  failed_events: number
  success_rate: number
}

export interface UploadAnalyticsResponse {
  ingested_events: number
  summary: AnalyticsSummary
  anomaly_breakdown?: AnomalyBreakdown
  processing_stats?: ProcessingStats
}


