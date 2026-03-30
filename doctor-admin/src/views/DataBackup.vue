<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { exportExcel, downloadDb, exportPatientRecord } from '@/api/backup'
import { getPatients } from '@/api/patients'

const exportingExcel = ref(false)
const exportingDb = ref(false)
const exportingPatient = ref(false)
const searchKeyword = ref('')
const searchResults = ref<Array<{ id: number; name: string; phone: string }>>([])
const selectedPatient = ref<{ id: number; name: string } | null>(null)

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function handleExportExcel() {
  exportingExcel.value = true
  try {
    const res = await exportExcel()
    const date = new Date().toISOString().slice(0, 10)
    downloadBlob(res.data as Blob, `中医问诊数据_${date}.xlsx`)
    ElMessage.success('Excel 导出成功')
  } finally {
    exportingExcel.value = false
  }
}

async function handleDownloadDb() {
  exportingDb.value = true
  try {
    const res = await downloadDb()
    const date = new Date().toISOString().slice(0, 10)
    downloadBlob(res.data as Blob, `zhongyi_backup_${date}.db`)
    ElMessage.success('数据库下载成功')
  } finally {
    exportingDb.value = false
  }
}

async function handleSearchPatient() {
  if (!searchKeyword.value.trim()) return
  const res = await getPatients({ search: searchKeyword.value })
  searchResults.value = res.data.map(p => ({ id: p.id, name: p.name, phone: p.phone }))
}

async function handleExportPatient() {
  if (!selectedPatient.value) {
    ElMessage.warning('请先选择患者')
    return
  }
  exportingPatient.value = true
  try {
    const res = await exportPatientRecord(selectedPatient.value.id)
    downloadBlob(res.data as Blob, `患者档案_${selectedPatient.value.name}.xlsx`)
    ElMessage.success('导出成功')
  } finally {
    exportingPatient.value = false
  }
}
</script>

<template>
  <div class="backup-page">
    <h2 class="page-title">数据备份</h2>

    <el-alert
      title="建议每周定期备份，备份文件请妥善保存在安全的地方"
      type="info"
      show-icon
      :closable="false"
      style="margin-bottom: 20px"
    />

    <div class="backup-grid">
      <!-- 导出 Excel -->
      <div class="backup-card">
        <div class="backup-icon" style="background:#E8F5E9">
          <el-icon size="32" color="#5DB391"><Document /></el-icon>
        </div>
        <h3>导出全部数据（Excel）</h3>
        <p>将所有患者、就诊记录、预约、病历等数据导出为 Excel 文件，便于查阅和归档。</p>
        <el-button type="primary" :loading="exportingExcel" @click="handleExportExcel" class="backup-btn">
          <el-icon><Download /></el-icon>
          导出 Excel
        </el-button>
      </div>

      <!-- 下载数据库 -->
      <div class="backup-card">
        <div class="backup-icon" style="background:#E3F2FD">
          <el-icon size="32" color="#64B5F6"><DataBase /></el-icon>
        </div>
        <h3>下载数据库备份</h3>
        <p>下载完整的 SQLite 数据库文件（zhongyi.db），可用 DB Browser for SQLite 查看所有数据。</p>
        <el-button :loading="exportingDb" @click="handleDownloadDb" class="backup-btn">
          <el-icon><Download /></el-icon>
          下载 .db 文件
        </el-button>
      </div>

      <!-- 按患者导出 -->
      <div class="backup-card wide">
        <div class="backup-icon" style="background:#FFF3E0">
          <el-icon size="32" color="#FFB74D"><User /></el-icon>
        </div>
        <h3>按患者导出病历</h3>
        <p>搜索并选择患者，导出该患者所有就诊记录和病历的完整 Excel 文件。</p>

        <div class="patient-search">
          <el-input
            v-model="searchKeyword"
            placeholder="输入患者姓名或手机号搜索"
            style="width: 260px"
            @keyup.enter="handleSearchPatient"
          >
            <template #append>
              <el-button :icon="'Search'" @click="handleSearchPatient" />
            </template>
          </el-input>

          <div v-if="searchResults.length > 0" class="search-results">
            <div
              v-for="p in searchResults"
              :key="p.id"
              class="result-item"
              :class="{ selected: selectedPatient?.id === p.id }"
              @click="selectedPatient = p"
            >
              <span class="result-name">{{ p.name }}</span>
              <span class="result-phone">{{ p.phone }}</span>
            </div>
          </div>
        </div>

        <div v-if="selectedPatient" class="selected-hint">
          <el-icon color="#5DB391"><CircleCheck /></el-icon>
          已选择：{{ selectedPatient.name }}
        </div>

        <el-button
          type="warning"
          :loading="exportingPatient"
          :disabled="!selectedPatient"
          @click="handleExportPatient"
          class="backup-btn"
        >
          <el-icon><Download /></el-icon>
          导出该患者档案
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.backup-page { max-width: 900px; }

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 20px;
}

.backup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.backup-card {
  background: white;
  border-radius: var(--radius-card);
  padding: 28px;
  box-shadow: var(--shadow-card);
}

.backup-card.wide {
  grid-column: 1 / -1;
}

.backup-icon {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.backup-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 8px;
}

.backup-card p {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 20px;
  line-height: 1.6;
}

.backup-btn {
  min-width: 140px;
}

.patient-search { margin-bottom: 16px; }

.search-results {
  margin-top: 8px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  max-height: 180px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.15s;
}

.result-item:last-child { border-bottom: none; }
.result-item:hover { background: var(--color-primary-light); }
.result-item.selected { background: var(--color-primary-light); border-left: 3px solid var(--color-primary); }

.result-name { font-weight: 500; }
.result-phone { color: var(--color-text-secondary); font-size: 13px; }

.selected-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-primary);
  margin-bottom: 12px;
}

@media (max-width: 768px) {
  .backup-grid { grid-template-columns: 1fr; }
  .backup-card.wide { grid-column: 1; }
}
</style>
