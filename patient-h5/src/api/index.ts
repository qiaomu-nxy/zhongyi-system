import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 15000,
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (!err.response) {
      return Promise.reject(new Error('网络异常，请检查网络连接'))
    }
    const msg = err.response.data?.detail || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

export default api