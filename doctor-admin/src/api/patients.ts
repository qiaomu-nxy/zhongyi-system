import api from './index'

export interface Patient {
  id: number
  name: string
  phone: string
  gender: string | null
  birth_date: string | null
  medical_history: string[]
  allergy_history: string | null
  is_active: boolean
  created_at: string
}

export interface PatientCreate {
  name: string
  phone: string
  gender?: string
  birth_date?: string
  medical_history?: string[]
  allergy_history?: string
}

export const getPatients = (params?: { search?: string; skip?: number; limit?: number }) =>
  api.get<Patient[]>('/api/v1/patients', { params })

export const getPatient = (id: number) =>
  api.get<Patient>(`/api/v1/patients/${id}`)

export const createPatient = (data: PatientCreate) =>
  api.post<Patient>('/api/v1/patients', data)

export const updatePatient = (id: number, data: Partial<PatientCreate>) =>
  api.put<Patient>(`/api/v1/patients/${id}`, data)

export const getPatientHistory = (id: number) =>
  api.get(`/api/v1/patients/${id}/history`)

export const addPatientHistory = (id: number, data: object) =>
  api.post(`/api/v1/patients/${id}/history`, data)

export const getPatientLabResults = (id: number) =>
  api.get(`/api/v1/patients/${id}/lab-results`)

export const getPatientAppointments = (id: number) =>
  api.get(`/api/v1/appointments/patient/${id}`)

export const exportPatient = (id: number) =>
  api.get(`/api/v1/backup/patients/${id}/export`, { responseType: 'blob' })
