import api from './index'

export const getSymptomTrend = (patientId: number) =>
  api.get(`/api/v1/analysis/patients/${patientId}/symptom-trend`)

export const getSymptomRadar = (patientId: number) =>
  api.get(`/api/v1/analysis/patients/${patientId}/radar`)

export const getTreatmentTimeline = (patientId: number) =>
  api.get(`/api/v1/analysis/patients/${patientId}/timeline`)

export const getLabTrend = (patientId: number) =>
  api.get(`/api/v1/analysis/patients/${patientId}/lab-trend`)
