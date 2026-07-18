<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import {
  ArrowBackOutline,
  SpeedometerOutline,
  CreateOutline,
  GitBranchOutline,
  PeopleOutline,
  EarthOutline,
  TimeOutline,
  BarChartOutline,
  SettingsOutline,
} from '@vicons/ionicons5'

const props = defineProps<{
  novelId: string
  novelTitle: string
}>()

const route = useRoute()
const router = useRouter()

const navItems = [
  { key: 'overview', label: '概览', icon: SpeedometerOutline, path: 'overview' },
  { key: 'workbench', label: '工作台', icon: CreateOutline, path: 'workbench' },
  { key: 'outline', label: '大纲', icon: GitBranchOutline, path: 'outline' },
  { key: 'characters', label: '人物', icon: PeopleOutline, path: 'characters' },
  { key: 'world', label: '世界观', icon: EarthOutline, path: 'world' },
  { key: 'timeline', label: '时间线', icon: TimeOutline, path: 'timeline' },
  { key: 'analytics', label: '数据分析', icon: BarChartOutline, path: 'analytics' },
  { key: 'settings', label: '设置', icon: SettingsOutline, path: 'settings' },
]

const activeKey = computed(() => {
  const path = route.path
  if (path.includes('/workbench') || path.includes('/chapter')) return 'workbench'
  if (path.includes('/characters') || path.includes('/cast') || path.includes('/character-graph')) return 'characters'
  if (path.includes('/world') || path.includes('/location-graph')) return 'world'
  if (path.includes('/outline')) return 'outline'
  if (path.includes('/timeline')) return 'timeline'
  if (path.includes('/analytics')) return 'analytics'
  if (path.includes('/settings')) return 'settings'
  return 'overview'
})

function goBack() {
  router.push('/library')
}

function navigateTo(key: string) {
  const item = navItems.find(i => i.key === key)
  if (item) {
    router.push(`/book/${props.novelId}/${item.path}`)
  }
}
</script>

<template>
  <div class="book-subnav">
    <div class="book-subnav-inner">
      <div class="book-subnav-left">
        <button class="back-btn" @click="goBack" title="返回作品库">
          <ArrowBackOutline class="back-icon" />
        </button>
        <div class="book-title-wrap">
          <h1 class="book-title">{{ novelTitle || '未命名作品' }}</h1>
        </div>
      </div>

      <nav class="book-nav">
        <div
          v-for="item in navItems"
          :key="item.key"
          class="nav-item"
          :class="{ active: activeKey === item.key }"
          @click="navigateTo(item.key)"
        >
          <component :is="item.icon" class="nav-icon" />
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </nav>

      <div class="book-subnav-right">
        <slot name="right" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-subnav {
  position: sticky;
  top: 0;
  z-index: 40;
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.book-subnav-inner {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 24px;
  gap: 16px;
  max-width: 100%;
  overflow-x: auto;
  scrollbar-width: none;
}

.book-subnav-inner::-webkit-scrollbar {
  display: none;
}

.book-subnav-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: var(--app-surface-subtle);
  border-radius: 8px;
  cursor: pointer;
  color: var(--app-text-muted);
  transition: all 0.18s ease;
}

.back-btn:hover {
  background: var(--color-brand-light);
  color: var(--color-brand);
}

.back-icon {
  width: 16px;
  height: 16px;
}

.book-title-wrap {
  display: flex;
  align-items: center;
}

.book-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.book-nav {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--app-text-muted);
  font-size: 13px;
  font-weight: 500;
  transition: all 0.18s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.nav-item:hover {
  background: var(--app-surface-subtle);
  color: var(--app-text-secondary);
}

.nav-item.active {
  background: var(--color-brand-light);
  color: var(--color-brand);
  font-weight: 600;
}

.nav-icon {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.nav-label {
  line-height: 1;
}

.book-subnav-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

@media (max-width: 900px) {
  .book-subnav-inner {
    padding: 0 14px;
    height: 44px;
  }

  .book-title {
    max-width: 120px;
    font-size: 14px;
  }

  .nav-item {
    padding: 5px 10px;
    font-size: 12px;
  }

  .nav-icon {
    width: 14px;
    height: 14px;
  }
}
</style>
