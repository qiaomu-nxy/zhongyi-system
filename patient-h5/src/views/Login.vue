<template>
  <div class="login-page">
    <div class="logo-area">
      <div class="logo-icon">中医</div>
      <h1 class="logo-title">问诊系统</h1>
      <p class="logo-sub">填写信息，快速就诊</p>
    </div>

    <div class="form-card">
      <van-cell-group inset>
        <van-field
          v-model="phone"
          label="手机号"
          placeholder="请输入11位手机号"
          type="tel"
          maxlength="11"
          :error-message="phoneError"
          clearable
        />
        <van-field
          v-model="name"
          label="姓名"
          placeholder="请输入您的姓名"
          :error-message="nameError"
          clearable
        />
      </van-cell-group>

      <div class="btn-area">
        <van-button
          type="primary"
          block
          round
          :loading="loading"
          loading-text="查询中..."
          @click="handleLogin"
        >
          进入问诊
        </van-button>
      </div>
    </div>

    <p class="tip">首次使用将引导您填写基本信息</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { patientLogin } from '../api/auth'
import { usePatientStore } from '../stores/patient'

const router = useRouter()
const store = usePatientStore()

const phone = ref('')
const name = ref('')
const phoneError = ref('')
const nameError = ref('')
const loading = ref(false)

onMounted(() => {
  store.loadFromStorage()
  if (store.patientId) {
    router.replace('/records')
  }
})

function validate(): boolean {
  phoneError.value = ''
  nameError.value = ''
  if (!/^\d{11}$/.test(phone.value)) {
    phoneError.value = '请输入11位手机号'
    return false
  }
  if (!name.value.trim()) {
    nameError.value = '请输入姓名'
    return false
  }
  return true
}

async function handleLogin() {
  if (!validate()) return
  loading.value = true
  try {
    const res: any = await patientLogin(phone.value, name.value.trim())
    if (res.exists) {
      store.setPatient(res.patient_id, res.name, res.visit_count)
      router.replace('/records')
    } else {
      // 新患者：跳转填写基本信息，携带手机号和姓名
      router.push({ path: '/info', query: { phone: phone.value, name: name.value.trim() } })
    }
  } catch (e: any) {
    showToast(e.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--color-primary-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 24px 32px;
}

.logo-area {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 72px;
  height: 72px;
  background: var(--color-primary);
  color: #fff;
  border-radius: 20px;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 4px 16px rgba(93, 179, 145, 0.35);
}

.logo-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 6px;
}

.logo-sub {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.form-card {
  width: 100%;
  background: var(--color-card);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  margin-bottom: 24px;
}

.btn-area {
  padding: 20px 16px;
}

:deep(.van-button--primary) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  height: 48px;
  font-size: 16px;
}

.tip {
  font-size: 13px;
  color: var(--color-text-secondary);
}
</style>