<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-inner">
        <button class="brand" type="button" aria-label="返回创作总览" @click="goHome">
          <span class="brand-logo" aria-hidden="true">叙</span>
          <span class="brand-copy">
            <span class="brand-line">
              <strong class="brand-name">{{ BRAND.chineseName }}</strong>
              <span class="brand-product">{{ BRAND.productName }}</span>
            </span>
            <span class="brand-tagline">{{ BRAND.tagline }}</span>
          </span>
        </button>

        <nav class="main-nav" aria-label="主导航">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            active-class="is-active"
          >
            <span class="nav-icon" aria-hidden="true">
              <component :is="item.icon" :size="17" />
            </span>
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </router-link>
        </nav>

        <div class="header-right">
          <n-button
            quaternary
            class="settings-button"
            aria-label="应用设置"
            @click="appSettingsShell.open()"
          >
            <template #icon>
              <n-icon :component="IconSettings" :size="19" />
            </template>
            <span class="settings-label">设置</span>
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
import { BRAND } from '@/constants/brand'

const router = useRouter()
const appSettingsShell = useAppSettingsShellStore()

const svgIcon = (path: string) => () =>
  h('svg', {
    xmlns: 'http://www.w3.org/2000/svg',
    viewBox: '0 0 24 24',
    width: '1em',
    height: '1em',
    fill: 'none',
    stroke: 'currentColor',
    'stroke-width': 1.8,
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
  }, h('path', { d: path }))

const IconDashboard = svgIcon('M4 4h6v6H4zM14 4h6v4h-6zM14 12h6v8h-6zM4 14h6v6H4z')
const IconTrending = svgIcon('M4 17l5-5 4 3 7-8M15 7h5v5')
const IconWorkshop = svgIcon('M5 3h10l4 4v14H5zM14 3v5h5M8 13h8M8 17h6')
const IconLibrary = svgIcon('M4 5.5l5-1.5v15l-5 1.5zM9 4l6 1.5v15L9 19zM15 5.5l5-1.5v15l-5 1.5z')
const IconSettings = svgIcon('M12 15.5a3.5 3.5 0 100-7 3.5 3.5 0 000 7zM19.4 15a1.7 1.7 0 00.3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 00-1.9-.3 1.7 1.7 0 00-1 1.6v.2h-4V21a1.7 1.7 0 00-1-1.6 1.7 1.7 0 00-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 00.3-1.9A1.7 1.7 0 003 14H2.8v-4H3a1.7 1.7 0 001.6-1 1.7 1.7 0 00-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 009 4.6 1.7 1.7 0 0010 3V2.8h4V3a1.7 1.7 0 001 1.6 1.7 1.7 0 001.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 00-.3 1.9 1.7 1.7 0 001.6 1h.2v4H21a1.7 1.7 0 00-1.6 1z')

const navItems = [
  { path: '/dashboard', label: '创作总览', icon: IconDashboard, badge: '' },
  { path: '/market', label: '市场洞察', icon: IconTrending, badge: '趋势' },
  { path: '/studio', label: '创作工坊', icon: IconWorkshop, badge: '' },
  { path: '/library', label: '作品库', icon: IconLibrary, badge: '' },
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
  flex: 0 0 auto;
  background: color-mix(in srgb, var(--app-surface) 92%, transparent);
  border-bottom: 1px solid var(--app-border);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.32) inset;
  backdrop-filter: blur(18px);
}

.header-inner {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto minmax(180px, 1fr);
  align-items: center;
  height: 68px;
  padding: 0 28px;
  max-width: 1600px;
  margin: 0 auto;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: center;
  justify-self: start;
  gap: 11px;
  padding: 0;
  color: inherit;
  background: transparent;
  border: 0;
  cursor: pointer;
  text-align: left;
}

.brand:focus-visible,
.nav-item:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 4px;
  border-radius: 10px;
}

.brand-logo {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  background: linear-gradient(145deg, #232a42, #111827);
  color: #f8f4e8;
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 700;
  border-radius: 10px;
  box-shadow: 0 5px 14px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

[data-theme='dark'] .brand-logo,
[data-theme='anchor'] .brand-logo {
  background: linear-gradient(145deg, color-mix(in srgb, var(--color-brand) 28%, #20283b), #0e1420);
}

.brand-copy,
.brand-line {
  display: flex;
  align-items: center;
}

.brand-copy {
  align-items: flex-start;
  flex-direction: column;
  gap: 1px;
}

.brand-line {
  gap: 7px;
  line-height: 1.1;
}

.brand-name {
  color: var(--app-text-primary);
  font-size: 16px;
  letter-spacing: 0.02em;
}

.brand-product {
  color: var(--app-text-muted);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.brand-tagline {
  color: var(--app-text-muted);
  font-size: 10px;
  letter-spacing: 0.08em;
}

.main-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 4px;
  background: var(--app-surface-subtle);
  border: 1px solid var(--app-border);
  border-radius: 13px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 7px;
  min-height: 36px;
  padding: 0 13px;
  border-radius: 9px;
  color: var(--app-text-secondary);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.nav-item:hover {
  color: var(--app-text-primary);
}

.nav-item.is-active {
  color: var(--color-brand);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
  font-weight: 650;
}

.nav-icon {
  display: flex;
  align-items: center;
  opacity: 0.82;
}

.nav-badge {
  padding: 1px 5px;
  border: 1px solid var(--color-brand-border);
  border-radius: 999px;
  color: var(--color-brand);
  background: var(--color-brand-light);
  font-size: 9px;
  font-weight: 700;
  line-height: 1.5;
}

.header-right {
  display: flex;
  justify-content: flex-end;
}

.settings-button {
  color: var(--app-text-secondary);
}

.settings-label {
  font-size: 13px;
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
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

@media (max-width: 1180px) {
  .header-inner {
    grid-template-columns: auto 1fr auto;
    gap: 14px;
    padding: 0 20px;
  }

  .brand-tagline,
  .brand-product {
    display: none;
  }

  .nav-item {
    padding: 0 10px;
  }
}

@media (max-width: 900px) {
  .header-inner {
    height: 62px;
    padding: 0 14px;
  }

  .brand-copy,
  .nav-label,
  .settings-label {
    display: none;
  }

  .main-nav {
    justify-self: center;
  }

  .nav-item {
    padding: 0 11px;
  }

  .nav-badge {
    position: absolute;
    top: 3px;
    right: 3px;
    width: 5px;
    height: 5px;
    padding: 0;
    overflow: hidden;
    border: 0;
    background: var(--color-brand);
  }
}

@media (max-width: 560px) {
  .header-inner {
    grid-template-columns: auto 1fr;
  }

  .header-right {
    display: none;
  }

  .brand-logo {
    width: 34px;
    height: 34px;
  }

  .main-nav {
    justify-self: end;
    max-width: calc(100vw - 66px);
    overflow-x: auto;
    scrollbar-width: none;
  }

  .main-nav::-webkit-scrollbar {
    display: none;
  }
}
</style>
