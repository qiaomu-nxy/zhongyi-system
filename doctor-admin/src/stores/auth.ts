import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface DoctorInfo {
  doctor_id: number
  name: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('doctor_token'))
  const doctor = ref<DoctorInfo | null>(
    JSON.parse(localStorage.getItem('doctor_info') || 'null')
  )

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => doctor.value?.role === 'admin')

  function login(accessToken: string, info: DoctorInfo) {
    token.value = accessToken
    doctor.value = info
    localStorage.setItem('doctor_token', accessToken)
    localStorage.setItem('doctor_info', JSON.stringify(info))
  }

  function logout() {
    token.value = null
    doctor.value = null
    localStorage.removeItem('doctor_token')
    localStorage.removeItem('doctor_info')
  }

  return { token, doctor, isLoggedIn, isAdmin, login, logout }
})
