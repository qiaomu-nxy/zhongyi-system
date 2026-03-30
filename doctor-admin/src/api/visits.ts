import api from './index'

export interface TodayStats {
  total: number
  waiting: number
  completed: number
  new_patients: number
  return_patients: number
  visits: Visit[]
}

export interface Visit {
  id: number
  patient_id: number
  visit_date: string
  visit_number: number
  status: string
  chief_complaint: string | null
  symptom_submitted_at: string | null
  created_at: string
  patient?: {
    id: number
    name: string
    gender: string | null
    birth_date: string | null
    phone: string
  }
}

export const getTodayVisits = () =>
  api.get<TodayStats>('/api/v1/visits/today')

export const getVisits = (params?: { date?: string; status?: string; patient_id?: number }) =>
  api.get<Visit[]>('/api/v1/visits', { params })

export const getVisit = (id: number) =>
  api.get<Visit>(`/api/v1/visits/${id}`)

export const createVisit = (data: { patient_id: number; chief_complaint?: string }) =>
  api.post<Visit>('/api/v1/visits', data)

export const checkIn = (id: number) =>
  api.put(`/api/v1/visits/${id}/check-in`)

export const updateVisitStatus = (id: number, status: string) =>
  api.put(`/api/v1/visits/${id}/status`, { status })

export const getVisitSymptoms = (id: number) =>
  api.get(`/api/v1/visits/${id}/symptoms`)
