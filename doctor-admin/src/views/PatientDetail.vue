<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPatient, updatePatient, getPatientAppointments, exportPatient, type Patient } from '@/api/patients'
import { getVisits, type Visit } from '@/api/visits'
import { getPatientLabResults } from '@/api/patients'

const route = useRoute()
const router = useRouter()
const patientId = Number(route.params.id)

const loading = ref(false)
const patient = ref<Patient | null>(null)
const visits = ref<Visit[]>([])
const appointments = ref<any[]>([])
const labResults = ref<any[]>([])
const activeTab = ref('visits')

const editDrawerVisible = ref(false)
const editForm = ref<Partial<Patient>>({})

async function loadAll() {
  loading.value = true
  try {
    const pRes = await getPatient(patientId)
    patient.value = pRes.data
    editForm.value = { ...pRes.data }
  } catch (e: any) {
    ElMessage.error('加载患者信息失败：' + (e?.response?.data?.detail || e?.message || '未知错误'))
    loading.value = false
    return
  }

  // 其余数据独立加载，单个失败不影响主信息展示
  Promise.all([
    getVisits({ patient_id: patientId }).then(r => { visits.value = r.data }).catch(() => {}),
    getPatientAppointments(patientId).then(r => { appointments.value = r.data }).catch(() => {}),
    getPatientLabResults(patientId).then(r => { labResults.value = r.data }).catch(() => {}),
  ]).finally(() => { loading.value = false })
}

function getAge(birthDate: string | null): string {
  if (!birthDate) return '未知'
  const age = Math.floor((Date.now() - new Date(birthDate).getTime()) / (365.25 * 24 * 3600 * 1000))
  return `${age}岁`
}

function getVisitStatusType(status: string) {
  const map: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
    '待签到': 'warning', '待接诊': 'success', '已完成': 'info', '已作废': 'danger'
  }
  return map[status] ?? 'info'
}

function getAptStatusType(status: string) {
  const map: Record<string, 'success' | 'warning' | 'info' | 'danger'> = {
    '待就诊': 'warning', '已完成': 'success', '已取消': 'info', '爽约': 'danger'
  }
  return map[status] ?? 'info'
}

async function handleSaveEdit() {
  if (!editForm.value.name || !editForm.value.phone) {
    ElMessage.warning('姓名和手机号不能为空')
    return
  }
  await updatePatient(patientId, editForm.value)
  ElMessage.success('保存成功')
  editDrawerVisible.value = false
  await loadAll()
}

async function handleExport() {
  const res = await exportPatient(patientId)
  const url = URL.createObjectURL(res.data as Blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `患者档案_${patient.value?.name}.xlsx`
  a.click()
  URL.revokeObjectURL(url)
}

const medicalHistoryOptions = ['糖尿病', '高血压', '心脏病', '肝病', '肾病', '无']

onMounted(loadAll)
</script>

<template>
  <div class="patient-detail" v-loading="loading">
    <div class="back-bar">
      <el-button link :icon="'ArrowLeft'" @click="router.back()">返回患者列表</el-button>
    </div>

    <template v-if="patient">
      <!-- 患者信息卡 -->
      <div class="info-card">
        <div class="info-avatar">{{ patient.name[0] }}</div>
        <div class="info-main">
          <div class="info-name-row">
            <h2>{{ patient.name }}</h2>
            <el-tag v-if="patient.gender" size="small" :type="patient.gender === '男' ? 'primary' : 'danger'">{{ patient.gender }}</el-tag>
          </div>
          <div class="info-meta">
            <span>{{ getAge(patient.birth_date) }}</span>
            <span>📱 {{ patient.phone }}</span>
            <span>注册：{{ new Date(patient.created_at).toLocaleDateString('zh-CN') }}</span>
          </div>
          <div v-if="patient.medical_history?.length" class="info-tags">
            <span class="tag-label">既往病史：</span>
            <el-tag v-for="h in patient.medical_history" :key="h" size="small" type="warning" style="margin: 2px">{{ h }}</el-tag>
          </div>
          <div v-if="patient.allergy_history" class="info-allergy">
            <span class="tag-label">过敏史：</span>{{ patient.allergy_history }}
          </div>
        </div>
        <div class="info-actions">
          <el-button :icon="'Edit'" @click="editDrawerVisible = true">编辑</el-button>
          <el-button :icon="'Download'" @click="handleExport">导出档案</el-button>
          <el-button type="primary" :icon="'DataAnalysis'" @click="router.push(`/analysis?patient_id=${patientId}`)">数据分析</el-button>
        </div>
      </div>

      <!-- Tab -->
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- 就诊记录 -->
        <el-tab-pane label="就诊记录" name="visits">
          <div v-if="visits.length === 0" class="empty-hint">暂无就诊记录</div>
          <el-timeline v-else>
            <el-timeline-item
              v-for="v in visits"
              :key="v.id"
              :timestamp="new Date(v.visit_date).toLocaleDateString('zh-CN')"
              placement="top"
            >
              <div class="visit-card">
                <div class="visit-header">
                  <span class="visit-num">第{{ v.visit_number }}次就诊</span>
                  <el-tag :type="getVisitStatusType(v.status)" size="small">{{ v.status }}</el-tag>
                  <el-tag v-if="v.symptom_submitted_at" type="success" size="small">已填症状</el-tag>
                </div>
                <p v-if="v.chief_complaint" class="visit-complaint">{{ v.chief_complaint }}</p>
                <el-button link size="small" type="primary" @click="router.push(`/visits/${v.id}/record`)">查看病历 →</el-button>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>

        <!-- 预约记录 -->
        <el-tab-pane label="预约记录" name="appointments">
          <div v-if="appointments.length === 0" class="empty-hint">暂无预约记录</div>
          <el-table v-else :data="appointments">
            <el-table-column label="预约日期" prop="appointment_date" width="120" />
            <el-table-column label="时段" prop="time_slot" width="80" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="getAptStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="取消原因" prop="cancel_reason" />
          </el-table>
        </el-tab-pane>

        <!-- 检验指标 -->
        <el-tab-pane label="检验指标" name="lab">
          <div v-if="labResults.length === 0" class="empty-hint">暂无检验指标记录</div>
          <el-table v-else :data="labResults">
            <el-table-column label="指标名称" prop="indicator_name" />
            <el-table-column label="数值" prop="value" />
            <el-table-column label="单位" prop="unit" />
            <el-table-column label="参考范围" >
              <template #default="{ row }">{{ row.ref_min }}–{{ row.ref_max }}</template>
            </el-table-column>
            <el-table-column label="记录时间" width="120">
              <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString('zh-CN') }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- 编辑抽屉 -->
    <el-drawer v-model="editDrawerVisible" title="编辑患者信息" size="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="editForm.birth_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="既往病史">
          <el-checkbox-group v-model="editForm.medical_history">
            <el-checkbox v-for="opt in medicalHistoryOptions" :key="opt" :label="opt">{{ opt }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="过敏史">
          <el-input v-model="editForm.allergy_history" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDrawerVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.patient-detail { max-width: 1000px; }

.back-bar { margin-bottom: 16px; }

.info-card {
  background: white;
  border-radius: var(--radius-card);
  padding: 24px;
  box-shadow: var(--shadow-card);
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.info-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-main { flex: 1; min-width: 0; }

.info-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.info-name-row h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text);
}

.info-meta {
  display: flex;
  gap: 16px;
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}

.info-tags, .info-allergy {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 6px;
}

.tag-label { font-weight: 500; color: var(--color-text); }

.info-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.detail-tabs {
  background: white;
  border-radius: var(--radius-card);
  padding: 0 20px 20px;
  box-shadow: var(--shadow-card);
}

.visit-card {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  margin-bottom: 4px;
}

.visit-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.visit-num {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text);
}

.visit-complaint {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 6px;
}

.empty-hint {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 40px;
}

@media (max-width: 768px) {
  .info-card { flex-direction: column; }
  .info-actions { flex-direction: row; flex-wrap: wrap; }
}
</style>
