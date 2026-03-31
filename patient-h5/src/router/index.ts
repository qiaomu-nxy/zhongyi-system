import { createRouter, createWebHistory } from 'vue-router'
import { usePatientStore } from '../stores/patient'

const routes = [
  { path: '/', redirect: '/records' },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/info', component: () => import('../views/PatientInfo.vue') },
  { path: '/appointment', component: () => import('../views/Appointment.vue'), meta: { requiresAuth: true } },
  { path: '/symptoms', component: () => import('../views/SymptomForm.vue'), meta: { requiresAuth: true } },
  { path: '/records', component: () => import('../views/MyRecords.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const store = usePatientStore()
  store.loadFromStorage()
  if (to.meta.requiresAuth && !store.patientId) {
    return '/login'
  }
})

export default router