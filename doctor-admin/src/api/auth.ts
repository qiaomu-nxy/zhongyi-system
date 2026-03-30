import api from './index'

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  doctor: {
    id: number
    username: string
    name: string
    role: string
  }
}

export const doctorLogin = (data: LoginPayload) =>
  api.post<LoginResponse>('/api/v1/auth/doctor/login', data)
