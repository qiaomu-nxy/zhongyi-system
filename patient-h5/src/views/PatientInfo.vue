<template>
  <div class="page">
    <van-nav-bar title="基本信息" left-arrow @click-left="router.back()" />

    <van-form @submit="handleSubmit" class="form-body">
      <van-cell-group inset title="基本资料">
        <van-field v-model="form.name" name="name" label="姓名" placeholder="请输入姓名" readonly />
        <van-field v-model="form.phone" name="phone" label="手机号" readonly />
        <van-field name="gender" label="性别">
          <template #input>
            <van-radio-group v-model="form.gender" direction="horizontal">
              <van-radio name="男">男</van-radio>
              <van-radio name="女">女</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        <van-field
          v-model="form.birth_date"
          name="birth_date"
          label="出生日期"
          placeholder="YYYY-MM-DD"
          @click="showDatePicker = true"
          readonly
        />
      </van-cell-group>

      <van-cell-group inset title="健康史">
        <van-field name="medical_history" label="既往病史">
          <template #input>
            <div class="chip-group">
              <van-tag
                v-for="item in medicalOptions"
                :key="item"
                :type="form.medical_history.includes(item) ? 'success' : 'default'"
                size="medium"
                @click="toggleMedical(item)"
                class="chip"
              >{{ item }}</van-tag>
            </div>
          </template>
        </van-field>
        <van-field
          v-model="form.allergy_history"
          name="allergy_history"
          label="过敏史"
          placeholder="如：青霉素、花粉（无则留空）"
          type="textarea"
          rows="2"
          autosize
        />
      </van-cell-group>

      <div class="submit-area">
        <van-button type="primary" native-type="submit" block round :loading="loading">
          保存并继续
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="pickerDate"
        title="选择出生日期"
        :min-date="new Date(1930, 0, 1)"
        :max-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast } from 'vant'
import { createPatient } from '../api/patient'
import { usePatientStore } from '../stores/patient'

const router = useRouter()
const route = useRoute()
const store = usePatientStore()

const loading = ref(false)
const showDatePicker = ref(false)
const pickerDate = ref(['2000', '01', '01'])

const medicalOptions = ['糖尿病', '高血压', '心脏病', '肝病', '肾病', '无']

const form = ref({
  name: (route.query.name as string) || '',
  phone: (route.query.phone as string) || '',
  gender: '男',
  birth_date: '',
  medical_history: [] as string[],
  allergy_history: '',
})

function toggleMedical(item: string) {
  const idx = form.value.medical_history.indexOf(item)
  if (idx >= 0) {
    form.value.medical_history.splice(idx, 1)
  } else {
    if (item === '无') form.value.medical_history = ['无']
    else {
      form.value.medical_history = form.value.medical_history.filter(i => i !== '无')
      form.value.medical_history.push(item)
    }
  }
}

function onDateConfirm({ selectedValues }: any) {
  form.value.birth_date = selectedValues.join('-')
  showDatePicker.value = false
}

async function handleSubmit() {
  if (!form.value.name) return showToast('请填写姓名')
  loading.value = true
  try {
    const payload = {
      ...form.value,
      birth_date: form.value.birth_date || null,
      medical_history: form.value.medical_history.length ? form.value.medical_history : null,
      allergy_history: form.value.allergy_history || null,
    }
    const res: any = await createPatient(payload)
    store.setPatient(res.id, res.name, 0)
    router.replace('/records')
  } catch (e: any) {
    showToast(e.message || '提交失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { background: var(--color-bg); min-height: 100vh; }
.form-body { padding-top: 12px; }
.chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { cursor: pointer; }
:deep(.van-tag--success) { background: var(--color-primary); border-color: var(--color-primary); }
.submit-area { padding: 24px 16px; }
:deep(.van-button--primary) { background: var(--color-primary); border-color: var(--color-primary); height: 48px; }
</style>