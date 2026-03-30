<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const menuItems = [
  { path: '/dashboard', icon: 'House', label: '今日就诊' },
  { path: '/patients', icon: 'User', label: '患者管理' },
  { path: '/appointments', icon: 'Calendar', label: '预约管理' },
  { path: '/analysis', icon: 'DataAnalysis', label: '数据分析' },
  { path: '/backup', icon: 'Download', label: '数据备份' },
]

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="side-nav">
    <div class="logo-area">
      <div class="logo-icon">中</div>
      <span class="logo-text">中医问诊系统</span>
    </div>

    <nav class="menu">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="menu-item"
        :class="{ active: route.path.startsWith(item.path) && item.path !== '/' }"
      >
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="user-area">
      <div class="user-info">
        <div class="user-avatar">{{ auth.doctor?.name?.[0] ?? '医' }}</div>
        <div class="user-detail">
          <div class="user-name">{{ auth.doctor?.name }}</div>
          <div class="user-role">{{ auth.doctor?.role === 'admin' ? '管理员' : '医师' }}</div>
        </div>
      </div>
      <el-button link class="logout-btn" @click="handleLogout">
        <el-icon><SwitchButton /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.side-nav {
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--color-sidebar);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: var(--color-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

.logo-text {
  color: white;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.menu {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: var(--color-sidebar-hover);
  color: rgba(255, 255, 255, 0.9);
}

.menu-item.active {
  background: rgba(93, 179, 145, 0.15);
  color: var(--color-primary);
  border-left-color: var(--color-primary);
}

.menu-item .el-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.user-area {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-detail {
  min-width: 0;
}

.user-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  color: rgba(255, 255, 255, 0.45);
  font-size: 11px;
}

.logout-btn {
  color: rgba(255, 255, 255, 0.45) !important;
  padding: 4px !important;
}

.logout-btn:hover {
  color: var(--color-danger) !important;
}
</style>
