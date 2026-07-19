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
  NSpin,
  NEmpty,
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

const STAGE_NAMES: Record<string, string> = {
  planning: '规划中',
  macro_planning: '宏观规划',
  act_planning: '幕级规划',
  writing: '撰写中',
  auditing: '审计中',
  reviewing: '待审阅',
  paused_for_review: '待审阅',
  completed: '已完成',
}

function formatStage(stage: string): string {
  return STAGE_NAMES[stage] || stage
}

function formatWordCount(count: number): string {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toLocaleString()
}

const aiReminders = ref<Array<{ type: string; icon?: typeof WarningOutline; text: string; action: string }>>([
  { type: 'warning', icon: WarningOutline, text: '第18章伏笔「青铜钥匙」还未回收', action: 'foreshadow' },
  { type: 'info', icon: PeopleOutline, text: '人物李牧已经 17 章没有出现', action: 'character' },
  { type: 'success', icon: SparklesOutline, text: '建议下一章进入高潮桥段', action: 'workbench' },
])

const generatingTasks = [
  { novel: '末日序列', chapter: '第 38 章', progress: 65, eta: '32 秒' },
]

const recentActivity = ref<Array<{ time: string; text: string; type: string }>>([
  { time: '10:25', text: '修改了人物「李牧」的设定', type: 'edit' },
  { time: '09:48', text: 'AI 生成了第 37 章', type: 'generate' },
  { time: '昨天', text: '完成了第 36 章写作', type: 'write' },
])

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

    const novelId = latestNovel.value?.id || ''
    const dashboardRes = await fetch(`/api/v1/dashboard/data?novel_id=${encodeURIComponent(novelId)}`)
      .then(res => res.json())
      .catch(() => null)

    if (dashboardRes) {
      if (dashboardRes.reminders && dashboardRes.reminders.length > 0) {
        aiReminders.value = dashboardRes.reminders.map((r: any) => ({
          ...r,
          icon: getIconForReminderType(r.type),
        }))
      }
      if (dashboardRes.activities && dashboardRes.activities.length > 0) {
        recentActivity.value = dashboardRes.activities
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getIconForReminderType(type: string) {
  switch (type) {
    case 'warning': return WarningOutline
    case 'success': return SparklesOutline
    default: return PeopleOutline
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

function handleReminderClick(item: { action?: string }) {
  if (!item.action || !hasNovels || !latestNovel.value) return
  const novel = latestNovel.value
  
  switch (item.action) {
    case 'foreshadow':
      router.push(`/book/${novel.id}/workbench`)
      break
    case 'character':
      router.push(`/book/${novel.id}/characters`)
      break
    case 'workbench':
    default:
      router.push(`/book/${novel.id}/workbench`)
      break
  }
}

function handleContinueWriting() {
  if (hasNovels.value && latestNovel.value) {
    goWorkbench(latestNovel.value.id)
  } else {
    goCreateNovel()
  }
}

function handleCheckConsistency() {
  if (hasNovels.value && latestNovel.value) {
    goWorkbench(latestNovel.value.id)
  } else {
    goCreateNovel()
  }
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
        <div class="hero-main hero-banner-pro">
          <div class="hero-decorations" aria-hidden="true">
            <span class="deco-orb orb-1" />
            <span class="deco-orb orb-2" />
            <span class="deco-grid" />
          </div>
          <div class="hero-left">
            <div class="greeting">
              <span class="greeting-eyebrow">
                <SparklesOutline class="greeting-icon" />
                AI 创作驾驶舱
                <span class="pro-badge is-dot" style="margin-left: 4px">PRO</span>
              </span>
              <h1 class="greeting-title">
                {{ hasNovels ? `继续写《${latestNovel?.title}》` : '开始你的第一部长篇' }}
              </h1>
              <p class="greeting-desc">
                {{ hasNovels ? `已完成 ${latestNovel?.chapters?.length || 0} 章，共 ${formatWordCount(latestNovel?.total_word_count || 0)} 字，继续保持创作节奏。` : '从一句话梗概开始，建立你的长篇叙事工程。' }}
              </p>
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
                <n-button size="large" class="action-secondary" @click="goLibrary">
                  <template #icon><BookOutline :size="16" /></template>
                  作品库
                </n-button>
              </div>
            </div>
          </div>
          <div class="hero-right">
            <div class="hero-right-top">
              <div class="hero-side-card">
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
                  <span class="metric-trend is-up" title="较昨日">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 15 6-6 6 6"/></svg>
                    +18%
                  </span>
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
                  color="var(--color-brand)"
                  rail-color="var(--app-border)"
                  style="margin-top: 14px"
                />
                <div class="goal-foot">
                  <span class="goal-foot-item">
                    <span class="goal-foot-dot"></span>
                    还差 {{ Math.max(0, dailyGoal - todayWords).toLocaleString() }} 字达成今日目标
                  </span>
                </div>
              </div>
            </div>
            <div class="hero-right-bottom">
              <div class="hero-metrics">
                <div class="metric-card surface-pro">
                  <div class="metric-icon blue">
                    <BookOutline :size="16" />
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ stats.totalNovels }}</div>
                    <div class="metric-label">进行中作品</div>
                  </div>
                  <span class="metric-trend is-up" title="较上周">+2</span>
                </div>
                <div class="metric-card surface-pro">
                  <div class="metric-icon purple">
                    <CreateOutline :size="16" />
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ formatWordCount(stats.totalWords) }}</div>
                    <div class="metric-label">累计字数</div>
                  </div>
                  <span class="metric-trend is-up" title="较上周">+12.4%</span>
                </div>
                <div class="metric-card surface-pro">
                  <div class="metric-icon green">
                    <BarChartOutline :size="16" />
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ stats.totalChapters }}</div>
                    <div class="metric-label">已完成章节</div>
                  </div>
                  <span class="metric-trend is-up" title="较上周">+8</span>
                </div>
                <div class="metric-card surface-pro">
                  <div class="metric-icon orange">
                    <FlashOutline :size="16" />
                  </div>
                  <div class="metric-info">
                    <div class="metric-value">{{ streakDays }}</div>
                    <div class="metric-label">连续写作天数</div>
                  </div>
                  <span class="metric-trend is-flat" title="保持">持平</span>
                </div>
              </div>
            </div>
          </div>
        </div>
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
                v-for="novel in novels.slice(0, 4)"
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
                      {{ formatStage(novel.stage) }}
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
                @click="handleReminderClick(item)"
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
                <n-button size="small" type="primary" @click="handleContinueWriting">
                  <template #icon><PlayOutline :size="14" /></template>
                  {{ hasNovels ? '继续写第 38 章' : '开始创作' }}
                </n-button>
                <n-button size="small" @click="handleCheckConsistency">
                  <template #icon><CheckmarkOutline :size="14" /></template>
                  {{ hasNovels ? '检查一致性' : '检查设定' }}
                </n-button>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 右：生成任务 + 最近活动 -->
        <div class="main-col col-right">
          <n-card v-if="generatingTasks.length > 0" class="section-card task-card" :bordered="false" style="margin-bottom: 0">
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
  height: 100%;
  background: var(--app-page-bg);
  display: flex;
  flex-direction: column;
}

.dashboard-inner {
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 24px 24px 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

/* Hero */
.hero-section {
  display: block;
  flex: 0 0 auto;
  margin-bottom: 0;
}

.hero-main {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 28px;
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  align-items: stretch;
}

.hero-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  z-index: 1;
  min-width: 0;
}

.hero-right {
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: relative;
  z-index: 1;
  min-width: 0;
}

.hero-right-top {
  flex-shrink: 0;
}

.hero-right-top .hero-side-card {
  width: 100%;
}

.hero-right-bottom {
  flex: 1;
  min-height: 0;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 10px;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
}

/* 装饰：光晕 + 网格 */
.hero-decorations {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
.deco-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.55;
}
.deco-orb.orb-1 {
  top: -80px;
  right: -60px;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, var(--color-brand) 0%, transparent 70%);
}
.deco-orb.orb-2 {
  bottom: -100px;
  left: 30%;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, var(--color-gold) 0%, transparent 70%);
  opacity: 0.25;
}
.deco-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--app-border) 1px, transparent 1px),
    linear-gradient(90deg, var(--app-border) 1px, transparent 1px);
  background-size: 32px 32px;
  opacity: 0.35;
  mask-image: radial-gradient(ellipse 70% 60% at 100% 0%, #000 0%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse 70% 60% at 100% 0%, #000 0%, transparent 70%);
}

.greeting {
  position: relative;
}

.greeting-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-brand);
  background: var(--color-brand-light);
  border: 1px solid var(--color-brand-border);
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 18px;
  letter-spacing: 0.02em;
}
[data-theme='anchor'] .greeting-eyebrow {
  color: var(--color-gold);
}

.greeting-icon {
  width: 14px;
  height: 14px;
}

.greeting-title {
  font-size: clamp(28px, 3.2vw, 38px);
  font-weight: 700;
  color: var(--app-text-primary);
  margin: 0 0 12px 0;
  line-height: 1.2;
  letter-spacing: -0.02em;
  font-family: var(--font-serif);
}

.greeting-desc {
  font-size: 14px;
  color: var(--app-text-secondary);
  margin: 0 0 24px 0;
  max-width: 520px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 12px;
  position: relative;
  flex-wrap: wrap;
}

.action-primary {
  min-width: 140px;
  box-shadow: 0 4px 14px var(--color-brand-border);
}
.action-secondary {
  background: var(--app-surface);
  border: 1px solid var(--app-border-strong);
  color: var(--app-text-primary);
}
.action-secondary:hover {
  border-color: var(--color-brand-border);
  background: var(--app-surface);
}

/* 今日目标卡（嵌在 hero 内） */
.hero-side-card {
  position: relative;
  background: color-mix(in srgb, var(--app-surface) 88%, transparent);
  backdrop-filter: blur(8px);
  border: 1px solid var(--app-border-strong);
  border-radius: var(--app-radius-lg);
  padding: 18px 22px;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.5) inset,
    var(--app-shadow-md);
}
[data-theme='dark'] .hero-side-card,
[data-theme='anchor'] .hero-side-card {
  background: color-mix(in srgb, var(--app-surface) 78%, transparent);
}

.goal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.goal-icon-wrap {
  width: 38px;
  height: 38px;
  background: var(--color-brand-light);
  color: var(--color-brand);
  border: 1px solid var(--color-brand-border);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
[data-theme='anchor'] .goal-icon-wrap {
  background: var(--color-gold-dim);
  color: var(--color-gold);
  border-color: var(--color-gold-border);
}

.goal-icon {
  width: 18px;
  height: 18px;
}

.goal-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.goal-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.goal-streak {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-warning);
  font-weight: 500;
}

.streak-icon {
  width: 12px;
  height: 12px;
}

.goal-stats {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.goal-current {
  font-size: 38px;
  font-weight: 700;
  line-height: 1;
  color: var(--app-text-primary);
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}

.goal-divider {
  font-size: 18px;
  color: var(--app-text-muted);
  font-weight: 400;
}

.goal-total {
  font-size: 14px;
  color: var(--app-text-muted);
}

.goal-foot {
  margin-top: 12px;
  display: flex;
  align-items: center;
}
.goal-foot-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: var(--app-text-muted);
}
.goal-foot-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-brand);
}

/* Metrics */
.metric-card {
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
  height: 100%;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
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
  gap: 1px;
  flex: 1;
  min-width: 0;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text-primary);
  line-height: 1.2;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}

.metric-label {
  font-size: 12px;
  color: var(--app-text-muted);
  font-weight: 500;
}

.metric-trend {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-mono);
  line-height: 1.4;
}

.metric-trend.is-up {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.metric-trend.is-down {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.metric-trend.is-flat {
  background: rgba(148, 163, 184, 0.12);
  color: var(--app-text-muted);
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  grid-template-rows: 1fr;
  gap: 10px;
  align-items: stretch;
  flex: 1;
  min-height: 0;
}

.main-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
  height: 100%;
}

.main-col > .section-card,
.main-col > .task-card {
  flex: 1;
  min-height: 0;
  height: 100%;
}

.section-card {
  border-radius: var(--app-radius-md);
  --n-padding-bottom: 12px !important;
  --n-padding-top: 12px !important;
  --n-padding-left: 16px !important;
  --n-padding-right: 16px !important;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.section-card :deep(.n-card) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.section-card :deep(.n-card__content) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.section-card :deep(.n-card-header) {
  padding-bottom: 10px !important;
  flex-shrink: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-title {
  font-size: 14px;
  font-weight: 650;
  color: var(--app-text-primary);
  display: flex;
  align-items: center;
  gap: 7px;
}

.title-icon {
  width: 15px;
  height: 15px;
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
  padding: 32px 16px;
  flex: 1;
}

/* Novel List */
.novel-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-height: 0;
  justify-content: flex-start;
}

.novel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 8px;
  border-radius: 9px;
  cursor: pointer;
  transition: all 0.18s ease;
}

.novel-item:hover {
  background: var(--app-surface-subtle);
}

.novel-cover {
  width: 38px;
  height: 38px;
  border-radius: 7px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  font-weight: 700;
  font-size: 15px;
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
  width: 14px;
  height: 14px;
  opacity: 0.6;
}

/* AI Reminders */
.ai-card {
  background: linear-gradient(180deg, rgba(139, 92, 246, 0.03) 0%, var(--app-surface) 100%);
  border: 1px solid rgba(139, 92, 246, 0.1);
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 0;
  flex: 1;
  min-height: 0;
  justify-content: flex-start;
  overflow-y: auto;
  max-height: 180px;
  padding-right: 4px;
  scrollbar-width: thin;
}

.reminder-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 9px;
  background: var(--app-surface-subtle);
  cursor: pointer;
  transition: all 0.18s ease;
  border: 1px solid transparent;
}

.reminder-item:hover {
  background: var(--color-brand-light);
  border-color: rgba(139, 92, 246, 0.12);
  transform: translateX(2px);
}

.reminder-icon-wrap {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
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
  flex-shrink: 0;
}

.reminder-text {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  color: var(--app-text-secondary);
  line-height: 1.55;
  overflow-wrap: break-word;
  word-break: break-word;
  padding-top: 2px;
}

.reminder-arrow {
  width: 13px;
  height: 13px;
  color: var(--app-text-muted);
  flex-shrink: 0;
  margin-top: 4px;
  opacity: 0.6;
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.reminder-item:hover .reminder-arrow {
  opacity: 1;
  transform: translateX(2px);
}

.ai-suggestion {
  padding-top: 10px;
  border-top: 1px solid var(--app-divider);
  flex-shrink: 0;
}

.suggestion-title {
  font-size: 12px;
  color: var(--app-text-muted);
  margin-bottom: 8px;
}

.suggestion-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.suggestion-actions :deep(.n-button) {
  font-size: 12px;
}

.suggestion-actions :deep(.n-button .n-button__content) {
  gap: 4px;
}

/* Generating */
.task-card {
  border: 1px solid rgba(59, 130, 246, 0.15);
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.03) 0%, var(--app-surface) 100%);
}

.generating-item {
  padding: 4px 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 0;
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
  flex: 1;
  min-height: 0;
  justify-content: flex-start;
  overflow-y: auto;
  max-height: 160px;
  padding-right: 4px;
  scrollbar-width: thin;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 5px 0;
  font-size: 13px;
}

.activity-time {
  font-size: 11px;
  color: var(--app-text-muted);
  min-width: 44px;
  flex-shrink: 0;
  text-align: right;
}

.activity-text {
  color: var(--app-text-secondary);
  flex: 1;
}

@media (max-width: 1100px) {
  .hero-main {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 28px;
  }

  .hero-metrics {
    grid-template-columns: repeat(4, minmax(0, 1fr));
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
    padding: 24px 20px;
    gap: 20px;
  }

  .hero-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
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

  .deco-grid {
    opacity: 0.2;
  }
}
</style>
