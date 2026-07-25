<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-inner">
        <!-- 品牌 -->
        <button class="brand" type="button" aria-label="返回创作总览" @click="goHome">
          <span class="brand-logo" aria-hidden="true">叙</span>
          <span class="brand-copy">
            <span class="brand-line">
              <strong class="brand-name">{{ BRAND.chineseName }}</strong>
              <span class="pro-badge is-dot">PRO</span>
            </span>
            <span class="brand-tagline">{{ BRAND.descriptor }}</span>
          </span>
        </button>

        <span class="topbar-divider" aria-hidden="true" />

        <!-- 主导航 -->
        <nav class="main-nav" aria-label="主导航">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            active-class="is-active"
          >
            <span class="nav-icon" aria-hidden="true">
              <component :is="item.icon" :size="16" />
            </span>
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </router-link>
        </nav>

        <!-- 右侧：搜索 + 引擎状态 + 操作 + 用户 -->
        <div class="header-right">
          <div class="cmd-search" role="button" tabindex="0" aria-label="全局搜索" @click="handleSearch" @keydown.enter="handleSearch">
            <span class="cmd-search-icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
            </span>
            <span class="cmd-search-text">搜索作品、章节、角色…</span>
            <span class="cmd-search-kbd">⌘ K</span>
          </div>

          <span class="engine-status" :class="engineStatusClass" :title="engineStatusTitle">
            <span class="engine-dot" aria-hidden="true" />
            <span class="engine-label">{{ engineStatusText }}</span>
          </span>

          <button class="topbar-icon-btn" type="button" aria-label="帮助中心" @click="handleHelp">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .8-1 1.7v.5"/><circle cx="12" cy="17" r="0.6" fill="currentColor"/></svg>
          </button>

          <button class="topbar-icon-btn" type="button" aria-label="通知中心" @click="handleNotifications">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6"/><path d="M10 19a2 2 0 0 0 4 0"/></svg>
            <span class="topbar-icon-dot" aria-hidden="true" />
          </button>

          <span class="topbar-divider" aria-hidden="true" />

          <n-dropdown
            trigger="click"
            placement="bottom-end"
            :options="userMenuOptions"
            @select="handleUserMenuSelect"
          >
            <div class="user-menu-trigger" role="button" tabindex="0" aria-label="用户菜单">
              <span class="user-avatar">墨</span>
              <span class="user-name">墨作者</span>
              <span class="user-caret">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
              </span>
            </div>
          </n-dropdown>
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
import { h, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon, NDropdown, useMessage } from 'naive-ui'
import type { DropdownOption } from 'naive-ui'
import { useAppSettingsShellStore } from '@/stores/appSettingsShellStore'
import { useThemeStore } from '@/stores/themeStore'
import { BRAND } from '@/constants/brand'

const router = useRouter()
const route = useRoute()
const appSettingsShell = useAppSettingsShellStore()
const themeStore = useThemeStore()
const message = useMessage()

const svgIcon = (path: string, opts: Record<string, number | string> = {}) => () =>
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
    ...opts,
  }, h('path', { d: path }))

const IconDashboard = svgIcon('M4 4h6v6H4zM14 4h6v4h-6zM14 12h6v8h-6zM4 14h6v6H4z')
const IconLibrary = svgIcon('M4 5.5l5-1.5v15l-5 1.5zM9 4l6 1.5v15L9 19zM15 5.5l5-1.5v15l-5 1.5z')

function renderIcon(icon: () => ReturnType<typeof h>) {
  return () => h(NIcon, { size: 16 }, { default: icon })
}

const navItems = [
  { path: '/dashboard', label: '开始写作', icon: IconDashboard, badge: '' },
  { path: '/library', label: '作品库', icon: IconLibrary, badge: '' },
]



// 引擎状态（基于主题模式 + 假数据，后续可接入真实状态）
const engineStatusClass = computed(() => {
  return 'is-idle'
})
const engineStatusText = computed(() => '引擎就绪')
const engineStatusTitle = computed(() => 'AI 引擎状态：就绪 · 点击查看详情')

function goHome() {
  router.push('/dashboard')
}

function handleSearch() {
  message.info('全局命令面板（⌘K）即将上线，敬请期待')
}

function handleHelp() {
  message.info('帮助中心建设中')
}

function handleNotifications() {
  message.info('暂无新通知')
}

function openSettings() {
  appSettingsShell.open()
}

function cycleTheme() {
  const order: Array<'light' | 'dark' | 'anchor'> = ['light', 'dark', 'anchor']
  const cur = themeStore.mode === 'auto' ? 'light' : (themeStore.mode as 'light' | 'dark' | 'anchor')
  const idx = order.indexOf(cur)
  const next = order[(idx + 1) % order.length]
  themeStore.setTheme(next)
  const labelMap = { light: '亮色', dark: '暗色', anchor: '黑金' } as const
  message.success(`已切换至${labelMap[next]}主题`)
}

function goLibrary() {
  router.push('/library')
}

function goStudio() {
  router.push('/studio')
}

const userMenuOptions = computed<DropdownOption[]>(() => [
  {
    label: '墨作者',
    key: 'header',
    type: 'render',
    render: () =>
      h('div', { style: 'padding: 8px 12px; min-width: 200px;' }, [
        h('div', { style: 'font-size: 14px; font-weight: 700; color: var(--app-text-primary);' }, '墨作者'),
        h('div', { style: 'font-size: 12px; color: var(--app-text-muted); margin-top: 2px;' }, 'Pro 会员 · 终身版'),
      ]),
  },
  { type: 'divider', key: 'd1' },
  { label: '作品库', key: 'library', icon: renderIcon(IconLibrary) },
  { type: 'divider', key: 'd2' },
  { label: '外观主题', key: 'theme', icon: renderIcon(IconDashboard) },
  { label: '偏好设置', key: 'settings', icon: renderIcon(IconDashboard) },
])

function handleUserMenuSelect(key: string) {
  switch (key) {
    case 'library':
      goLibrary()
      break
    case 'theme':
      cycleTheme()
      break
    case 'settings':
      openSettings()
      break
  }
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
  background: color-mix(in srgb, var(--app-surface) 94%, transparent);
  border-bottom: 1px solid var(--app-border);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.32) inset,
    0 1px 2px rgba(15, 23, 42, 0.03);
  backdrop-filter: blur(18px);
}

.header-inner {
  display: flex;
  align-items: center;
  gap: 18px;
  height: 60px;
  padding: 0 24px;
  max-width: 1680px;
  margin: 0 auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0;
  color: inherit;
  background: transparent;
  border: 0;
  cursor: pointer;
  text-align: left;
  flex-shrink: 0;
}

.brand:focus-visible,
.nav-item:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 4px;
  border-radius: 10px;
}

.brand-logo {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  background: linear-gradient(145deg, #232a42, #111827);
  color: #f8f4e8;
  font-family: var(--font-serif);
  font-size: 16px;
  font-weight: 700;
  border-radius: 9px;
  box-shadow:
    0 4px 12px rgba(15, 23, 42, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  flex-shrink: 0;
}

[data-theme='dark'] .brand-logo,
[data-theme='anchor'] .brand-logo {
  background: linear-gradient(145deg, color-mix(in srgb, var(--color-brand) 28%, #20283b), #0e1420);
}

[data-theme='anchor'] .brand-logo {
  background: linear-gradient(145deg, color-mix(in srgb, var(--color-gold) 28%, #1a1610), #0a0c10);
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(212, 168, 67, 0.25) inset;
}

.brand-copy {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  gap: 2px;
}

.brand-line {
  display: flex;
  align-items: center;
  gap: 7px;
  line-height: 1.1;
}

.brand-name {
  color: var(--app-text-primary);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.02em;
  font-family: var(--font-serif);
}

.brand-tagline {
  color: var(--app-text-muted);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: var(--font-mono);
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 7px;
  min-height: 34px;
  padding: 0 13px;
  border-radius: 8px;
  color: var(--app-text-muted);
  font-size: 13px;
  font-weight: 550;
  text-decoration: none;
  transition: color 0.18s ease, background 0.18s ease;
}

.nav-item:hover {
  color: var(--app-text-primary);
  background: var(--app-surface-subtle);
}

.nav-item.is-active {
  color: var(--color-brand);
  font-weight: 650;
}

.nav-item.is-active-group {
  color: var(--color-brand);
  font-weight: 650;
}

.nav-item.is-active::after,
.nav-item.is-active-group::after {
  content: '';
  position: absolute;
  left: 13px;
  right: 13px;
  bottom: -19px;
  height: 2px;
  background: var(--color-brand);
  border-radius: 2px 2px 0 0;
}

.nav-item-dropdown {
  padding-right: 10px;
}

.nav-dropdown-caret {
  display: inline-flex;
  opacity: 0.5;
  margin-left: 1px;
}

.nav-item:hover .nav-dropdown-caret {
  opacity: 0.85;
}

[data-theme='anchor'] .nav-item.is-active {
  color: var(--color-gold);
}
[data-theme='anchor'] .nav-item.is-active::after {
  background: var(--color-gold);
}

.nav-icon {
  display: flex;
  align-items: center;
  opacity: 0.85;
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
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.app-main {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  background: var(--app-page-bg);
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

/* ── 响应式 ── */
@media (max-width: 1280px) {
  .header-inner {
    gap: 14px;
    padding: 0 18px;
  }
  .brand-tagline {
    display: none;
  }
  .cmd-search {
    min-width: 220px;
  }
  .cmd-search-text {
    max-width: 120px;
  }
}

@media (max-width: 1080px) {
  .cmd-search {
    min-width: 0;
    width: 44px;
    padding: 0;
    justify-content: center;
  }
  .cmd-search-text,
  .cmd-search-kbd {
    display: none;
  }
  .engine-status .engine-label {
    display: none;
  }
  .user-menu-trigger .user-name {
    display: none;
  }
  .user-menu-trigger {
    padding: 3px;
  }
}

@media (max-width: 900px) {
  .header-inner {
    height: 56px;
    padding: 0 14px;
    gap: 10px;
  }
  .brand-copy {
    display: none;
  }
  .nav-label {
    display: none;
  }
  .nav-item {
    padding: 0 11px;
  }
  .nav-item.is-active::after {
    left: 6px;
    right: 6px;
    bottom: -16px;
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
  .topbar-divider {
    display: none;
  }
  .engine-status,
  .topbar-icon-btn[aria-label='帮助中心'] {
    display: none;
  }
}

@media (max-width: 560px) {
  .main-nav {
    margin-left: auto;
  }
  .header-right {
    margin-left: 0;
  }
  .brand-logo {
    width: 32px;
    height: 32px;
  }
}
</style>
