import api from './index'

export const getVisits = (patientId: number) =>
  api.get('/api/v1/visits', { params: { patient_id: patientId } })
export const checkIn = (visitId: number) => api.put(`/api/v1/visits/${visitId}/check-in`)