<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getVisit, getVisitSymptoms, type Visit } from '@/api/visits'
import {
  getMedicalRecord, createMedicalRecord, updateMedicalRecord,
  addLabResult, type MedicalRecord, type MedicalRecordCreate
} from '@/api/medicalRecords'
import { getPatient, type Patient } from '@/api/patients'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const visitId = Number(route.params.id)

const loading = ref(false)
const saving = ref(false)
const visit = ref<Visit | null>(null)
const patient = ref<Patient | null>(null)
const symptoms = ref<any[]>([])
const existingRecord = ref<MedicalRecord | null>(null)

const form = ref<MedicalRecordCreate>({
  treatment_types: [],
  prescription: '',
  acupuncture_points: [],
  tongue_diagnosis: '',
  pulse_diagnosis: '',
  physical_signs: '',
  diagnosis: '',
  syndrome_analysis: '',
  treatment_plan: '',
  notes: '',
})

const acuPointInput = ref('')
const treatmentOptions = ['中药', '针灸', '推拿', '艾灸', '其他']

const hasHerb = computed(() => form.value.treatment_types.includes('中药'))
const hasAcu = computed(() => form.value.treatment_types.includes('针灸'))

const isReadOnly = computed(() => {
  return !!existingRecord.value && auth.doctor?.role !== 'admin'
})

function addAcuPoint() {
  const pt = acuPointInput.value.trim()
  if (pt && !form.value.acupuncture_points!.includes(pt)) {
    form.value.acupuncture_points!.push(pt)
    acuPointInput.value = ''
  }
}

function removeAcuPoint(pt: string) {
  form.value.acupuncture_points = form.value.acupuncture_points!.filter(p => p !== pt)
}

function getSeverityColor(s: number) {
  if (s <= 3) return '#67C23A'
  if (s <= 6) return '#E6A23C'
  return '#F56C6C'
}

async function loadAll() {
  loading.value = true
  try {
    const [vRes, sRes] = await Promise.all([
      getVisit(visitId),
      getVisitSymptoms(visitId),
    ])
    visit.value = vRes.data
    symptoms.value = sRes.data

    if (visit.value.patient) {
      patient.value = visit.value.patient as Patient
    }

    // 尝试加载已有病历
    try {
      const rRes = await getMedicalRecord(visitId)
      if (rRes.data) {
        existingRecord.value = rRes.data
        // 填充表单
        form.value = {
          treatment_types: rRes.data.treatment_types ?? [],
          prescription: rRes.data.prescription ?? '',
          acupuncture_points: rRes.data.acupuncture_points ?? [],
          tongue_diagnosis: rRes.data.tongue_diagnosis ?? '',
          pulse_diagnosis: rRes.data.pulse_diagnosis ?? '',
          physical_signs: rRes.data.physical_signs ?? '',
          diagnosis: rRes.data.diagnosis ?? '',
          syndrome_analysis: rRes.data.syndrome_analysis ?? '',
          treatment_plan: rRes.data.treatment_plan ?? '',
          notes: rRes.data.notes ?? '',
        }
      }
    } catch {
      // 无病历，正常
    }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (form.value.treatment_types.length === 0) {
    ElMessage.warning('请至少选择一种治疗方式')
    return
  }
  saving.value = true
  try {
    if (existingRecord.value) {
      await updateMedicalRecord(existingRecord.value.id, form.value)
      ElMessage.success('病历已更新')
    } else {
      const res = await createMedicalRecord(visitId, form.value)
      existingRecord.value = res.data
      ElMessage.success('病历已保存，就诊状态已更新为已完成')
    }
    await loadAll()
  } finally {
    saving.value = false
  }
}

onMounted(loadAll)
</script>

<template>
  <div class="medical-record" v-loading="loading">
    <div class="back-bar">
      <el-button link :icon="'ArrowLeft'" @click="router.back()">返回</el-button>
      <span v-if="patient" class="breadcrumb">{{ patient.name }} / 第{{ visit?.visit_number }}次就诊</span>
    </div>

    <div v-if="isReadOnly" class="readonly-tip">
      <el-alert type="info" :closable="false" show-icon>
        病历已提交，普通医师不可修改。如需修改请联系管理员。
      </el-alert>
    </div>

    <div class="two-col">
      <!-- 左栏：病历表单 -->
      <div class="left-col">
        <div class="col-card">
          <h3 class="col-title">病历填写</h3>

          <!-- 治疗方式 -->
          <div class="form-group">
            <label class="form-label required">治疗方式</label>
            <el-checkbox-group v-model="form.treatment_types" :disabled="isReadOnly">
              <el-checkbox v-for="opt in treatmentOptions" :key="opt" :label="opt">{{ opt }}</el-checkbox>
            </el-checkbox-group>
          </div>

          <!-- 中药处方 -->
          <div v-if="hasHerb" class="form-group">
            <label class="form-label">处方（中药）</label>
            <el-input
              v-model="form.prescription"
              type="textarea"
              :rows="4"
              placeholder="请输入处方内容，如：黄芪30g、白术15g、茯苓15g..."
              :disabled="isReadOnly"
            />
          </div>

          <!-- 针灸穴位 -->
          <div v-if="hasAcu" class="form-group">
            <label class="form-label">针灸穴位</label>
            <div class="acu-tags">
              <el-tag
                v-for="pt in form.acupuncture_points"
                :key="pt"
                closable
                :disable-transitions="false"
                @close="removeAcuPoint(pt)"
                style="margin: 3px"
              >{{ pt }}</el-tag>
            </div>
            <div class="acu-input" v-if="!isReadOnly">
              <el-input
                v-model="acuPointInput"
                placeholder="输入穴位名，回车添加"
                size="small"
                @keyup.enter="addAcuPoint"
                style="width: 200px"
              />
              <el-button size="small" @click="addAcuPoint">添加</el-button>
            </div>
          </div>

          <!-- 四诊 -->
          <div class="form-row">
            <div class="form-group half">
              <label class="form-label">舌诊</label>
              <el-input v-model="form.tongue_diagnosis" placeholder="如：舌淡红苔薄白" :disabled="isReadOnly" />
            </div>
            <div class="form-group half">
              <label class="form-label">脉诊</label>
              <el-input v-model="form.pulse_diagnosis" placeholder="如：脉沉细" :disabled="isReadOnly" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">体征观察</label>
            <el-input v-model="form.physical_signs" type="textarea" :rows="2" placeholder="如：颜面发黑、痰核..." :disabled="isReadOnly" />
          </div>

          <div class="form-group">
            <label class="form-label">诊断</label>
            <el-input v-model="form.diagnosis" type="textarea" :rows="2" placeholder="中医诊断..." :disabled="isReadOnly" />
          </div>

          <div class="form-group">
            <label class="form-label">辨证思路</label>
            <el-input v-model="form.syndrome_analysis" type="textarea" :rows="3" placeholder="病机分析..." :disabled="isReadOnly" />
          </div>

          <div class="form-group">
            <label class="form-label">治疗方案</label>
            <el-input v-model="form.treatment_plan" type="textarea" :rows="3" placeholder="治疗计划..." :disabled="isReadOnly" />
          </div>

          <div class="form-group">
            <label class="form-label">备注</label>
            <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="其他备注..." :disabled="isReadOnly" />
          </div>

          <div class="save-area">
            <el-button
              v-if="!isReadOnly"
              type="primary"
              size="large"
              :loading="saving"
              class="save-btn"
              @click="handleSave"
            >
              {{ existingRecord ? '更新病历' : '保存病历' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右栏：患者症状 -->
      <div class="right-col">
        <div class="col-card">
          <h3 class="col-title">本次症状</h3>

          <div v-if="!symptoms.length" class="no-symptoms">
            <el-empty description="患者尚未提交症状" :image-size="80" />
          </div>

          <div v-else class="symptom-list">
            <div v-for="s in symptoms" :key="s.id" class="symptom-card">
              <div class="symptom-header">
                <span class="symptom-body">{{ s.body_part }}</span>
                <span class="symptom-name">{{ s.symptom_name }}</span>
                <span class="symptom-severity" :style="{ color: getSeverityColor(s.severity) }">
                  {{ s.severity }}/10
                </span>
              </div>
              <div class="severity-bar">
                <div
                  class="severity-fill"
                  :style="{ width: `${s.severity * 10}%`, background: getSeverityColor(s.severity) }"
                />
              </div>
              <div class="symptom-meta">
                <span v-if="s.duration">持续：{{ s.duration }}</span>
                <span v-if="s.location">位置：{{ s.location }}</span>
              </div>
              <div v-if="s.description" class="symptom-desc">{{ s.description }}</div>
            </div>
          </div>
        </div>

        <!-- 患者基本信息小卡 -->
        <div v-if="patient" class="col-card patient-mini">
          <h3 class="col-title">患者信息</h3>
          <div class="mini-info">
            <div class="mini-row"><span>姓名</span><span>{{ patient.name }}</span></div>
            <div class="mini-row"><span>性别</span><span>{{ patient.gender ?? '—' }}</span></div>
            <div class="mini-row"><span>手机</span><span>{{ patient.phone }}</span></div>
            <div v-if="patient.allergy_history" class="mini-row allergy">
              <span>过敏史</span><span>{{ patient.allergy_history }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.medical-record { max-width: 1200px; }

.back-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.breadcrumb {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.readonly-tip { margin-bottom: 16px; }

.two-col {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 20px;
  align-items: flex-start;
}

.col-card {
  background: white;
  border-radius: var(--radius-card);
  padding: 24px;
  box-shadow: var(--shadow-card);
  margin-bottom: 16px;
}

.col-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-group.half { flex: 1; }

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 6px;
}

.form-label.required::before {
  content: '* ';
  color: var(--color-danger);
}

.acu-tags { min-height: 32px; margin-bottom: 8px; }

.acu-input { display: flex; gap: 8px; align-items: center; }

.save-area { padding-top: 8px; }

.save-btn { width: 100%; }

/* 症状卡片 */
.symptom-list { display: flex; flex-direction: column; gap: 10px; }

.symptom-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
}

.symptom-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.symptom-body {
  font-size: 11px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: 2px 6px;
  border-radius: 4px;
}

.symptom-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  flex: 1;
}

.symptom-severity { font-size: 13px; font-weight: 600; }

.severity-bar {
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  margin-bottom: 6px;
  overflow: hidden;
}

.severity-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

.symptom-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.symptom-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
  font-style: italic;
}

.patient-mini .mini-info { display: flex; flex-direction: column; gap: 8px; }

.mini-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.mini-row span:first-child { color: var(--color-text-secondary); }
.mini-row span:last-child { color: var(--color-text); font-weight: 500; }

.mini-row.allergy span:last-child { color: var(--color-danger); }

.no-symptoms { padding: 20px 0; }

@media (max-width: 768px) {
  .two-col { grid-template-columns: 1fr; }
}
</style>
