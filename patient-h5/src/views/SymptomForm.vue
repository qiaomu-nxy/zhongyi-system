<template>
  <div class="page">
    <van-nav-bar title="症状填写" left-arrow @click-left="router.back()" />

    <van-loading v-if="loading" size="24px" class="loading" />
    <van-empty v-else-if="noVisit" description="今日无就诊安排，请先预约" >
      <template #bottom>
        <van-button type="primary" @click="router.push('/appointment')">去预约</van-button>
      </template>
    </van-empty>

    <template v-else>
      <!-- Step 1: 选部位 -->
      <div class="section-card">
        <p class="section-title">① 点击身体部位选择不适区域</p>
        <BodyPartSelector v-model="selectedParts" />
      </div>

      <!-- Step 2: 选症状 -->
      <div v-if="selectedParts.length" class="section-card">
        <p class="section-title">② 选择具体症状</p>
        <div v-for="part in selectedParts" :key="part" class="part-group">
          <p class="part-label">{{ part }}</p>
          <div class="chip-row">
            <van-tag
              v-for="sym in symptomsFor(part)"
              :key="sym"
              :type="isSelected(part, sym) ? 'danger' : 'default'"
              size="medium"
              @click="toggleSymptom(part, sym)"
              class="sym-chip"
            >{{ sym }}</van-tag>
          </div>
        </div>
      </div>

      <!-- Step 3: 评分卡片 -->
      <div v-if="symptomList.length" class="section-card">
        <p class="section-title">③ 为每个症状打分</p>
        <div v-for="item in symptomList" :key="item.body_part + item.symptom_name" class="score-card">
          <p class="score-sym">{{ item.body_part }} · {{ item.symptom_name }}</p>
          <div class="score-row">
            <span class="score-label">严重程度</span>
            <van-slider
              v-model="item.severity"
              :min="1" :max="10"
              active-color="#EF9A9A"
              class="slider"
            />
            <span class="score-val">{{ item.severity }}</span>
          </div>
          <van-field
            v-model="item.duration"
            label="持续时间"
            placeholder="选填"
            @click="showDurationPicker(item)"
            readonly
          />
          <van-field
            v-model="item.description"
            label="补充描述"
            placeholder="选填，如加重/缓解因素"
            type="textarea"
            rows="1"
            autosize
          />
        </div>
      </div>

      <div class="submit-area">
        <van-button
          type="primary"
          block
          round
          :loading="submitting"
          :disabled="!symptomList.length"
          @click="handleSubmit"
        >提交症状</van-button>
      </div>
    </template>

    <van-popup v-model:show="durationPickerVisible" position="bottom">
      <van-picker
        :columns="durationOptions"
        @confirm="onDurationConfirm"
        @cancel="durationPickerVisible = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { submitSymptoms, getSymptomConfig } from '../api/symptom'
import { getVisits } from '../api/visit'
import { usePatientStore } from '../stores/patient'
import BodyPartSelector from '../components/BodyPartSelector.vue'

const router = useRouter()
const store = usePatientStore()

const loading = ref(true)
const submitting = ref(false)
const noVisit = ref(false)
const todayVisitId = ref<number | null>(null)

const selectedParts = ref<string[]>([])
const selectedSymptoms = ref<Record<string, string[]>>({})
const config = ref<any[]>([])

const durationOptions = ['今天', '2-3天', '一周内', '半月内', '一个月', '一月以上']
const durationPickerVisible = ref(false)
let activeDurationItem: any = null

interface SymptomItem {
  body_part: string
  symptom_name: string
  severity: number
  duration: string
  description: string
}
const symptomList = computed<SymptomItem[]>(() => {
  const list: SymptomItem[] = []
  for (const part of selectedParts.value) {
    for (const sym of selectedSymptoms.value[part] || []) {
      const existing = list.find(i => i.body_part === part && i.symptom_name === sym)
      if (!existing) {
        list.push({ body_part: part, symptom_name: sym, severity: 5, duration: '', description: '' })
      }
    }
  }
  return list
})

function symptomsFor(part: string): string[] {
  return config.value.find((p: any) => p.label === part)?.symptoms || []
}

function isSelected(part: string, sym: string): boolean {
  return (selectedSymptoms.value[part] || []).includes(sym)
}

function toggleSymptom(part: string, sym: string) {
  if (!selectedSymptoms.value[part]) selectedSymptoms.value[part] = []
  const idx = selectedSymptoms.value[part].indexOf(sym)
  if (idx >= 0) selectedSymptoms.value[part].splice(idx, 1)
  else selectedSymptoms.value[part].push(sym)
}

function showDurationPicker(item: any) {
  activeDurationItem = item
  durationPickerVisible.value = true
}

function onDurationConfirm({ selectedValues }: any) {
  if (activeDurationItem) activeDurationItem.duration = selectedValues[0]
  durationPickerVisible.value = false
}

async function handleSubmit() {
  if (!todayVisitId.value) return
  submitting.value = true
  try {
    await submitSymptoms(todayVisitId.value, symptomList.value)
    showSuccessToast('症状已提交')
    setTimeout(() => router.replace('/records'), 1500)
  } catch (e: any) {
    showToast(e.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const [visits, cfg]: any = await Promise.all([
      getVisits(store.patientId!),
      getSymptomConfig(),
    ])
    config.value = cfg.body_parts || []
    const today = new Date().toISOString().slice(0, 10)
    const todayVisit = visits.find((v: any) => v.visit_date === today && v.status !== '已作废')
    if (!todayVisit) {
      noVisit.value = true
    } else {
      todayVisitId.value = todayVisit.id
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { background: var(--color-bg); min-height: 100vh; padding-bottom: 80px; }
.loading { display: flex; justify-content: center; padding: 60px; }
.section-card { background: var(--color-card); margin: 12px; border-radius: var(--radius-card); padding: 16px; box-shadow: var(--shadow-card); }
.section-title { font-size: 14px; font-weight: 600; color: var(--color-primary); margin-bottom: 12px; }
.part-group { margin-bottom: 16px; }
.part-label { font-size: 13px; font-weight: 600; color: var(--color-text-secondary); margin-bottom: 8px; }
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
.sym-chip { cursor: pointer; }
:deep(.van-tag--danger) { background: var(--color-symptom); border-color: var(--color-symptom); }
.score-card { border: 1px solid var(--color-border); border-radius: 12px; padding: 12px; margin-bottom: 12px; }
.score-sym { font-size: 14px; font-weight: 600; color: var(--color-symptom); margin-bottom: 10px; }
.score-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.score-label { font-size: 13px; color: var(--color-text-secondary); white-space: nowrap; }
.slider { flex: 1; }
.score-val { font-size: 15px; font-weight: 700; color: var(--color-symptom); min-width: 20px; }
.submit-area { position: fixed; bottom: 0; left: 0; right: 0; padding: 12px 16px; background: var(--color-card); box-shadow: 0 -2px 8px rgba(0,0,0,0.07); }
:deep(.van-button--primary) { background: var(--color-primary); border-color: var(--color-primary); height: 46px; }
</style>