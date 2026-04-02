<template>
  <div class="page">
    <!-- 顶部患者信息 -->
    <div class="patient-header">
      <div class="avatar">{{ store.name.slice(0, 1) }}</div>
      <div class="info">
        <p class="pname">{{ store.name }}</p>
        <p class="pcount">累计就诊 {{ store.visitCount }} 次</p>
      </div>
      <van-button size="small" plain @click="router.push('/appointment')">预约就诊</van-button>
    </div>

    <van-tabs v-model:active="activeTab" sticky>
      <!-- 就诊记录 -->
      <van-tab title="就诊记录">
        <van-pull-refresh v-model="refreshingVisits" @refresh="loadVisits">
          <van-empty v-if="!visits.length && !loadingVisits" description="暂无就诊记录" />
          <van-loading v-else-if="loadingVisits" size="24px" class="loading" />
          <div v-else class="timeline">
            <div v-for="v in visits" :key="v.id" class="timeline-item" @click="toggleVisit(v.id)">
              <div class="tl-dot" :class="v.status === '已完成' ? 'done' : 'pending'" />
              <div class="tl-content">
                <div class="tl-header">
                  <span class="tl-num">第 {{ v.visit_number }} 次就诊</span>
                  <van-tag :type="v.status === '已完成' ? 'success' : 'primary'" size="small">{{ v.status }}</van-tag>
                </div>
                <p class="tl-date">{{ v.visit_date }}</p>
                <div v-if="expandedVisit === v.id && v.record" class="tl-detail">
                  <p v-if="v.record.diagnosis"><b>诊断：</b>{{ v.record.diagnosis }}</p>
                  <p v-if="v.record.treatment_plan"><b>治疗方案：</b>{{ v.record.treatment_plan }}</p>
                  <p v-if="v.record.notes"><b>医嘱：</b>{{ v.record.notes }}</p>
                </div>
              </div>
            </div>
          </div>
        </van-pull-refresh>
      </van-tab>

      <!-- 预约记录 -->
      <van-tab title="预约记录">
        <van-pull-refresh v-model="refreshingApts" @refresh="loadAppointments">
          <van-empty v-if="!appointments.length && !loadingApts" description="暂无预约记录" />
          <van-loading v-else-if="loadingApts" size="24px" class="loading" />
          <div v-else class="apt-list">
            <div v-for="a in appointments" :key="a.id" class="apt-card">
              <div class="apt-info">
                <p class="apt-date">{{ a.appointment_date }} &nbsp;<b>{{ a.time_slot }}</b></p>
                <van-tag :type="aptTagType(a.status)" size="small">{{ a.status }}</van-tag>
              </div>
              <van-button
                v-if="a.status === '待就诊' && canCancel(a.appointment_date, a.time_slot)"
                size="small"
                plain
                type="danger"
                @click="handleCancel(a.id)"
              >取消预约</van-button>
              <p v-if="a.status === '待就诊' && !canCancel(a.appointment_date, a.time_slot)" class="today-tip">
                距就诊不足2小时，请按时到店
              </p>
            </div>
          </div>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 底部导航 -->
    <van-tabbar>
      <van-tabbar-item icon="home-o" @click="activeTab = 0">就诊</van-tabbar-item>
      <van-tabbar-item icon="calendar-o" @click="router.push('/appointment')">预约</van-tabbar-item>
      <van-tabbar-item icon="user-o" @click="router.push('/info')">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { getVisits } from '../api/visit'
import { getMyAppointments, cancelAppointment } from '../api/appointment'
import { usePatientStore } from '../stores/patient'

const router = useRouter()
const store = usePatientStore()

const activeTab = ref(0)
const visits = ref<any[]>([])
const appointments = ref<any[]>([])
const expandedVisit = ref<number | null>(null)
const loadingVisits = ref(false)
const loadingApts = ref(false)
const refreshingVisits = ref(false)
const refreshingApts = ref(false)

function toggleVisit(id: number) {
  expandedVisit.value = expandedVisit.value === id ? null : id
}

function aptTagType(status: string) {
  return { 待就诊: 'primary', 已完成: 'success', 已取消: 'default', 爽约: 'danger' }[status] || 'default'
}

function canCancel(date: string, timeSlot: string) {
  const aptTime = new Date(`${date}T${timeSlot}:00`)
  const twoHoursBefore = new Date(aptTime.getTime() - 2 * 60 * 60 * 1000)
  return new Date() < twoHoursBefore
}

async function loadVisits() {
  loadingVisits.value = true
  try {
    const res: any = await getVisits(store.patientId!)
    visits.value = res
    store.visitCount = res.length
  } finally {
    loadingVisits.value = false
    refreshingVisits.value = false
  }
}

async function loadAppointments() {
  loadingApts.value = true
  try {
    const res: any = await getMyAppointments(store.patientId!)
    appointments.value = res
  } finally {
    loadingApts.value = false
    refreshingApts.value = false
  }
}

async function handleCancel(id: number) {
  await showConfirmDialog({ title: '确认取消', message: '取消后时段立即释放，可重新预约' })
  try {
    await cancelAppointment(id)
    showToast('已取消')
    loadAppointments()
  } catch (e: any) {
    showToast(e.message)
  }
}

onMounted(() => {
  loadVisits()
  loadAppointments()
})
</script>

<style scoped>
.page { width: 100%; overflow-x: hidden; background: var(--color-bg); min-height: 100vh; padding-bottom: 60px; }
.patient-header {
  display: flex; align-items: center; gap: 12px;
  background: var(--color-primary); color: #fff;
  padding: 20px 16px;
}
.avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.25);
  font-size: 18px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.info { flex: 1; }
.pname { font-size: 16px; font-weight: 600; }
.pcount { font-size: 13px; opacity: 0.8; margin-top: 2px; }
.loading { display: flex; justify-content: center; padding: 32px; }
.timeline { padding: 16px; }
.timeline-item { display: flex; gap: 12px; margin-bottom: 20px; cursor: pointer; }
.tl-dot {
  width: 12px; height: 12px; border-radius: 50%; margin-top: 4px; flex-shrink: 0;
  border: 2px solid var(--color-primary);
}
.tl-dot.done { background: var(--color-primary); }
.tl-dot.pending { background: #fff; }
.tl-content { flex: 1; background: var(--color-card); border-radius: 12px; padding: 12px; box-shadow: var(--shadow-card); }
.tl-header { display: flex; justify-content: space-between; align-items: center; }
.tl-num { font-weight: 600; font-size: 14px; }
.tl-date { font-size: 13px; color: var(--color-text-secondary); margin-top: 4px; }
.tl-detail { margin-top: 8px; font-size: 13px; line-height: 1.8; border-top: 1px solid var(--color-border); padding-top: 8px; }
.apt-list { padding: 12px 16px; display: flex; flex-direction: column; gap: 12px; }
.apt-card { background: var(--color-card); border-radius: 12px; padding: 14px; box-shadow: var(--shadow-card); }
.apt-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.apt-date { font-size: 15px; }
.today-tip { font-size: 13px; color: var(--color-primary); margin-top: 4px; }
:deep(.van-tag--success) { background: var(--color-primary); border-color: var(--color-primary); }
</style>