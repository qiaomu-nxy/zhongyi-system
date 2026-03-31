<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAppointments, cancelAppointment, markNoShow, type Appointment
} from '@/api/appointments'
import {
  getSchedules, updateSchedule, getScheduleOverrides, createOverride, deleteOverride,
  type Schedule, type ScheduleOverride
} from '@/api/schedules'

const activeTab = ref('calendar')

// ========== 预约日历 ==========
const weekOffset = ref(0)
const appointments = ref<Appointment[]>([])
const calLoading = ref(false)

const weekDates = computed(() => {
  const dates: string[] = []
  const today = new Date()
  const monday = new Date(today)
  monday.setDate(today.getDate() - today.getDay() + 1 + weekOffset.value * 7)
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    dates.push(d.toISOString().slice(0, 10))
  }
  return dates
})

const weekLabel = computed(() => {
  const start = new Date(weekDates.value[0]).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
  const end = new Date(weekDates.value[6]).toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
  return `${start} — ${end}`
})

const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

function getAptsByDate(date: string) {
  return appointments.value.filter(a => a.appointment_date === date)
}

function aptStatusClass(status: string) {
  if (status === '待就诊') return 'apt-waiting'
  if (status === '已完成') return 'apt-done'
  if (status === '已取消') return 'apt-cancelled'
  if (status === '爽约') return 'apt-noshow'
  return ''
}

const popoverApt = ref<Appointment | null>(null)

async function loadCalendar() {
  calLoading.value = true
  try {
    const start = weekDates.value[0]
    const end = weekDates.value[6]
    const promises = weekDates.value.map(d => getAppointments({ date: d }))
    const results = await Promise.all(promises)
    appointments.value = results.flatMap(r => r.data)
  } finally {
    calLoading.value = false
  }
}

async function handleCancelByDoctor(apt: Appointment) {
  await ElMessageBox.confirm(`确认取消 ${apt.patient?.name ?? '该患者'} 的预约？`, '取消预约', { type: 'warning' })
  await cancelAppointment(apt.id, { by_doctor: true })
  ElMessage.success('预约已取消')
  popoverApt.value = null
  await loadCalendar()
}

async function handleMarkNoShow(apt: Appointment) {
  await ElMessageBox.confirm('确认将此预约标记为爽约？', '标记爽约', { type: 'warning' })
  await markNoShow(apt.id)
  ElMessage.success('已标记爽约')
  await loadCalendar()
}

// ========== 预约列表 ==========
const listLoading = ref(false)
const allAppointments = ref<Appointment[]>([])
const listDate = ref('')
const listStatus = ref('')

async function loadList() {
  listLoading.value = true
  try {
    const res = await getAppointments({
      date: listDate.value || undefined,
      status: listStatus.value || undefined,
    })
    allAppointments.value = res.data
  } finally {
    listLoading.value = false
  }
}

// ========== 排班设置 ==========
const schedules = ref<Schedule[]>([])
const overrides = ref<ScheduleOverride[]>([])
const schedLoading = ref(false)
const weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const slotOptions = [{ value: 30, label: '30分钟' }, { value: 45, label: '45分钟' }, { value: 60, label: '60分钟' }]

const defaultSchedule = () => ({
  is_working: true, morning_start: '08:00', morning_end: '12:00',
  afternoon_start: '14:00', afternoon_end: '17:30', slot_duration: 30
})

// 7天响应式排班数据，索引0=周一
const scheduleRows = ref<Schedule[]>(
  Array.from({ length: 7 }, (_, i) => ({ ...defaultSchedule(), weekday: i, id: 0 } as Schedule))
)

function syncScheduleRows() {
  for (let i = 0; i < 7; i++) {
    const found = schedules.value.find(s => s.weekday === i)
    if (found) {
      Object.assign(scheduleRows.value[i], found)
    } else {
      Object.assign(scheduleRows.value[i], { ...defaultSchedule(), weekday: i, id: 0 })
    }
  }
}

async function saveSchedule(weekday: number) {
  const s = scheduleRows.value[weekday]
  await updateSchedule({ ...s, weekday })
  ElMessage.success(`${weekdayNames[weekday]}排班已保存`)
  await loadSchedules()
}

// 临时调整
const overrideForm = ref({
  override_date: '',
  is_working: false,
  morning_start: '08:00', morning_end: '12:00',
  afternoon_start: '14:00', afternoon_end: '17:30',
  slot_duration: 30, reason: '',
})
const overrideDrawer = ref(false)

async function handleAddOverride() {
  if (!overrideForm.value.override_date) {
    ElMessage.warning('请选择日期')
    return
  }
  await createOverride(overrideForm.value)
  ElMessage.success('临时调整已添加')
  overrideDrawer.value = false
  await loadSchedules()
}

async function handleDeleteOverride(id: number) {
  await ElMessageBox.confirm('确认删除此临时调整？', '提示', { type: 'warning' })
  await deleteOverride(id)
  ElMessage.success('已删除')
  await loadSchedules()
}

async function loadSchedules() {
  schedLoading.value = true
  try {
    const [sRes, oRes] = await Promise.all([getSchedules(), getScheduleOverrides()])
    schedules.value = sRes.data
    overrides.value = oRes.data
    syncScheduleRows()
  } finally {
    schedLoading.value = false
  }
}

function onTabChange(tab: string) {
  if (tab === 'calendar') loadCalendar()
  else if (tab === 'list') loadList()
  else if (tab === 'schedule') loadSchedules()
}

onMounted(() => {
  loadCalendar()
})
</script>

<template>
  <div class="appoint-page">
    <h2 class="page-title">预约管理</h2>

    <el-tabs v-model="activeTab" @tab-click="(tab: any) => onTabChange(tab.props.name)">

      <!-- 预约日历 -->
      <el-tab-pane label="预约日历" name="calendar">
        <div class="week-nav">
          <el-button :icon="'ArrowLeft'" @click="weekOffset--; loadCalendar()" />
          <span class="week-label">{{ weekLabel }}</span>
          <el-button :icon="'ArrowRight'" @click="weekOffset++; loadCalendar()" />
          <el-button link @click="weekOffset = 0; loadCalendar()">本周</el-button>
        </div>

        <div class="week-grid" v-loading="calLoading">
          <div v-for="(date, i) in weekDates" :key="date" class="day-col">
            <div class="day-header" :class="{ today: date === new Date().toISOString().slice(0,10) }">
              <span class="day-name">{{ weekDays[i] }}</span>
              <span class="day-date">{{ new Date(date).getDate() }}</span>
            </div>
            <div class="day-body">
              <div v-if="getAptsByDate(date).length === 0" class="no-apt" title="当日无预约">—</div>
              <el-popover
                v-for="apt in getAptsByDate(date)"
                :key="apt.id"
                placement="right"
                :width="220"
                trigger="click"
              >
                <template #reference>
                  <div :class="['apt-item', aptStatusClass(apt.status)]">
                    <span class="apt-time">{{ apt.time_slot }}</span>
                    <span class="apt-name">{{ apt.patient?.name ?? '—' }}</span>
                  </div>
                </template>
                <div class="apt-popover">
                  <div class="pop-name">{{ apt.patient?.name }}</div>
                  <div class="pop-info">{{ apt.patient?.phone }}</div>
                  <div class="pop-info">{{ apt.appointment_date }} {{ apt.time_slot }}</div>
                  <el-tag :type="apt.status === '待就诊' ? 'warning' : 'info'" size="small">{{ apt.status }}</el-tag>
                  <div class="pop-actions" v-if="apt.status === '待就诊'">
                    <el-button size="small" type="danger" @click="handleCancelByDoctor(apt)">取消预约</el-button>
                    <el-button size="small" @click="handleMarkNoShow(apt)">标记爽约</el-button>
                  </div>
                </div>
              </el-popover>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 预约列表 -->
      <el-tab-pane label="预约列表" name="list">
        <div class="list-filters">
          <el-date-picker v-model="listDate" type="date" value-format="YYYY-MM-DD" placeholder="按日期筛选" clearable />
          <el-select v-model="listStatus" placeholder="按状态筛选" clearable style="width:130px">
            <el-option label="待就诊" value="待就诊" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已取消" value="已取消" />
            <el-option label="爽约" value="爽约" />
          </el-select>
          <el-button type="primary" @click="loadList">查询</el-button>
        </div>

        <el-table :data="allAppointments" v-loading="listLoading" empty-text="暂无数据">
          <el-table-column label="患者" min-width="80">
            <template #default="{ row }">{{ row.patient?.name ?? '—' }}</template>
          </el-table-column>
          <el-table-column label="手机号" width="130">
            <template #default="{ row }">{{ row.patient?.phone ?? '—' }}</template>
          </el-table-column>
          <el-table-column label="预约日期" prop="appointment_date" width="120" />
          <el-table-column label="时段" prop="time_slot" width="80" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === '待就诊' ? 'warning' : row.status === '已完成' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <template v-if="row.status === '待就诊'">
                <el-button size="small" type="danger" link @click="handleCancelByDoctor(row)">取消</el-button>
                <el-button size="small" link @click="handleMarkNoShow(row)">爽约</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 排班设置 -->
      <el-tab-pane label="排班设置" name="schedule">
        <div v-loading="schedLoading">
          <div class="schedule-table">
            <div v-for="(name, i) in weekdayNames" :key="i" class="schedule-row">
              <div class="schedule-day">{{ name }}</div>
              <div class="schedule-content">
                <el-switch v-model="scheduleRows[i].is_working" active-text="出诊" inactive-text="休息" />
                <template v-if="scheduleRows[i].is_working">
                  <div class="time-range">
                    <span class="time-label">上午</span>
                    <el-time-select v-model="scheduleRows[i].morning_start" start="06:00" end="12:00" step="00:30" placeholder="开始" style="width:110px" />
                    <span>—</span>
                    <el-time-select v-model="scheduleRows[i].morning_end" start="06:00" end="13:00" step="00:30" placeholder="结束" style="width:110px" />
                  </div>
                  <div class="time-range">
                    <span class="time-label">下午</span>
                    <el-time-select v-model="scheduleRows[i].afternoon_start" start="12:00" end="18:00" step="00:30" placeholder="开始" style="width:110px" />
                    <span>—</span>
                    <el-time-select v-model="scheduleRows[i].afternoon_end" start="12:00" end="20:00" step="00:30" placeholder="结束" style="width:110px" />
                  </div>
                  <div class="time-range">
                    <span class="time-label">时间间隔</span>
                    <el-select v-model="scheduleRows[i].slot_duration" style="width:100px">
                      <el-option v-for="o in slotOptions" :key="o.value" :label="o.label" :value="o.value" />
                    </el-select>
                  </div>
                </template>
              </div>
              <el-button size="small" type="primary" @click="saveSchedule(i)">保存</el-button>
            </div>
          </div>

          <!-- 临时调整 -->
          <div class="override-section">
            <div class="override-header">
              <h4>临时调整</h4>
              <el-button size="small" type="primary" @click="overrideDrawer = true">+ 添加调整</el-button>
            </div>
            <el-table :data="overrides" empty-text="暂无临时调整">
              <el-table-column label="日期" prop="override_date" width="120" />
              <el-table-column label="是否出诊" width="90">
                <template #default="{ row }">
                  <el-tag :type="row.is_working ? 'success' : 'danger'" size="small">{{ row.is_working ? '出诊' : '休息' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="时段" min-width="150">
                <template #default="{ row }">
                  <template v-if="row.is_working">{{ row.morning_start }}–{{ row.morning_end }} / {{ row.afternoon_start }}–{{ row.afternoon_end }}</template>
                  <span v-else class="text-secondary">—</span>
                </template>
              </el-table-column>
              <el-table-column label="原因" prop="reason" />
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button size="small" type="danger" link @click="handleDeleteOverride(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 临时调整抽屉 -->
    <el-drawer v-model="overrideDrawer" title="添加临时调整" size="380px">
      <el-form :model="overrideForm" label-width="90px">
        <el-form-item label="日期" required>
          <el-date-picker v-model="overrideForm.override_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="是否出诊">
          <el-switch v-model="overrideForm.is_working" active-text="出诊" inactive-text="休息" />
        </el-form-item>
        <template v-if="overrideForm.is_working">
          <el-form-item label="上午时段">
            <div style="display:flex;gap:8px;align-items:center">
              <el-time-select v-model="overrideForm.morning_start" start="06:00" end="12:00" step="00:30" style="width:120px" />
              <span>—</span>
              <el-time-select v-model="overrideForm.morning_end" start="06:00" end="13:00" step="00:30" style="width:120px" />
            </div>
          </el-form-item>
          <el-form-item label="下午时段">
            <div style="display:flex;gap:8px;align-items:center">
              <el-time-select v-model="overrideForm.afternoon_start" start="12:00" end="18:00" step="00:30" style="width:120px" />
              <span>—</span>
              <el-time-select v-model="overrideForm.afternoon_end" start="12:00" end="20:00" step="00:30" style="width:120px" />
            </div>
          </el-form-item>
          <el-form-item label="时间间隔">
            <el-select v-model="overrideForm.slot_duration" style="width:100px">
              <el-option v-for="o in slotOptions" :key="o.value" :label="o.label" :value="o.value" />
            </el-select>
          </el-form-item>
        </template>
        <el-form-item label="原因">
          <el-input v-model="overrideForm.reason" placeholder="如：外出会议" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="overrideDrawer = false">取消</el-button>
        <el-button type="primary" @click="handleAddOverride">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.appoint-page { max-width: 1200px; }

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 20px;
}

.week-nav {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.week-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  min-width: 180px;
  text-align: center;
}

.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  background: white;
  border-radius: var(--radius-card);
  padding: 16px;
  box-shadow: var(--shadow-card);
  min-height: 300px;
}

.day-col { display: flex; flex-direction: column; gap: 6px; }

.day-header {
  text-align: center;
  padding: 8px 4px;
  border-radius: 8px;
  background: var(--color-bg);
}

.day-header.today {
  background: var(--color-primary-light);
}

.day-name {
  display: block;
  font-size: 11px;
  color: var(--color-text-secondary);
}

.day-date {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.day-header.today .day-date { color: var(--color-primary); }

.day-body { flex: 1; }

.no-apt {
  text-align: center;
  color: var(--color-border);
  padding: 20px 0;
}

.apt-item {
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  margin-bottom: 4px;
  border: 1px solid transparent;
}

.apt-waiting { background: #FFF3E0; border-color: #E6A23C; }
.apt-done { background: #F0F9FF; border-color: #909399; }
.apt-cancelled { background: #FEF0F0; }
.apt-noshow { background: #FEF0F0; border-color: #F56C6C; }

.apt-time { font-weight: 600; margin-right: 4px; }
.apt-name { color: var(--color-text); }

.apt-popover { padding: 4px 0; }
.pop-name { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.pop-info { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 2px; }
.pop-actions { margin-top: 10px; display: flex; gap: 8px; }

.list-filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.schedule-table { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }

.schedule-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--shadow-card);
}

.schedule-day {
  width: 40px;
  font-weight: 600;
  color: var(--color-text);
  flex-shrink: 0;
}

.schedule-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.time-label {
  color: var(--color-text-secondary);
  width: 30px;
}

.override-section { margin-top: 24px; }

.override-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.override-header h4 { margin: 0; font-size: 15px; }

.text-secondary { color: var(--color-text-secondary); }

@media (max-width: 768px) {
  .week-grid { grid-template-columns: repeat(4, 1fr); }
  .schedule-row { flex-direction: column; align-items: flex-start; }
}
</style>
