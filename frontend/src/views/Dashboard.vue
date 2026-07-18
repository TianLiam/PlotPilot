<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NIcon,
  NProgress,
  NTag,
  NSpace,
  NCard,
  NGrid,
  NGi,
  NSpin,
  NEmpty,
  NAvatar,
  NBadge,
} from 'naive-ui'
import {
  CreateOutline,
  BookOutline,
  FlagOutline,
  FlameOutline,
  WarningOutline,
  SparklesOutline,
  PulseOutline,
  TimeOutline,
  PeopleOutline,
  LocationOutline,
  BarChartOutline,
  ChevronForwardOutline,
  PlayOutline,
  FlashOutline,
  CheckmarkOutline,
  AlertCircleOutline,
  InformationCircleOutline,
} from '@vicons/ionicons5'
import { useStatsStore } from '../stores/statsStore'
import { novelApi, type NovelDTO } from '../api/novel'
import type { GlobalStats } from '../types/api'

const router = useRouter()
const statsStore = useStatsStore()

const loading = ref(true)
const novels = ref<NovelDTO[]>([])
const stats = ref({
  totalNovels: 0,
  totalWords: 0,
  totalChapters: 0,
  lockedGenres: 0,
})

const dailyGoal = 5000
const todayWords = 2847
const streakDays = 8
const dailyProgress = computed(() => Math.round((todayWords / dailyGoal) * 100))

const latestNovel = computed(() => novels.value[0] || null)
const hasNovels = computed(() => novels.value.length > 0)

function formatWordCount(count: number): string {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toLocaleString()
}

const aiReminders = [
  { type: 'warning', icon: WarningOutline, text: '第18章伏笔「青铜钥匙」还未回收' },
  { type: 'info', icon: PeopleOutline, text: '人物李牧已经 17 章没有出现' },
  { type: 'warning', icon: AlertCircleOutline, text: '世界观设定存在 2 处冲突，建议检查' },
  { type: 'success', icon: SparklesOutline, text: '建议下一章进入高潮桥段' },
]

const generatingTasks = [
  { novel: '末日序列', chapter: '第 38 章', progress: 65, eta: '32 秒' },
]

const recentActivity = [
  { time: '10:25', text: '修改了人物「李牧」的设定', type: 'edit' },
  { time: '09:48', text: 'AI 生成了第 37 章', type: 'generate' },
  { time: '昨天', text: '更新了世界观设定', type: 'edit' },
  { time: '昨天', text: '完成了第 36 章写作', type: 'write' },
  { time: '3 天前', text: '创建了新作品「星尘回响」', type: 'create' },
]

async function loadData() {
  loading.value = true
  try {
    const [novelsData, globalStats] = await Promise.all([
      novelApi.listNovels().catch(() => []),
      statsStore.loadGlobalStats().catch(() => null),
    ])
    novels.value = novelsData
    if (globalStats) {
      stats.value = {
        totalNovels: globalStats.total_books || 0,
        totalWords: globalStats.total_words || 0,
        totalChapters: globalStats.total_chapters || 0,
        lockedGenres: 0,
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function goNovel(id: string) {
  router.push(`/book/${id}/overview`)
}

function goWorkbench(id: string) {
  router.push(`/book/${id}/workbench`)
}

function goLibrary() {
  router.push('/library')
}

function goCreateNovel() {
  router.push('/studio')
}

function goMarket() {
  router.push('/market')
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="dashboard-page">
    <div class="dashboard-inner">
      <!-- 顶部欢迎 + 今日目标 -->
      <section class="hero-section">
        <div class="hero-main">
          <div class="greeting">
            <span class="greeting-eyebrow">
              <SparklesOutline class="greeting-icon" />
              AI 创作驾驶舱
            </span>
            <h1 class="greeting-title">
              {{ hasNovels ? `继续写《${latestNovel?.title}》` : '开始你的第一部长篇' }}
            </h1>
            <p class="greeting-desc">
              {{ hasNovels ? '昨天写到第 37 章，今天的目标是 5000 字。' : '从一句话梗概开始，建立你的长篇叙事工程。' }}
            </p>
          </div>
          <div class="hero-actions">
            <n-button
              v-if="hasNovels"
              type="primary"
              size="large"
              class="action-primary"
              @click="goWorkbench(latestNovel!.id)"
            >
              <template #icon><PlayOutline :size="16" /></template>
              继续创作
            </n-button>
            <n-button v-else type="primary" size="large" class="action-primary" @click="goCreateNovel">
              <template #icon><CreateOutline :size="16" /></template>
              创建作品
            </n-button>
            <n-button size="large" @click="goLibrary">
              <template #icon><BookOutline :size="16" /></template>
              作品库
            </n-button>
          </div>
        </div>

        <div class="hero-side">
          <div class="goal-card">
            <div class="goal-header">
              <div class="goal-icon-wrap">
                <FlagOutline class="goal-icon" />
              </div>
              <div class="goal-meta">
                <span class="goal-label">今日目标</span>
                <span class="goal-streak">
                  <FlameOutline class="streak-icon" />
                  连续 {{ streakDays }} 天
                </span>
              </div>
            </div>
            <div class="goal-stats">
              <span class="goal-current">{{ todayWords.toLocaleString() }}</span>
              <span class="goal-divider">/</span>
              <span class="goal-total">{{ dailyGoal.toLocaleString() }} 字</span>
            </div>
            <n-progress
              type="line"
              :percentage="dailyProgress"
              :show-indicator="false"
              :height="8"
              color="rgba(255,255,255,0.9)"
              rail-color="rgba(255,255,255,0.2)"
              style="margin-top: 12px"
            />
          </div>
        </div>
      </section>

      <!-- 快速数据概览 -->
      <section class="metrics-section">
        <n-grid :cols="4" :x-gap="16" :y-gap="16">
          <n-gi>
            <div class="metric-card">
              <div class="metric-icon blue">
                <BookOutline :size="20" />
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ stats.totalNovels }}</div>
                <div class="metric-label">进行中作品</div>
              </div>
            </div>
          </n-gi>
          <n-gi>
            <div class="metric-card">
              <div class="metric-icon purple">
                <CreateOutline :size="20" />
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ formatWordCount(stats.totalWords) }}</div>
                <div class="metric-label">累计字数</div>
              </div>
            </div>
          </n-gi>
          <n-gi>
            <div class="metric-card">
              <div class="metric-icon green">
                <BarChartOutline :size="20" />
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ stats.totalChapters }}</div>
                <div class="metric-label">已完成章节</div>
              </div>
            </div>
          </n-gi>
          <n-gi>
            <div class="metric-card">
              <div class="metric-icon orange">
                <FlashOutline :size="20" />
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ streakDays }}</div>
                <div class="metric-label">连续写作天数</div>
              </div>
            </div>
          </n-gi>
        </n-grid>
      </section>

      <!-- 主体三栏 -->
      <section class="main-grid">
        <!-- 左：最近作品 -->
        <div class="main-col col-left">
          <n-card class="section-card" :bordered="false">
            <template #header>
              <div class="card-header">
                <span class="card-title">最近作品</span>
                <n-button text type="primary" size="small" @click="goLibrary">
                  全部
                  <template #icon><ChevronForwardOutline :size="14" /></template>
                </n-button>
              </div>
            </template>

            <div v-if="loading" class="card-loading">
              <n-spin size="medium" />
            </div>
            <div v-else-if="novels.length === 0" class="card-empty">
              <n-empty description="还没有作品，去创建第一部吧" size="small" />
            </div>
            <div v-else class="novel-list">
              <div
                v-for="novel in novels.slice(0, 5)"
                :key="novel.id"
                class="novel-item"
                @click="goNovel(novel.id)"
              >
                <div class="novel-cover">
                  <span class="cover-text">{{ novel.title?.[0] || '?' }}</span>
                </div>
                <div class="novel-info">
                  <div class="novel-title-row">
                    <span class="novel-title">{{ novel.title }}</span>
                    <n-tag :type="novel.stage === 'writing' ? 'info' : 'success'" size="small" :bordered="false">
                      {{ novel.stage }}
                    </n-tag>
                  </div>
                  <div class="novel-meta">
                    <span>{{ novel.chapters?.length || 0 }} 章</span>
                    <span>·</span>
                    <span>{{ formatWordCount(novel.total_word_count || 0) }} 字</span>
                  </div>
                </div>
                <ChevronForwardOutline class="novel-arrow" :size="16" />
              </div>
            </div>
          </n-card>
        </div>

        <!-- 中：AI 提醒 -->
        <div class="main-col col-center">
          <n-card class="section-card ai-card" :bordered="false">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <SparklesOutline class="title-icon ai" :size="16" />
                  AI 提醒
                </span>
                <n-badge :value="aiReminders.length" type="warning" size="small">
                  <span></span>
                </n-badge>
              </div>
            </template>

            <div class="reminder-list">
              <div
                v-for="(item, idx) in aiReminders"
                :key="idx"
                class="reminder-item"
                :class="item.type"
              >
                <div class="reminder-icon-wrap">
                  <component :is="item.icon" class="reminder-icon" :size="16" />
                </div>
                <span class="reminder-text">{{ item.text }}</span>
                <ChevronForwardOutline class="reminder-arrow" :size="14" />
              </div>
            </div>

            <div class="ai-suggestion">
              <div class="suggestion-title">AI 建议下一步</div>
              <div class="suggestion-actions">
                <n-button size="small" type="primary" @click="hasNovels && goWorkbench(latestNovel!.id)">
                  <template #icon><PlayOutline :size="14" /></template>
                  继续写第 38 章
                </n-button>
                <n-button size="small">
                  <template #icon><CheckmarkOutline :size="14" /></template>
                  检查一致性
                </n-button>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 右：生成任务 + 最近活动 -->
        <div class="main-col col-right">
          <n-card v-if="generatingTasks.length > 0" class="section-card task-card" :bordered="false" style="margin-bottom: 16px">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <PulseOutline class="title-icon pulse" :size="16" />
                  生成中
                </span>
              </div>
            </template>
            <div
              v-for="task in generatingTasks"
              :key="task.novel + task.chapter"
              class="generating-item"
            >
              <div class="gen-info">
                <span class="gen-novel">{{ task.novel }}</span>
                <span class="gen-chapter">{{ task.chapter }}</span>
              </div>
              <div class="gen-progress">
                <n-progress
                  type="line"
                  :percentage="task.progress"
                  :show-indicator="false"
                  :height="4"
                  color="#3b82f6"
                  rail-color="rgba(59, 130, 246, 0.1)"
                />
                <span class="gen-eta">预计 {{ task.eta }}</span>
              </div>
            </div>
          </n-card>

          <n-card class="section-card" :bordered="false">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <TimeOutline class="title-icon" :size="16" />
                  最近活动
                </span>
              </div>
            </template>
            <div class="activity-list">
              <div
                v-for="(item, idx) in recentActivity"
                :key="idx"
                class="activity-item"
              >
                <span class="activity-time">{{ item.time }}</span>
                <span class="activity-text">{{ item.text }}</span>
              </div>
            </div>
          </n-card>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100%;
  background: var(--app-page-bg);
}

.dashboard-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* Hero */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  margin-bottom: 28px;
}

.hero-main {
  background: var(--app-surface);
  border-radius: var(--app-radius-xl);
  padding: 40px;
  border: 1px solid var(--app-border);
  position: relative;
  overflow: hidden;
}

.hero-main::before {
  content: '';
  position: absolute;
  top: -100px;
  right: -100px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, var(--color-brand-light) 0%, transparent 70%);
  pointer-events: none;
}

.greeting {
  position: relative;
  z-index: 1;
}

.greeting-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-brand);
  background: var(--color-brand-light);
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 16px;
}

.greeting-icon {
  width: 14px;
  height: 14px;
}

.greeting-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--app-text-primary);
  margin: 0 0 10px 0;
  line-height: 1.3;
}

.greeting-desc {
  font-size: 14px;
  color: var(--app-text-muted);
  margin: 0 0 28px 0;
  max-width: 480px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.action-primary {
  min-width: 140px;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.goal-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--app-radius-xl);
  padding: 28px;
  color: white;
  position: relative;
  overflow: hidden;
}

.goal-card::before {
  content: '';
  position: absolute;
  bottom: -60px;
  right: -60px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.goal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.goal-icon-wrap {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.goal-icon {
  width: 20px;
  height: 20px;
}

.goal-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.goal-label {
  font-size: 13px;
  opacity: 0.85;
}

.goal-streak {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  opacity: 0.75;
}

.streak-icon {
  width: 12px;
  height: 12px;
}

.goal-stats {
  display: flex;
  align-items: baseline;
  gap: 6px;
  position: relative;
  z-index: 1;
}

.goal-current {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.goal-divider {
  font-size: 18px;
  opacity: 0.4;
}

.goal-total {
  font-size: 14px;
  opacity: 0.75;
}

/* Metrics */
.metrics-section {
  margin-bottom: 28px;
}

.metric-card {
  background: var(--app-surface);
  border-radius: var(--app-radius-md);
  padding: 20px;
  border: 1px solid var(--app-border);
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.2s ease;
}

.metric-card:hover {
  box-shadow: var(--app-shadow-hover);
  transform: translateY(-2px);
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-icon.blue {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.metric-icon.purple {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.metric-icon.green {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.metric-icon.orange {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.metric-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--app-text-primary);
  line-height: 1.2;
}

.metric-label {
  font-size: 12px;
  color: var(--app-text-muted);
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 16px;
}

.main-col {
  display: flex;
  flex-direction: column;
}

.section-card {
  border-radius: var(--app-radius-lg);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  width: 16px;
  height: 16px;
}

.title-icon.ai {
  color: #8b5cf6;
}

.title-icon.pulse {
  color: #3b82f6;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.card-loading,
.card-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

/* Novel List */
.novel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.novel-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.18s ease;
}

.novel-item:hover {
  background: var(--app-surface-subtle);
}

.novel-cover {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  font-weight: 700;
  font-size: 18px;
}

.novel-info {
  flex: 1;
  min-width: 0;
}

.novel-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.novel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.novel-meta {
  font-size: 12px;
  color: var(--app-text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.novel-arrow {
  color: var(--app-text-muted);
  flex-shrink: 0;
}

/* AI Reminders */
.ai-card {
  background: linear-gradient(180deg, rgba(139, 92, 246, 0.03) 0%, var(--app-surface) 100%);
  border: 1px solid rgba(139, 92, 246, 0.1);
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--app-surface-subtle);
  cursor: pointer;
  transition: all 0.18s ease;
}

.reminder-item:hover {
  background: var(--color-brand-light);
}

.reminder-icon-wrap {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.reminder-item.warning .reminder-icon-wrap {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.reminder-item.info .reminder-icon-wrap {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.reminder-item.success .reminder-icon-wrap {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.reminder-icon {
  width: 14px;
  height: 14px;
}

.reminder-text {
  flex: 1;
  font-size: 13px;
  color: var(--app-text-secondary);
  line-height: 1.5;
}

.reminder-arrow {
  color: var(--app-text-muted);
  flex-shrink: 0;
}

.ai-suggestion {
  padding-top: 16px;
  border-top: 1px solid var(--app-divider);
}

.suggestion-title {
  font-size: 12px;
  color: var(--app-text-muted);
  margin-bottom: 10px;
}

.suggestion-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Generating */
.task-card {
  border: 1px solid rgba(59, 130, 246, 0.15);
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.03) 0%, var(--app-surface) 100%);
}

.generating-item {
  padding: 4px 0;
}

.gen-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.gen-novel {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.gen-chapter {
  font-size: 12px;
  color: var(--app-text-muted);
}

.gen-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gen-progress > :deep(.n-progress) {
  flex: 1;
}

.gen-eta {
  font-size: 11px;
  color: var(--app-text-muted);
  white-space: nowrap;
}

/* Activity */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 13px;
}

.activity-time {
  font-size: 11px;
  color: var(--app-text-muted);
  min-width: 48px;
  flex-shrink: 0;
}

.activity-text {
  color: var(--app-text-secondary);
  flex: 1;
}

@media (max-width: 1100px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .main-grid {
    grid-template-columns: 1fr 1fr;
  }

  .col-right {
    grid-column: span 2;
    flex-direction: row;
    gap: 16px;
  }

  .col-right .section-card {
    flex: 1;
  }

  .task-card {
    margin-bottom: 0 !important;
  }
}

@media (max-width: 768px) {
  .dashboard-inner {
    padding: 20px 16px;
  }

  .hero-main {
    padding: 28px 24px;
  }

  .greeting-title {
    font-size: 24px;
  }

  .goal-current {
    font-size: 28px;
  }

  .main-grid {
    grid-template-columns: 1fr;
  }

  .col-right {
    grid-column: span 1;
    flex-direction: column;
    gap: 16px;
  }

  .task-card {
    margin-bottom: 0 !important;
  }
}
</style>
