<script setup lang="ts">
import { ref } from 'vue'
import SideNav from './SideNav.vue'

const sidebarVisible = ref(true)

function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
}
</script>

<template>
  <div class="app-layout" :class="{ 'sidebar-hidden': !sidebarVisible }">
    <SideNav v-if="sidebarVisible" />

    <div class="main-content">
      <div class="mobile-header">
        <el-button link @click="toggleSidebar">
          <el-icon size="22"><Expand v-if="!sidebarVisible" /><Fold v-else /></el-icon>
        </el-button>
        <span class="mobile-title">中医问诊系统</span>
      </div>
      <div class="content-body">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s;
}

.app-layout.sidebar-hidden .main-content {
  margin-left: 0;
}

.mobile-header {
  display: none;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.mobile-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.content-body {
  flex: 1;
  padding: 24px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }

  .mobile-header {
    display: flex;
  }

  .content-body {
    padding: 16px;
  }
}
</style>
