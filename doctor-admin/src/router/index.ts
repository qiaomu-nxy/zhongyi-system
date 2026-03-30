import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
        { path: 'patients', name: 'PatientList', component: () => import('@/views/PatientList.vue') },
        { path: 'patients/:id', name: 'PatientDetail', component: () => import('@/views/PatientDetail.vue') },
        { path: 'visits/:id/record', name: 'MedicalRecord', component: () => import('@/views/MedicalRecord.vue') },
        { path: 'appointments', name: 'AppointCalendar', component: () => import('@/views/AppointCalendar.vue') },
        { path: 'analysis', name: 'Analysis', component: () => import('@/views/Analysis.vue') },
        { path: 'backup', name: 'DataBackup', component: () => import('@/views/DataBackup.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('doctor_token')
  if (!to.meta.public && !token) {
    return '/login'
  }
  if (to.path === '/login' && token) {
    return '/dashboard'
  }
})

export default router
