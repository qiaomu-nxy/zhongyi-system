import api from './index'

export const doctorLogin = (username: string, password: string) =>
  api.post('/api/v1/auth/doctor/login', { username, password })

export const patientLogin = (phone: string, name: string) =>
  api.post('/api/v1/auth/patient/login', { phone, name })