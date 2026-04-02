<template>
  <div class="page">
    <van-nav-bar title="在线预约" left-arrow @click-left="router.back()" />

    <!-- 日期选择横条 -->
    <div class="date-bar">
      <div
        v-for="d in dateList"
        :key="d.value"
        class="date-item"
        :class="{ active: selectedDate === d.value }"
        @click="selectDate(d.value)"
      >
        <span class="date-weekday">{{ d.weekday }}</span>
        <span class="date-day">{{ d.day }}</span>
        <span class="date-tag" v-if="d.isToday">今天</span>
      </div>
    </div>

    <!-- 时段网格 -->
    <div class="slots-section">
      <van-loading v-if="loadingSlots" size="24px" class="loading" />
      <template v-else>
        <p v-if="!slots.length" class="empty-tip">当日休诊或无可用时段</p>
        <div v-else class="slots-grid">
          <div
            v-for="slot in slots"
            :key="slot.time_slot"
            class="slot-item"
            :class="{
              available: slot.available,
              selected: selectedSlot === slot.time_slot,
              booked: !slot.available,
            }"
            @click="slot.available && (selectedSlot = slot.time_slot)"
          >
            {{ slot.time_slot }}
          </div>
        </div>
      </template>
    </div>

    <!-- 确认卡片 -->
    <div v-if="selectedSlot" class="confirm-card">
      <p class="confirm-info">
        <van-icon name="clock-o" /> {{ selectedDate }} &nbsp;{{ selectedSlot }}
      </p>
      <van-button type="primary" block round :loading="booking" @click="handleBook">
        确认预约
      </van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { getAvailableSlots, createAppointment } from '../api/appointment'
import { usePatientStore } from '../stores/patient'

const router = useRouter()
const store = usePatientStore()

const selectedDate = ref('')
const selectedSlot = ref('')
const slots = ref<any[]>([])
const loadingSlots = ref(false)
const booking = ref(false)

const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const dateList = (() => {
  const list = []
  for (let i = 0; i < 7; i++) {
    const d = new Date()
    d.setDate(d.getDate() + i)
    list.push({
      value: d.toISOString().slice(0, 10),
      day: d.getDate(),
      weekday: weekdays[d.getDay()],
      isToday: i === 0,
    })
  }
  return list
})()

async function selectDate(date: string) {
  selectedDate.value = date
  selectedSlot.value = ''
  loadingSlots.value = true
  try {
    const res: any = await getAvailableSlots(date)
    slots.value = res
  } catch (e: any) {
    showToast(e.message)
  } finally {
    loadingSlots.value = false
  }
}

async function handleBook() {
  booking.value = true
  try {
    await createAppointment({
      patient_id: store.patientId,
      appointment_date: selectedDate.value,
      time_slot: selectedSlot.value,
    })
    showSuccessToast('预约成功')
    setTimeout(() => router.replace('/records'), 1500)
  } catch (e: any) {
    showToast(e.message || '预约失败')
  } finally {
    booking.value = false
  }
}

onMounted(() => selectDate(dateList[0].value))
</script>

<style scoped>
.page { width: 100%; overflow-x: hidden; background: var(--color-bg); min-height: 100vh; }
.date-bar {
  display: flex;
  overflow-x: auto;
  overflow-y: hidden;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-card);
  border-bottom: 1px solid var(--color-border);
  -webkit-overflow-scrolling: touch;
  overscroll-behavior-x: contain;
}
.date-item {
  flex: 0 0 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 4px;
  border-radius: 12px;
  cursor: pointer;
  position: relative;
}
.date-item.active { background: var(--color-primary); color: #fff; }
.date-weekday { font-size: 11px; opacity: 0.7; }
.date-day { font-size: 18px; font-weight: 600; margin: 2px 0; }
.date-tag { font-size: 10px; background: var(--color-symptom); color: #fff; border-radius: 4px; padding: 0 4px; }
.slots-section { padding: 16px; }
.loading { display: flex; justify-content: center; margin-top: 32px; }
.empty-tip { text-align: center; color: var(--color-text-secondary); margin-top: 32px; }
.slots-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.slot-item {
  padding: 10px 0;
  text-align: center;
  border-radius: 10px;
  font-size: 14px;
  border: 1.5px solid var(--color-border);
  background: var(--color-card);
  cursor: pointer;
}
.slot-item.available:hover { border-color: var(--color-primary); }
.slot-item.selected { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.slot-item.booked { background: #f5f5f5; color: #ccc; cursor: not-allowed; }
.confirm-card {
  position: fixed;
  bottom: 0;
  left: 50%;
  right: auto;
  transform: translateX(-50%);
  width: min(100%, 480px);
  background: var(--color-card);
  padding: 16px;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.08);
}
.confirm-info { font-size: 15px; color: var(--color-text); margin-bottom: 12px; }
:deep(.van-button--primary) { background: var(--color-primary); border-color: var(--color-primary); height: 46px; }
</style>