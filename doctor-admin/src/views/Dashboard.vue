<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTodayVisits, createVisit, type TodayStats, type Visit } from '@/api/visits'
import { getPatients, createPatient, type Patient } from '@/api/patients'

const router = useRouter()
const loading = ref(false)
const stats = ref<TodayStats>({ total: 0, waiting: 0, completed: 0, new_patients: 0, return_patients: 0, visits: [] })

const waitingVisits = ref<Visit[]>([])
const completedVisits = ref<Visit[]>([])

// 手动创建就诊相关
const createDialogVisible = ref(false)
const searchKeyword = ref('')
const searchResults = ref<Patient[]>([])
const selectedPatient = ref<Patient | null>(null)
const newPatientForm = ref({ name: '', phone: '', gender: '男' })
const showNewPatientForm = ref(false)
const createLoading = ref(false)

async function loadData(showFeedback = false) {
  loading.value = true
  try {
    const res = await getTodayVisits()
    stats.value = res.data
    waitingVisits.value = res.data.visits.filter(v => v.status === '待接诊' || v.status === '待签到')
    completedVisits.value = res.data.visits.filter(v => v.status === '已完成')
    if (showFeedback) ElMessage.success('数据已刷新')
  } catch {
    ElMessage.error('刷新失败，请检查网络')
  } finally {
    loading.value = false
  }
}

function getAge(birthDate: string | null): string {
  if (!birthDate) return '—'
  const age = Math.floor((Date.now() - new Date(birthDate).getTime()) / (365.25 * 24 * 3600 * 1000))
  return `${age}岁`
}

function formatVisitNumber(n: number): string {
  return `第${n}次`
}

function getStatusTag(status: string) {
  const map: Record<string, { type: 'success' | 'warning' | 'info' | 'danger'; label: string }> = {
    '待签到': { type: 'warning', label: '待签到' },
    '待接诊': { type: 'success', label: '待接诊' },
    '已完成': { type: 'info', label: '已完成' },
    '已作废': { type: 'danger', label: '已作废' },
  }
  return map[status] ?? { type: 'info', label: status }
}

async function handleSearch() {
  if (!searchKeyword.value.trim()) return
  const res = await getPatients({ search: searchKeyword.value })
  searchResults.value = res.data
  showNewPatientForm.value = false
  selectedPatient.value = null
}

function selectPatient(p: Patient) {
  selectedPatient.value = p
  showNewPatientForm.value = false
}

async function handleCreateVisit() {
  createLoading.value = true
  try {
    let patientId: number
    if (showNewPatientForm.value) {
      if (!newPatientForm.value.name || !newPatientForm.value.phone) {
        ElMessage.warning('请填写患者姓名和手机号')
        return
      }
      const res = await createPatient(newPatientForm.value)
      patientId = res.data.id
    } else if (selectedPatient.value) {
      patientId = selectedPatient.value.id
    } else {
      ElMessage.warning('请选择或创建患者')
      return
    }
    await createVisit({ patient_id: patientId })
    ElMessage.success('就诊记录已创建')
    createDialogVisible.value = false
    resetCreateForm()
    await loadData()
  } finally {
    createLoading.value = false
  }
}

function resetCreateForm() {
  searchKeyword.value = ''
  searchResults.value = []
  selectedPatient.value = null
  showNewPatientForm.value = false
  newPatientForm.value = { name: '', phone: '', gender: '男' }
}

function goToMedicalRecord(visitId: number) {
  router.push(`/visits/${visitId}/record`)
}

onMounted(loadData)
</script>

<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h2 class="page-title">今日就诊</h2>
        <p class="page-subtitle">{{ new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }) }}</p>
      </div>
      <div class="header-actions">
        <el-button @click="loadData(true)" :loading="loading" :icon="'Refresh'" title="手动刷新最新就诊状态">刷新</el-button>
        <el-button type="primary" :icon="'Plus'" @click="createDialogVisible = true">手动创建就诊</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">今日总就诊</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-value">{{ stats.waiting }}</div>
        <div class="stat-label">待接诊</div>
      </div>
      <div class="stat-card success">
        <div class="stat-value">{{ stats.completed }}</div>
        <div class="stat-label">已完成</div>
      </div>
      <div class="stat-card info">
        <div class="stat-value">{{ stats.new_patients }}</div>
        <div class="stat-label">今日新患者</div>
      </div>
      <div class="stat-card primary">
        <div class="stat-value">{{ stats.return_patients }}</div>
        <div class="stat-label">今日复诊</div>
      </div>
    </div>

    <!-- 待接诊列表 -->
    <div class="section-card">
      <div class="section-header">
        <h3>待接诊 <el-tag type="warning" size="small">{{ waitingVisits.length }}</el-tag></h3>
      </div>
      <el-table :data="waitingVisits" v-loading="loading" empty-text="暂无待接诊患者">
        <el-table-column label="姓名" min-width="80">
          <template #default="{ row }">
            <span class="patient-name">{{ row.patient?.name ?? '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="性别" width="60">
          <template #default="{ row }">{{ row.patient?.gender ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="年龄" width="70">
          <template #default="{ row }">{{ getAge(row.patient?.birth_date ?? null) }}</template>
        </el-table-column>
        <el-table-column label="就诊次数" width="90">
          <template #default="{ row }">{{ formatVisitNumber(row.visit_number) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status).type" size="small">{{ getStatusTag(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="症状状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.symptom_submitted_at ? 'success' : 'info'" size="small">
              {{ row.symptom_submitted_at ? '已提交' : '未提交' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="主诉" min-width="120">
          <template #default="{ row }">
            <span class="text-secondary">{{ row.chief_complaint || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToMedicalRecord(row.id)">开始接诊</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 已完成列表 -->
    <div class="section-card">
      <div class="section-header">
        <h3>已完成 <el-tag type="info" size="small">{{ completedVisits.length }}</el-tag></h3>
      </div>
      <el-table :data="completedVisits" v-loading="loading" empty-text="今日暂无完成就诊">
        <el-table-column label="姓名" min-width="80">
          <template #default="{ row }">{{ row.patient?.name ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="性别" width="60">
          <template #default="{ row }">{{ row.patient?.gender ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="就诊次数" width="90">
          <template #default="{ row }">{{ formatVisitNumber(row.visit_number) }}</template>
        </el-table-column>
        <el-table-column label="主诉" min-width="120">
          <template #default="{ row }">{{ row.chief_complaint || '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="goToMedicalRecord(row.id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 手动创建就诊弹窗 -->
    <el-dialog v-model="createDialogVisible" title="手动创建就诊" width="480px" @close="resetCreateForm">
      <div class="create-dialog-body">
        <div class="search-area">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索患者姓名或手机号"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="'Search'" @click="handleSearch" />
            </template>
          </el-input>
        </div>

        <!-- 搜索结果 -->
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="p in searchResults"
            :key="p.id"
            class="result-item"
            :class="{ selected: selectedPatient?.id === p.id }"
            @click="selectPatient(p)"
          >
            <div class="result-name">{{ p.name }}</div>
            <div class="result-info">{{ p.phone }} · {{ p.gender ?? '未知' }}</div>
          </div>
        </div>
        <div v-else-if="searchKeyword && !showNewPatientForm" class="no-result">
          <p>未找到患者</p>
          <el-button size="small" type="primary" text @click="showNewPatientForm = true">+ 创建新患者</el-button>
        </div>

        <!-- 新患者表单 -->
        <div v-if="showNewPatientForm" class="new-patient-form">
          <el-divider>新患者信息</el-divider>
          <el-form :model="newPatientForm" label-width="70px" size="small">
            <el-form-item label="姓名" required>
              <el-input v-model="newPatientForm.name" placeholder="患者姓名" />
            </el-form-item>
            <el-form-item label="手机号" required>
              <el-input v-model="newPatientForm.phone" placeholder="11位手机号" />
            </el-form-item>
            <el-form-item label="性别">
              <el-radio-group v-model="newPatientForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreateVisit">
          确认创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 4px;
}

.page-subtitle {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: var(--radius-card);
  padding: 20px;
  text-align: center;
  box-shadow: var(--shadow-card);
  border-left: 4px solid var(--color-border);
}

.stat-card.warning { border-left-color: var(--color-warning); }
.stat-card.success { border-left-color: var(--color-success); }
.stat-card.info { border-left-color: var(--color-info); }
.stat-card.primary { border-left-color: var(--color-primary); }

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.section-card {
  background: white;
  border-radius: var(--radius-card);
  padding: 20px;
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.patient-name {
  font-weight: 500;
}

.text-secondary {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.create-dialog-body {
  min-height: 120px;
}

.search-area {
  margin-bottom: 12px;
}

.search-results {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.result-item {
  padding: 10px 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.15s;
}

.result-item:last-child { border-bottom: none; }
.result-item:hover { background: var(--color-primary-light); }
.result-item.selected { background: var(--color-primary-light); border-left: 3px solid var(--color-primary); }

.result-name {
  font-weight: 500;
  font-size: 14px;
  color: var(--color-text);
}

.result-info {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.no-result {
  text-align: center;
  padding: 16px;
  color: var(--color-text-secondary);
}

.no-result p { margin: 0 0 8px; }

.new-patient-form {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .page-header {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
