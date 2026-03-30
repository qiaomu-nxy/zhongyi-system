import api from './index'

export const submitSymptoms = (visitId: number, symptoms: any[]) =>
  api.post(`/api/v1/visits/${visitId}/symptoms`, symptoms)
export const getSymptomConfig = () => api.get('/api/v1/config/symptoms')