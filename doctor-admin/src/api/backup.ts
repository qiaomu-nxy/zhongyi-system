import api from './index'

export const exportExcel = () =>
  api.get('/api/v1/backup/export-excel', { responseType: 'blob' })

export const downloadDb = () =>
  api.get('/api/v1/backup/download-db', { responseType: 'blob' })

export const exportPatientRecord = (patientId: number) =>
  api.get(`/api/v1/backup/patients/${patientId}/export`, { responseType: 'blob' })
