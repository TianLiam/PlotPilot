<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-inner">
        <div class="brand" @click="goHome">
          <span class="brand-logo">墨</span>
          <span class="brand-name">墨枢 · AI 爆款工厂</span>
        </div>

        <nav class="main-nav">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            active-class="is-active"
          >
            <span class="nav-icon">
              <component :is="item.icon" :size="18" />
            </span>
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </router-link>
        </nav>

        <div class="header-right">
          <n-button
            quaternary
            circle
            size="medium"
            aria-label="应用设置"
            @click="appSettingsShell.open()"
          >
            <template #icon>
              <n-icon :component="IconSettings" :size="20" />
            </template>
          </n-button>
        </div>
      </div>
    </header>

    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import { useAppSettingsShellStore } from '@/stores/appSettingsShellStore'

const router = useRouter()
const appSettingsShell = useAppSettingsShellStore()

const IconDashboard = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z' }))

const IconTrending = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z' }))

const IconWorkshop = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h6v6h6v10H6z' }))

const IconLibrary = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M4 6H2v14a2 2 0 002 2h14v-2H4V6zm16-4H8a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V4a2 2 0 00-2-2zm0 14H8V4h12v12zM10 6h8v2h-8zm0 4h8v2h-8zm0 4h5v2h-5z' }))

const IconSettings = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', {
      fill: 'currentColor',
      d: 'M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.49.49 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 00-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.49.49 0 00-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6A3.6 3.6 0 1112 8.4a3.6 3.6 0 010 7.2z',
    }))

const IconSubscription = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z' }))

const navItems = [
  { path: '/dashboard', label: '驾驶舱', icon: IconDashboard, badge: '' },
  { path: '/market', label: '市场洞察', icon: IconTrending, badge: 'New' },
  { path: '/studio', label: '创作工坊', icon: IconWorkshop, badge: '' },
  { path: '/library', label: '我的书架', icon: IconLibrary, badge: '' },
  { path: '/subscription', label: '会员订阅', icon: IconSubscription, badge: '' },
]

function goHome() {
  router.push('/dashboard')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  height: 100vh;
  overflow: hidden;
  background: var(--app-page-bg);
}

.app-header {
  position: relative;
  z-index: 100;
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 24px;
  max-width: 1600px;
  margin: 0 auto;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
}

.brand-logo {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-brand) 0%, var(--color-gold) 100%);
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  border-radius: 8px;
  letter-spacing: -0.02em;
}

.brand-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text-primary);
  letter-spacing: -0.01em;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  text-decoration: none;
  color: var(--app-text-secondary);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  position: relative;
}

.nav-item:hover {
  color: var(--app-text-primary);
  background: var(--app-surface-subtle);
}

.nav-item.is-active {
  color: var(--color-brand);
  background: var(--color-brand-light);
  font-weight: 600;
}

.nav-icon {
  display: flex;
  align-items: center;
}

.nav-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
  color: #fff;
  line-height: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.app-main {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 900px) {
  .header-inner {
    padding: 0 16px;
    gap: 12px;
  }

  .brand-name {
    display: none;
  }

  .nav-label {
    display: none;
  }

  .nav-item {
    padding: 8px 10px;
  }
}

@media (max-width: 600px) {
  .nav-badge {
    position: absolute;
    top: 4px;
    right: 4px;
    font-size: 9px;
    padding: 1px 4px;
  }
}
</style>
