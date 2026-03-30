import api from './index'

export interface Appointment {
  id: number
  patient_id: number
  appointment_date: string
  time_slot: string
  status: string
  cancel_reason: string | null
  created_at: string
  patient?: {
    id: number
    name: string
    phone: string
    gender: string | null
  }
}

export interface Slot {
  time_slot: string
  available: boolean
}

export const getAvailableSlots = (date: string) =>
  api.get<Slot[]>('/api/v1/appointments/available-slots', { params: { date } })

export const getAppointments = (params?: { date?: string; status?: string }) =>
  api.get<Appointment[]>('/api/v1/appointments', { params })

export const cancelAppointment = (id: number, data: { reason?: string; by_doctor?: boolean }) => {
  const endpoint = data.by_doctor
    ? `/api/v1/appointments/${id}/cancel-doctor`
    : `/api/v1/appointments/${id}/cancel`
  return api.put(endpoint, { cancel_reason: data.reason ?? null })
}

export const markNoShow = (id: number) =>
  api.put(`/api/v1/appointments/${id}/no-show`)
