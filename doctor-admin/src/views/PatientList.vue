<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPatients, type Patient } from '@/api/patients'

const router = useRouter()
const loading = ref(false)
const patients = ref<Patient[]>([])
const search = ref('')
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)

async function loadPatients() {
  loading.value = true
  try {
    const res = await getPatients({ search: search.value || undefined, skip: (currentPage.value - 1) * pageSize, limit: pageSize })
    patients.value = res.data
    total.value = res.data.length >= pageSize ? currentPage.value * pageSize + 1 : (currentPage.value - 1) * pageSize + res.data.length
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  loadPatients()
}

function getAge(birthDate: string | null): string {
  if (!birthDate) return '—'
  const age = Math.floor((Date.now() - new Date(birthDate).getTime()) / (365.25 * 24 * 3600 * 1000))
  return `${age}岁`
}

onMounted(loadPatients)
</script>

<template>
  <div class="patient-list">
    <div class="page-header">
      <h2 class="page-title">患者管理</h2>
      <div class="search-box">
        <el-input
          v-model="search"
          placeholder="搜索姓名或手机号"
          clearable
          style="width: 260px"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="patients" v-loading="loading" empty-text="暂无患者记录" stripe>
        <el-table-column label="姓名" min-width="90">
          <template #default="{ row }">
            <span class="patient-link" @click="router.push(`/patients/${row.id}`)">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="性别" width="60">
          <template #default="{ row }">{{ row.gender ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="年龄" width="70">
          <template #default="{ row }">{{ getAge(row.birth_date) }}</template>
        </el-table-column>
        <el-table-column label="手机号" width="130">
          <template #default="{ row }">{{ row.phone }}</template>
        </el-table-column>
        <el-table-column label="既往病史" min-width="120">
          <template #default="{ row }">
            <span v-if="!row.medical_history?.length" class="text-secondary">无</span>
            <el-tag v-for="h in row.medical_history" :key="h" size="small" style="margin: 2px">{{ h }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="过敏史" min-width="100">
          <template #default="{ row }">
            <span class="text-secondary">{{ row.allergy_history || '无' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="120">
          <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString('zh-CN') }}</template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="router.push(`/patients/${row.id}`)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        class="pagination"
        @current-change="loadPatients"
      />
    </div>
  </div>
</template>

<style scoped>
.patient-list { max-width: 1200px; }

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

.search-box { display: flex; gap: 8px; }

.table-card {
  background: white;
  border-radius: var(--radius-card);
  padding: 20px;
  box-shadow: var(--shadow-card);
}

.patient-link {
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 500;
}

.patient-link:hover { text-decoration: underline; }

.text-secondary { color: var(--color-text-secondary); font-size: 13px; }

.pagination { margin-top: 20px; justify-content: center; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>
