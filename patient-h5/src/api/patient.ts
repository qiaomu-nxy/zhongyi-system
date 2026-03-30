import api from './index'

export const createPatient = (data: any) => api.post('/api/v1/patients', data)
export const getPatient = (id: number) => api.get(`/api/v1/patients/${id}`)
export const updatePatient = (id: number, data: any) => api.put(`/api/v1/patients/${id}`, data)
export const addHistory = (id: number, data: any) => api.post(`/api/v1/patients/${id}/history`, data)
export const getHistory = (id: number) => api.get(`/api/v1/patients/${id}/history`)