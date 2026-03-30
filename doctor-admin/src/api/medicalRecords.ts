import api from './index'

export interface MedicalRecord {
  id: number
  visit_id: number
  treatment_types: string[]
  prescription: string | null
  acupuncture_points: string[]
  tongue_diagnosis: string | null
  pulse_diagnosis: string | null
  physical_signs: string | null
  diagnosis: string | null
  syndrome_analysis: string | null
  treatment_plan: string | null
  notes: string | null
  created_at: string
}

export interface MedicalRecordCreate {
  treatment_types: string[]
  prescription?: string
  acupuncture_points?: string[]
  tongue_diagnosis?: string
  pulse_diagnosis?: string
  physical_signs?: string
  diagnosis?: string
  syndrome_analysis?: string
  treatment_plan?: string
  notes?: string
}

export const getMedicalRecord = (visitId: number) =>
  api.get<MedicalRecord>(`/api/v1/visits/${visitId}/medical-record`)

export const createMedicalRecord = (visitId: number, data: MedicalRecordCreate) =>
  api.post<MedicalRecord>(`/api/v1/visits/${visitId}/medical-record`, data)

export const updateMedicalRecord = (id: number, data: Partial<MedicalRecordCreate>) =>
  api.put<MedicalRecord>(`/api/v1/medical-records/${id}`, data)

export const addLabResult = (visitId: number, data: object) =>
  api.post(`/api/v1/visits/${visitId}/lab-results`, data)
