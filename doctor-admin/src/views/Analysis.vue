<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPatients } from '@/api/patients'
import { getSymptomTrend, getSymptomRadar, getTreatmentTimeline, getLabTrend } from '@/api/analysis'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()

const selectedPatientId = ref<number | null>(route.query.patient_id ? Number(route.query.patient_id) : null)
const patients = ref<Array<{ id: number; name: string }>>([])
const loading = ref(false)

const lineChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)
const timelineRef = ref<HTMLElement | null>(null)
const labChartRef = ref<HTMLElement | null>(null)

let lineChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null
let labChart: echarts.ECharts | null = null

const timelineData = ref<any[]>([])

async function loadPatients() {
  const res = await getPatients({ limit: 100 })
  patients.value = res.data.map(p => ({ id: p.id, name: p.name }))
}

async function loadCharts() {
  if (!selectedPatientId.value) return
  loading.value = true
  try {
    const [trendRes, radarRes, tlRes, labRes] = await Promise.all([
      getSymptomTrend(selectedPatientId.value),
      getSymptomRadar(selectedPatientId.value),
      getTreatmentTimeline(selectedPatientId.value),
      getLabTrend(selectedPatientId.value),
    ])

    await nextTick()
    renderLineChart(trendRes.data)
    renderRadarChart(radarRes.data)
    timelineData.value = tlRes.data
    renderLabChart(labRes.data)
  } finally {
    loading.value = false
  }
}

function renderLineChart(data: any) {
  if (!lineChartRef.value) return
  if (!lineChart) lineChart = echarts.init(lineChartRef.value)

  if (!data?.series?.length) {
    lineChart.setOption({ title: { text: '暂无症状数据', left: 'center', top: 'middle', textStyle: { color: '#999' } }, series: [] })
    return
  }

  const colors = ['#5DB391', '#EF9A9A', '#64B5F6', '#FFB74D', '#CE93D8', '#80CBC4']
  lineChart.setOption({
    title: { text: '症状严重程度变化', left: 16, textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, type: 'scroll' },
    grid: { top: 50, bottom: 50, left: 40, right: 20 },
    xAxis: { type: 'category', data: data.x_labels ?? [], axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', min: 0, max: 10, name: '严重程度' },
    color: colors,
    series: (data.series ?? []).map((s: any) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      data: s.data,
      symbol: 'circle',
      symbolSize: 6,
    })),
  })
}

function renderRadarChart(data: any) {
  if (!radarChartRef.value) return
  if (!radarChart) radarChart = echarts.init(radarChartRef.value)

  if (!data?.indicators?.length) {
    radarChart.setOption({ title: { text: '暂无数据（至少需要2次就诊）', left: 'center', top: 'middle', textStyle: { color: '#999' } }, series: [] })
    return
  }

  radarChart.setOption({
    title: { text: '症状雷达图（首诊 vs 当前）', left: 16, textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: {},
    legend: { bottom: 0, data: ['首诊', '当前'] },
    radar: {
      indicator: (data.indicators ?? []).map((i: any) => ({ name: i.name, max: 10 })),
      splitArea: { areaStyle: { color: ['#f8f9fa', '#f0f7f4'] } },
    },
    series: [{
      type: 'radar',
      data: [
        { name: '首诊', value: data.first_visit ?? [], lineStyle: { color: '#EF9A9A' }, areaStyle: { color: 'rgba(239,154,154,0.2)' } },
        { name: '当前', value: data.latest_visit ?? [], lineStyle: { color: '#5DB391' }, areaStyle: { color: 'rgba(93,179,145,0.2)' } },
      ],
    }],
  })
}

function renderLabChart(data: any) {
  if (!labChartRef.value) return
  if (!labChart) labChart = echarts.init(labChartRef.value)

  if (!data?.indicators?.length) {
    labChart.setOption({ title: { text: '暂无检验数据', left: 'center', top: 'middle', textStyle: { color: '#999' } }, series: [] })
    return
  }

  labChart.setOption({
    title: { text: '检验指标趋势', left: 16, textStyle: { fontSize: 14, fontWeight: 600 } },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, type: 'scroll' },
    grid: { top: 50, bottom: 50, left: 50, right: 20 },
    xAxis: { type: 'category', data: data.dates ?? [] },
    yAxis: { type: 'value' },
    series: (data.indicators ?? []).map((ind: any) => ({
      name: ind.name,
      type: 'bar',
      data: ind.values,
      markLine: ind.ref_range ? {
        data: [{ yAxis: ind.ref_range[0], name: '参考下限' }, { yAxis: ind.ref_range[1], name: '参考上限' }],
        lineStyle: { type: 'dashed', color: '#999' },
        label: { show: false },
      } : undefined,
    })),
  })
}

watch(selectedPatientId, loadCharts)
onMounted(async () => {
  await loadPatients()
  if (selectedPatientId.value) {
    await loadCharts()
  }
})

window.addEventListener('resize', () => {
  lineChart?.resize()
  radarChart?.resize()
  timelineChart?.resize()
  labChart?.resize()
})
</script>

<template>
  <div class="analysis-page">
    <div class="page-header">
      <h2 class="page-title">数据分析</h2>
      <div class="patient-select">
        <label>选择患者：</label>
        <el-select v-model="selectedPatientId" placeholder="请选择患者" filterable style="width:200px" @change="loadCharts">
          <el-option v-for="p in patients" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
    </div>

    <div v-if="!selectedPatientId" class="empty-hint">
      <el-empty description="请先选择一位患者" />
    </div>

    <div v-else v-loading="loading" class="charts-grid">
      <!-- 症状折线图 -->
      <div class="chart-card full-width">
        <div ref="lineChartRef" class="chart-box" style="height:280px" />
      </div>

      <!-- 雷达图 + 时间轴 -->
      <div class="chart-card">
        <div ref="radarChartRef" class="chart-box" style="height:300px" />
      </div>

      <div class="chart-card">
        <div class="timeline-title">治疗时间轴</div>
        <div v-if="!timelineData.length" class="no-data">暂无数据</div>
        <el-timeline v-else style="padding: 10px 0 0 10px">
          <el-timeline-item
            v-for="item in timelineData"
            :key="item.visit_id"
            :timestamp="item.date"
            placement="top"
            size="small"
          >
            <div class="tl-item">
              <span class="tl-num">第{{ item.visit_number }}次</span>
              <el-tag v-if="item.treatment_types?.length" size="small" type="success" style="margin-left:8px">
                {{ item.treatment_types.join('·') }}
              </el-tag>
              <div v-if="item.diagnosis" class="tl-diag">{{ item.diagnosis }}</div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 检验指标柱状图 -->
      <div class="chart-card full-width">
        <div ref="labChartRef" class="chart-box" style="height:260px" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-page { max-width: 1200px; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.patient-select {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.empty-hint { padding: 60px 0; }

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  background: white;
  border-radius: var(--radius-card);
  padding: 16px;
  box-shadow: var(--shadow-card);
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-box { width: 100%; }

.timeline-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 12px;
}

.no-data {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 40px 0;
}

.tl-item { padding: 2px 0; }

.tl-num {
  font-weight: 500;
  font-size: 13px;
}

.tl-diag {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

@media (max-width: 768px) {
  .charts-grid { grid-template-columns: 1fr; }
  .chart-card.full-width { grid-column: 1; }
}
</style>
