import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('doctor_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('doctor_token')
      localStorage.removeItem('doctor_info')
      window.location.href = '/login'
    } else if (err.response?.data?.detail) {
      ElMessage.error(err.response.data.detail)
    } else {
      ElMessage.error('网络异常，请检查网络连接')
    }
    return Promise.reject(err)
  }
)

export default api
