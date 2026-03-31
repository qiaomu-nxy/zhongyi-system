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
        <van-field name="birth_date" label="出生日期">
          <template #input>
            <input
              type="date"
              v-model="form.birth_date"
              class="date-input"
              min="1930-01-01"
              :max="today"
            />
          </template>
        </van-field>
      </van-cell-group>

      <van-cell-group inset title="健康史">
        <van-field name="medical_history" label="既往病史">
          <template #input>
            <div class="medical-wrap">
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
              <div class="custom-input-row">
                <input
                  v-model="customMedical"
                  class="custom-input"
                  placeholder="其他病史，输入后按回车添加"
                  @keyup.enter="addCustomMedical"
                />
                <span class="add-btn" @click="addCustomMedical">添加</span>
              </div>
              <div v-if="customTags.length" class="chip-group" style="margin-top:6px">
                <van-tag
                  v-for="tag in customTags"
                  :key="tag"
                  type="success"
                  size="medium"
                  closeable
                  @close="removeCustom(tag)"
                  class="chip"
                >{{ tag }}</van-tag>
              </div>
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
const today = new Date().toISOString().split('T')[0]

const medicalOptions = ['糖尿病', '高血压', '心脏病', '冠心病', '脑梗', '高血脂', '痛风', '肝病', '肾病', '甲状腺疾病', '肿瘤', '骨质疏松', '无']
const customMedical = ref('')

const form = ref({
  name: (route.query.name as string) || '',
  phone: (route.query.phone as string) || '',
  gender: '男',
  birth_date: '',
  medical_history: [] as string[],
  allergy_history: '',
})

// 用户手动输入的自定义标签（不在预设选项里）
const customTags = ref<string[]>([])

function addCustomMedical() {
  const val = customMedical.value.trim()
  if (!val) return
  if (medicalOptions.includes(val) || customTags.value.includes(val) || form.value.medical_history.includes(val)) {
    customMedical.value = ''
    return
  }
  // 选了"无"时清除
  form.value.medical_history = form.value.medical_history.filter(i => i !== '无')
  customTags.value.push(val)
  form.value.medical_history.push(val)
  customMedical.value = ''
}

function removeCustom(tag: string) {
  customTags.value = customTags.value.filter(t => t !== tag)
  form.value.medical_history = form.value.medical_history.filter(t => t !== tag)
}

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
.date-input {
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--color-text);
  background: transparent;
  width: 100%;
}
.page { background: var(--color-bg); min-height: 100vh; }
.form-body { padding-top: 12px; }
.medical-wrap { width: 100%; }
.chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { cursor: pointer; }
.custom-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}
.custom-input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 13px;
  outline: none;
  color: var(--color-text);
}
.custom-input:focus { border-color: var(--color-primary); }
.add-btn {
  color: var(--color-primary);
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  padding: 4px 2px;
}
:deep(.van-tag--success) { background: var(--color-primary); border-color: var(--color-primary); }
.submit-area { padding: 24px 16px; }
:deep(.van-button--primary) { background: var(--color-primary); border-color: var(--color-primary); height: 48px; }
</style>