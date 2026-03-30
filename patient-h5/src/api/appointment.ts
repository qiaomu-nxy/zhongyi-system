import api from './index'

export const getAvailableSlots = (date: string) =>
  api.get('/api/v1/appointments/available-slots', { params: { date } })
export const createAppointment = (data: any) => api.post('/api/v1/appointments', data)
export const getMyAppointments = (patientId: number) =>
  api.get(`/api/v1/appointments/patient/${patientId}`)
export const cancelAppointment = (id: number, reason?: string) =>
  api.put(`/api/v1/appointments/${id}/cancel`, { cancel_reason: reason })