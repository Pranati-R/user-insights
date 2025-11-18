import api from './api'
import type {
  AnalyticsSummary,
  EventDTO,
  SessionSummary,
  AnomalyDetail,
  UploadAnalyticsResponse,
} from '../types'

export const fetchSummary = async () => {
  const { data } = await api.get<AnalyticsSummary>('/analytics/summary')
  return data
}

export const fetchEvents = async () => {
  const { data } = await api.get<{ events: EventDTO[] }>('/events')
  return data.events
}

export const fetchSessions = async () => {
  const { data } = await api.get<{ sessions: SessionSummary[] }>('/analytics/sessions')
  return data.sessions
}

export const fetchAnomalies = async () => {
  const { data } = await api.get<{ anomalies: SessionSummary[] }>('/analytics/anomalies')
  return data.anomalies
}

export const fetchSessionAnomaly = async (sessionId: string) => {
  const { data } = await api.get<AnomalyDetail>(`/analytics/sessions/${sessionId}/anomaly`)
  return data
}

export const uploadEventsFile = async (file: File) => {
  const body = new FormData()
  body.append('file', file)
  const { data } = await api.post<UploadAnalyticsResponse>('/upload-file', body, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

