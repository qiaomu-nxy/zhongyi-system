import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePatientStore = defineStore('patient', () => {
  const patientId = ref<number | null>(null)
  const name = ref('')
  const visitCount = ref(0)

  function setPatient(id: number, n: string, count: number) {
    patientId.value = id
    name.value = n
    visitCount.value = count
    localStorage.setItem('patient_id', String(id))
    localStorage.setItem('patient_name', n)
  }

  function loadFromStorage() {
    const id = localStorage.getItem('patient_id')
    const n = localStorage.getItem('patient_name')
    if (id && n) {
      patientId.value = Number(id)
      name.value = n
    }
  }

  function logout() {
    patientId.value = null
    name.value = ''
    visitCount.value = 0
    localStorage.removeItem('patient_id')
    localStorage.removeItem('patient_name')
  }

  return { patientId, name, visitCount, setPatient, loadFromStorage, logout }
})