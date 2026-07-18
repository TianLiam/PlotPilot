<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NButton, NStatistic, NGrid, NGi, NSpace, NProgress, NTag } from 'naive-ui'
import {
  CreateOutline,
  FlagOutline,
  FlameOutline,
  WarningOutline,
  TimeOutline,
  BookOutline,
  PeopleOutline,
  LocationOutline,
} from '@vicons/ionicons5'
import { novelApi, type NovelDTO } from '../../api/novel'
import { useStatsStore } from '../../stores/statsStore'

const route = useRoute()
const router = useRouter()
const statsStore = useStatsStore()

const novelId = computed(() => route.params.novelId as string)
const novel = ref<NovelDTO | null>(null)
const bookStats = ref<any>(null)
const loading = ref(true)

async function loadData() {
  loading.value = true
  try {
    const [novelData, statsData] = await Promise.all([
      novelApi.getNovel(novelId.value),
      statsStore.loadBookStats(novelId.value).catch(() => null),
    ])
    novel.value = novelData
    bookStats.value = statsData
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const dailyGoal = 5000
const todayWords = 2847
const dailyProgress = computed(() => Math.round((todayWords / dailyGoal) * 100))

const quickStats = computed(() => [
  { label: '总字数', value: bookStats.value?.total_words || 0, icon: BookOutline, color: '#3b82f6' },
  { label: '章节数', value: bookStats.value?.total_chapters || 0, icon: CreateOutline, color: '#8b5cf6' },
  { label: '人物数', value: 12, icon: PeopleOutline, color: '#22c55e' },
  { label: '地点数', value: 8, icon: LocationOutline, color: '#f59e0b' },
])

const aiReminders = [
  { type: 'warning', text: '第18章伏笔还未回收', icon: WarningOutline },
  { type: 'info', text: '人物李牧已经17章没有出现', icon: PeopleOutline },
  { type: 'warning', text: '世界观设定存在冲突，建议检查', icon: WarningOutline },
  { type: 'success', text: '建议下一章进入高潮桥段', icon: FlagOutline },
]

const recentActivity = [
  { time: '10:25', text: '修改了人物「李牧」的设定' },
  { time: '09:48', text: 'AI 生成了第 37 章' },
  { time: '昨天', text: '更新了世界观设定' },
  { time: '昨天', text: '完成了第 36 章写作' },
]

function goWorkbench() {
  router.push(`/book/${novelId.value}/workbench`)
}
</script>

<template>
  <div class="book-overview-page">
    <div class="overview-hero">
      <div class="hero-main">
        <div class="hero-title-row">
          <h1 class="hero-title">{{ novel?.title || '加载中...' }}</h1>
          <n-tag size="small" type="info">
            <template #icon><FlameOutline class="tag-icon" /></template>
            连续写作 8 天
          </n-tag>
        </div>
        <p class="hero-desc">{{ novel?.premise?.slice(0, 120) || '暂无简介' }}...</p>
        <n-space size="medium" style="margin-top: 20px">
          <n-button type="primary" size="large" @click="goWorkbench">
            <template #icon><CreateOutline /></template>
            继续创作
          </n-button>
          <n-button size="large">查看大纲</n-button>
        </n-space>
      </div>

      <div class="hero-side">
        <div class="goal-card">
          <div class="goal-header">
            <FlagOutline class="goal-icon" />
            <span class="goal-label">今日目标</span>
          </div>
          <div class="goal-value">
            <span class="goal-current">{{ todayWords.toLocaleString() }}</span>
            <span class="goal-divider">/</span>
            <span class="goal-total">{{ dailyGoal.toLocaleString() }}</span>
          </div>
          <n-progress
            type="line"
            :percentage="dailyProgress"
            :show-indicator="false"
            :height="6"
            color="#3b82f6"
            rail-color="rgba(59, 130, 246, 0.1)"
          />
        </div>
      </div>
    </div>

    <n-grid :cols="4" :x-gap="16" :y-gap="16" class="stats-grid">
      <n-gi v-for="stat in quickStats" :key="stat.label">
        <n-card hoverable class="stat-card">
          <div class="stat-card-inner">
            <div class="stat-icon" :style="{ background: stat.color + '15', color: stat.color }">
              <component :is="stat.icon" />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value.toLocaleString() }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <div class="overview-grid">
      <n-card title="AI 提醒" class="section-card">
        <template #header-extra>
          <n-button text size="small">全部</n-button>
        </template>
        <div class="reminder-list">
          <div v-for="(item, idx) in aiReminders" :key="idx" class="reminder-item">
            <component :is="item.icon" class="reminder-icon" :class="item.type" />
            <span class="reminder-text">{{ item.text }}</span>
          </div>
        </div>
      </n-card>

      <n-card title="最近活动" class="section-card">
        <template #header-extra>
          <n-button text size="small">更多</n-button>
        </template>
        <div class="activity-list">
          <div v-for="(item, idx) in recentActivity" :key="idx" class="activity-item">
            <span class="activity-time">{{ item.time }}</span>
            <span class="activity-text">{{ item.text }}</span>
          </div>
        </div>
      </n-card>
    </div>
  </div>
</template>

<style scoped>
.book-overview-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.overview-hero {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  margin-bottom: 24px;
}

.hero-main {
  background: var(--app-surface);
  border-radius: var(--app-radius-lg);
  padding: 32px;
  border: 1px solid var(--app-border);
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--app-text-primary);
  margin: 0;
}

.tag-icon {
  width: 14px;
  height: 14px;
}

.hero-desc {
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.7;
  margin: 0;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.goal-card {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: var(--app-radius-lg);
  padding: 24px;
  color: white;
}

.goal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  opacity: 0.9;
}

.goal-icon {
  width: 18px;
  height: 18px;
}

.goal-label {
  font-size: 13px;
  font-weight: 500;
}

.goal-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 12px;
}

.goal-current {
  font-size: 32px;
  font-weight: 700;
}

.goal-divider {
  font-size: 18px;
  opacity: 0.5;
}

.goal-total {
  font-size: 16px;
  opacity: 0.7;
}

.stats-grid {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: var(--app-radius-md);
}

.stat-card-inner {
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.stat-icon svg {
  width: 22px;
  height: 22px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--app-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: var(--app-text-muted);
}

.overview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.section-card {
  border-radius: var(--app-radius-md);
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--app-surface-subtle);
  border-radius: 8px;
  font-size: 13px;
  color: var(--app-text-secondary);
}

.reminder-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.reminder-icon.warning {
  color: var(--color-warning);
}

.reminder-icon.info {
  color: var(--color-info);
}

.reminder-icon.success {
  color: var(--color-success);
}

.reminder-text {
  flex: 1;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 13px;
}

.activity-time {
  color: var(--app-text-muted);
  font-size: 12px;
  min-width: 40px;
  flex-shrink: 0;
}

.activity-text {
  color: var(--app-text-secondary);
  flex: 1;
}

@media (max-width: 900px) {
  .book-overview-page {
    padding: 16px;
  }

  .overview-hero {
    grid-template-columns: 1fr;
  }

  .hero-main {
    padding: 20px;
  }

  .hero-title {
    font-size: 22px;
  }

  .stats-grid {
    --n-cols: 2;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
