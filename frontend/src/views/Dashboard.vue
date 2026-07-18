<template>
  <div class="dashboard">
    <div class="dashboard-bg" aria-hidden="true" />

    <div class="dashboard-inner">
      <section class="command-hero">
        <div class="hero-copy">
          <div class="hero-eyebrow">
            <span class="eyebrow-dot" aria-hidden="true" />
            创作驾驶舱
            <span>Creative command center</span>
          </div>
          <h1 class="hero-title">
            把故事写长，<br>
            <span>也始终写得前后一致。</span>
          </h1>
          <p class="hero-description">
            从宏观结构到每一章的角色状态、因果链与伏笔台账，
            在同一个叙事工作流里持续推进你的作品。
          </p>
          <div class="hero-actions">
            <n-button type="primary" size="large" class="hero-primary" @click="goHeroAction">
              <template #icon>
                <n-icon :component="hasNovels ? IconPen : IconAdd" :size="18" />
              </template>
              {{ hasNovels ? '继续最近创作' : '创建第一部作品' }}
            </n-button>
            <n-button size="large" class="hero-secondary" @click="goLibrary">
              查看作品库
            </n-button>
          </div>
        </div>

        <aside class="hero-status" aria-label="今日创作状态">
          <div class="status-topline">
            <span>今日 · {{ todayStr }}</span>
            <span class="system-ready"><i /> 叙事系统就绪</span>
          </div>
          <div class="status-focus">
            <span class="status-label">当前焦点</span>
            <strong>{{ latestNovelTitle }}</strong>
            <p>{{ hasNovels ? '继续梳理下一章的目标、冲突与状态变化。' : '从一句话梗概开始，建立你的长篇叙事工程。' }}</p>
          </div>
          <div class="status-flow" aria-label="创作流程">
            <span>结构规划</span>
            <i />
            <span>章节创作</span>
            <i />
            <span>一致性校验</span>
          </div>
        </aside>
      </section>

      <section class="metrics-grid" aria-label="创作数据概览">
        <article class="metric-card">
          <span class="metric-icon"><n-icon :component="IconBook" :size="19" /></span>
          <div class="metric-copy">
            <span class="metric-label">进行中作品</span>
            <strong class="metric-value numeric">{{ stats.totalNovels }}</strong>
          </div>
          <span class="metric-note">部</span>
        </article>
        <article class="metric-card">
          <span class="metric-icon"><n-icon :component="IconPen" :size="19" /></span>
          <div class="metric-copy">
            <span class="metric-label">累计正文</span>
            <strong class="metric-value numeric">{{ formatWordCount(stats.totalWords) }}</strong>
          </div>
          <span class="metric-note">字</span>
        </article>
        <article class="metric-card">
          <span class="metric-icon"><n-icon :component="IconChapters" :size="19" /></span>
          <div class="metric-copy">
            <span class="metric-label">已完成章节</span>
            <strong class="metric-value numeric">{{ stats.totalChapters }}</strong>
          </div>
          <span class="metric-note">章</span>
        </article>
        <article class="metric-card">
          <span class="metric-icon"><n-icon :component="IconPulse" :size="19" /></span>
          <div class="metric-copy">
            <span class="metric-label">题材已锁定</span>
            <strong class="metric-value numeric">{{ stats.lockedGenres }}</strong>
          </div>
          <span class="metric-note">部</span>
        </article>
      </section>

      <section class="primary-grid">
        <article class="surface-panel progress-panel">
          <header class="panel-header">
            <div>
              <span class="panel-kicker">Work in progress</span>
              <h2 class="panel-title">进行中的作品</h2>
            </div>
            <n-button text type="primary" size="small" @click="goLibrary">
              查看全部作品
              <template #icon><n-icon :component="IconArrow" /></template>
            </n-button>
          </header>

          <div v-if="loading" class="loading-state">
            <n-spin size="medium" />
          </div>

          <div v-else-if="novels.length === 0" class="empty-state">
            <div class="empty-mark"><n-icon :component="IconBook" :size="28" /></div>
            <div class="empty-copy">
              <strong>你的下一部长篇，从一个清晰的故事核心开始</strong>
              <p>先写下题材与一句话梗概，再逐步建立角色、世界与章节结构。</p>
            </div>
            <n-button type="primary" @click="goCreateNovel">开始建档</n-button>
          </div>

          <div v-else class="novel-progress-list">
            <button
              v-for="novel in displayNovels"
              :key="novel.slug"
              type="button"
              class="novel-progress-item"
              @click="goNovel(novel.slug)"
            >
              <div class="novel-heading">
                <span class="novel-index" aria-hidden="true">{{ String(displayNovels.indexOf(novel) + 1).padStart(2, '0') }}</span>
                <div class="novel-info">
                  <div class="novel-title-row">
                    <span class="novel-title">{{ novel.title }}</span>
                    <n-tag :type="getStageType(novel.stage)" size="small" round :bordered="false">
                      {{ novel.stage_label }}
                    </n-tag>
                  </div>
                  <div class="novel-meta">
                    <span>{{ novel.chapter_count }} 章</span>
                    <span>{{ formatWordCount(novel.word_count || 0) }} 字</span>
                  </div>
                </div>
                <span class="open-indicator"><n-icon :component="IconArrow" :size="16" /></span>
              </div>
              <div class="novel-progress">
                <n-progress
                  type="line"
                  :percentage="novel.progress || 0"
                  :show-indicator="false"
                  :height="5"
                  :color="getProgressColor(novel.stage)"
                />
                <span class="progress-text numeric">{{ novel.progress || 0 }}%</span>
              </div>
            </button>
          </div>
        </article>

        <aside class="surface-panel trend-panel">
          <header class="panel-header">
            <div>
              <span class="panel-kicker">Market radar</span>
              <h2 class="panel-title">创作市场雷达</h2>
            </div>
            <n-button text type="primary" size="small" @click="goTrends()">完整趋势</n-button>
          </header>
          <p class="panel-caption">只保留与当前创作决策有关的摘要，完整分析进入趋势大盘。</p>

          <div v-if="radarLoading" class="radar-loading"><n-spin size="small" /></div>
          <div v-else class="radar-body">
            <button
              type="button"
              class="radar-primary"
              :disabled="!latestNovelGenre"
              @click="goTrends(latestNovelGenre)"
            >
              <span class="radar-label">CURRENT PROJECT</span>
              <span class="radar-heading">
                <strong>{{ latestNovelGenre || '尚未锁定题材' }}</strong>
                <n-icon :component="IconArrow" :size="15" />
              </span>
              <span v-if="currentGenreSignal" class="radar-summary">
                热度 {{ formatHeatScore(currentGenreSignal.score) }} · {{ getTrendLabel(currentGenreSignal.trend) }}
              </span>
              <span v-else class="radar-summary">
                {{ latestNovelGenre ? '当前样本中暂无匹配信号' : '建档后可关联作品题材趋势' }}
              </span>
            </button>

            <div class="radar-secondary">
              <button
                type="button"
                class="radar-signal"
                :disabled="!topMarketSignal"
                @click="goTrends(topMarketSignal?.genre || '')"
              >
                <span class="radar-label">STRONGEST SIGNAL</span>
                <strong>{{ topMarketSignal?.genre || '等待市场数据' }}</strong>
                <small v-if="topMarketSignal">
                  {{ formatHeatScore(topMarketSignal.score) }} 热度 · {{ getTrendLabel(topMarketSignal.trend) }}
                </small>
              </button>
              <div class="radar-signal data-state">
                <span class="radar-label">DATA STATUS</span>
                <strong>{{ marketSignals.length }} 个有效信号</strong>
                <small>{{ marketUpdatedAt || '尚未完成更新' }}</small>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section class="secondary-grid">
        <nav class="surface-panel quick-panel" aria-label="快捷入口">
          <header class="panel-header compact">
            <div>
              <span class="panel-kicker">Shortcuts</span>
              <h2 class="panel-title">快速开始</h2>
            </div>
          </header>
          <div class="quick-grid">
            <button type="button" class="quick-item" @click="goTrends()">
              <span class="quick-icon"><n-icon :component="IconChart" :size="19" /></span>
              <span><strong>市场信号</strong><small>查看题材变化</small></span>
              <n-icon class="quick-arrow" :component="IconArrow" />
            </button>
            <button type="button" class="quick-item" @click="goResearch">
              <span class="quick-icon"><n-icon :component="IconSearch" :size="19" /></span>
              <span><strong>题材研究</strong><small>验证创作方向</small></span>
              <n-icon class="quick-arrow" :component="IconArrow" />
            </button>
            <button type="button" class="quick-item" @click="goDeconstruction">
              <span class="quick-icon"><n-icon :component="IconLayers" :size="19" /></span>
              <span><strong>作品拆解</strong><small>提炼叙事结构</small></span>
              <n-icon class="quick-arrow" :component="IconArrow" />
            </button>
            <button type="button" class="quick-item accent" @click="goCreateNovel">
              <span class="quick-icon"><n-icon :component="IconAdd" :size="19" /></span>
              <span><strong>新建作品</strong><small>创建叙事工程</small></span>
              <n-icon class="quick-arrow" :component="IconArrow" />
            </button>
          </div>
        </nav>

        <article class="surface-panel guidance-panel">
          <div class="guidance-mark" aria-hidden="true">AI</div>
          <div class="guidance-copy">
            <span class="panel-kicker">Narrative guidance</span>
            <h2>{{ guidanceTitle }}</h2>
            <p>{{ guidanceDescription }}</p>
            <div class="guidance-tags" aria-label="叙事检查项">
              <span>角色状态</span>
              <span>因果链</span>
              <span>伏笔台账</span>
            </div>
          </div>
          <n-button class="guidance-action" secondary type="primary" @click="goHeroAction">
            {{ hasNovels ? '进入工作台' : '开始规划' }}
            <template #icon><n-icon :component="IconArrow" /></template>
          </n-button>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import { novelApi, type NovelDTO } from '../api/novel'
import { marketApi, type GenreRecommendation } from '@/api/market'
import { getNovelStageLabel, getNovelStageTagType } from '@/domain/novel'
import { parseGenreWorldFromPremise } from '@/utils/premisePresets'
import { BRAND } from '@/constants/brand'

const router = useRouter()

const svgIcon = (paths: string[]) => () =>
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
  }, paths.map(d => h('path', { d })))

const IconBook = svgIcon(['M3.5 5.5A3.5 3.5 0 017 4h4v16H7a3.5 3.5 0 00-3.5 1.5z', 'M20.5 5.5A3.5 3.5 0 0017 4h-4v16h4a3.5 3.5 0 013.5 1.5z'])
const IconPen = svgIcon(['M4 20l4.2-1 10.6-10.6a2 2 0 00-2.8-2.8L5.4 16.2z', 'M14.5 7.1l2.8 2.8'])
const IconChapters = svgIcon(['M6 4h12v16H6z', 'M9 8h6', 'M9 12h6', 'M9 16h4'])
const IconPulse = svgIcon(['M3 12h4l2-5 4 10 2-5h6'])
const IconAdd = svgIcon(['M12 5v14', 'M5 12h14'])
const IconArrow = svgIcon(['M5 12h14', 'M14 7l5 5-5 5'])
const IconChart = svgIcon(['M5 19V9', 'M12 19V5', 'M19 19v-7'])
const IconSearch = svgIcon(['M10.5 18a7.5 7.5 0 100-15 7.5 7.5 0 000 15z', 'M16 16l5 5'])
const IconLayers = svgIcon(['M12 3l9 5-9 5-9-5z', 'M3 12l9 5 9-5', 'M3 16l9 5 9-5'])

const todayStr = computed(() => {
  const d = new Date()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getMonth() + 1}月${d.getDate()}日 · ${weekdays[d.getDay()]}`
})

const loading = ref(false)
const novels = ref<any[]>([])
const radarLoading = ref(false)
const marketSignals = ref<GenreRecommendation[]>([])
const marketUpdatedAt = ref('')

const stats = computed(() => ({
  totalNovels: novels.value.length,
  totalChapters: novels.value.reduce((sum, n) => sum + (n.chapter_count || 0), 0),
  totalWords: novels.value.reduce((sum, n) => sum + (n.word_count || 0), 0),
  lockedGenres: novels.value.filter(n => Boolean(n.genre)).length,
}))

const displayNovels = computed(() => novels.value.slice(0, 4).map(n => ({
  ...n,
  progress: n.target_chapters
    ? Math.min(100, Math.round(((n.chapter_count || 0) / n.target_chapters) * 100))
    : Math.min(100, n.chapter_count || 0),
})))

const hasNovels = computed(() => novels.value.length > 0)
const latestNovelTitle = computed(() => novels.value[0]?.title || '尚未建立作品')
const latestNovelSlug = computed(() => novels.value[0]?.slug || '')
const latestNovelGenre = computed(() => novels.value[0]?.genre || '')
const currentGenreSignal = computed(() => {
  const root = normalizeGenre(latestNovelGenre.value)
  if (!root) return null
  return marketSignals.value.find(item => {
    const signalGenre = normalizeGenre(item.genre)
    return signalGenre === root || signalGenre.includes(root) || root.includes(signalGenre)
  }) || null
})
const topMarketSignal = computed(() => {
  return [...marketSignals.value].sort((a, b) => {
    const trendWeight = (value: string) => value === 'up' ? 2 : value === 'stable' ? 1 : 0
    return trendWeight(b.trend) - trendWeight(a.trend) || b.score - a.score
  })[0] || null
})
const guidanceTitle = computed(() => hasNovels.value
  ? `为《${latestNovelTitle.value}》准备下一章`
  : '先建立故事核心，再让系统接住复杂度')
const guidanceDescription = computed(() => hasNovels.value
  ? '动笔前快速核对本章会改变什么：谁获得了新信息、哪条因果继续推进、哪些伏笔需要保持可见。'
  : `不必一次填满所有设定。先确定主角、核心欲望与主要阻力，${BRAND.chineseName}会沿着创作过程逐步组织叙事状态。`)

async function fetchNovels() {
  loading.value = true
  try {
    const data = await novelApi.listNovels()
    novels.value = data.map((novel: NovelDTO) => {
      const fromPrefix = parseGenreWorldFromPremise(novel.premise || '').genre
      const genre = novel.locked_genre?.trim() || fromPrefix || ''
      return {
        slug: novel.id,
        title: novel.title,
        stage: novel.stage,
        stage_label: getNovelStageLabel(novel.stage),
        genre,
        chapter_count: novel.chapters?.length || 0,
        word_count: novel.total_word_count,
        target_chapters: novel.target_chapters || 100,
      }
    })
  } catch {
    novels.value = []
  } finally {
    loading.value = false
  }
}

async function fetchMarketSignals() {
  radarLoading.value = true
  try {
    marketSignals.value = await marketApi.getGenreRecommendations(8)
    marketUpdatedAt.value = `更新于 ${new Intl.DateTimeFormat('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(new Date())}`
  } catch (error) {
    console.error('Failed to load market radar:', error)
    marketSignals.value = []
    marketUpdatedAt.value = ''
  } finally {
    radarLoading.value = false
  }
}

function normalizeGenre(value: string): string {
  return value.trim().split(/[\/·]/)[0]?.trim() || ''
}

function formatWordCount(count: number): string {
  if (count >= 10000) return `${(count / 10000).toFixed(1)}万`
  return `${count}`
}

function formatHeatScore(score: number): number {
  const normalized = score <= 1 ? score * 100 : score
  return Math.max(0, Math.min(100, Math.round(normalized)))
}

function getTrendLabel(trend: string): string {
  if (trend === 'up') return '正在上升'
  if (trend === 'down') return '正在回落'
  return '保持稳定'
}

const getStageType = (stage: string) => getNovelStageTagType(stage)
const getProgressColor = (stage: string) => ({
  planning: '#5b6ee1',
  writing: '#c58a2b',
  reviewing: '#7c63c7',
  completed: '#2f936f',
}[stage] || '#5b6ee1')

function goHeroAction() {
  if (latestNovelSlug.value) goNovel(latestNovelSlug.value)
  else goCreateNovel()
}

function goCreateNovel() { router.push('/home') }
function goLibrary() { router.push('/library') }
function goTrends(genre = '') {
  router.push({
    path: '/market/trends',
    query: genre ? { genre, from: 'dashboard' } : { from: 'dashboard' },
  })
}
function goResearch() { router.push('/market/research') }
function goDeconstruction() { router.push('/market/deconstruction') }
function goNovel(slug: string) { router.push(`/book/${slug}/workbench`) }

onMounted(() => {
  void Promise.all([fetchNovels(), fetchMarketSignals()])
})
</script>

<style scoped>
.dashboard {
  position: relative;
  min-height: 100%;
  padding: clamp(22px, 3vw, 38px);
  background: var(--app-page-bg);
  overflow: hidden;
}

.dashboard-bg {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(rgba(105, 117, 148, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(105, 117, 148, 0.035) 1px, transparent 1px),
    radial-gradient(circle at 8% 0%, var(--color-brand-light), transparent 28%),
    radial-gradient(circle at 96% 22%, var(--color-gold-dim), transparent 25%);
  background-size: 32px 32px, 32px 32px, auto, auto;
  mask-image: linear-gradient(to bottom, black, transparent 82%);
  pointer-events: none;
}

.dashboard-inner {
  position: relative;
  max-width: 1440px;
  margin: 0 auto;
}

.command-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.75fr);
  min-height: 280px;
  overflow: hidden;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 22px;
  box-shadow: var(--app-shadow-md);
}

.hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: clamp(32px, 4vw, 56px);
}

.hero-eyebrow,
.panel-kicker {
  color: var(--color-brand);
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.hero-eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.hero-eyebrow > span:last-child {
  color: var(--app-text-muted);
  font-size: 9px;
}

.eyebrow-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-brand);
  box-shadow: 0 0 0 4px var(--color-brand-light);
}

.hero-title {
  margin: 0;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: clamp(34px, 4vw, 50px);
  font-weight: 680;
  line-height: 1.18;
  letter-spacing: -0.045em;
}

.hero-title span {
  color: var(--app-text-secondary);
}

.hero-description {
  max-width: 660px;
  margin: 20px 0 0;
  color: var(--app-text-secondary);
  font-size: 14px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 28px;
}

.hero-primary,
.hero-secondary {
  min-height: 42px;
  padding-inline: 18px;
}

.hero-status {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 28px;
  color: #f4f6fb;
  background:
    radial-gradient(circle at 85% 10%, color-mix(in srgb, var(--color-brand) 38%, transparent), transparent 38%),
    linear-gradient(145deg, #20283c, #111827 72%);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}

.status-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: rgba(244, 246, 251, 0.6);
  font-size: 10px;
  font-weight: 650;
  letter-spacing: 0.05em;
}

.system-ready {
  display: flex;
  align-items: center;
  gap: 6px;
}

.system-ready i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #63d19e;
  box-shadow: 0 0 0 4px rgba(99, 209, 158, 0.12);
}

.status-focus {
  margin: auto 0;
  padding: 30px 0;
}

.status-label {
  display: block;
  margin-bottom: 10px;
  color: rgba(244, 246, 251, 0.52);
  font-size: 10px;
  letter-spacing: 0.12em;
}

.status-focus strong {
  display: block;
  overflow: hidden;
  color: #fff;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-focus p {
  margin: 10px 0 0;
  color: rgba(244, 246, 251, 0.68);
  font-size: 12px;
  line-height: 1.65;
}

.status-flow {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(244, 246, 251, 0.58);
  font-size: 9px;
  white-space: nowrap;
}

.status-flow i {
  width: 16px;
  height: 1px;
  background: rgba(244, 246, 251, 0.22);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 14px 0;
}

.metric-card {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 92px;
  padding: 18px 18px 18px 20px;
  overflow: hidden;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 15px;
}

.metric-card::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 3px;
  background: var(--color-brand);
  content: '';
  opacity: 0.72;
}

.metric-icon {
  display: grid;
  flex: 0 0 auto;
  width: 38px;
  height: 38px;
  place-items: center;
  margin-right: 13px;
  color: var(--color-brand);
  background: var(--color-brand-light);
  border-radius: 10px;
}

.metric-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.metric-label {
  color: var(--app-text-muted);
  font-size: 11px;
}

.metric-value {
  margin-top: 3px;
  color: var(--app-text-primary);
  font-size: 25px;
  line-height: 1;
}

.metric-note {
  align-self: flex-end;
  margin-left: auto;
  color: var(--app-text-muted);
  font-size: 10px;
}

.primary-grid,
.secondary-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(310px, 0.72fr);
  gap: 14px;
  margin-top: 14px;
}

.secondary-grid {
  grid-template-columns: minmax(0, 1.08fr) minmax(0, 1fr);
  margin-bottom: 24px;
}

.surface-panel {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 18px;
  box-shadow: var(--app-shadow-sm);
}

.progress-panel,
.trend-panel,
.quick-panel {
  padding: 24px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 20px;
}

.panel-header.compact {
  margin-bottom: 16px;
}

.panel-title {
  margin: 4px 0 0;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 650;
}

.panel-caption {
  margin: -12px 0 12px;
  color: var(--app-text-muted);
  font-size: 11px;
}

.loading-state {
  display: grid;
  min-height: 176px;
  place-items: center;
}

.empty-state {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  min-height: 168px;
  padding: 26px;
  background: var(--app-surface-subtle);
  border: 1px dashed var(--app-border-strong);
  border-radius: 14px;
  gap: 18px;
}

.empty-mark {
  display: grid;
  width: 58px;
  height: 58px;
  place-items: center;
  color: var(--color-brand);
  background: var(--color-brand-light);
  border-radius: 16px;
}

.empty-copy strong {
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 16px;
}

.empty-copy p {
  max-width: 570px;
  margin: 7px 0 0;
  color: var(--app-text-muted);
  font-size: 12px;
  line-height: 1.65;
}

.novel-progress-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.novel-progress-item {
  width: 100%;
  padding: 14px 16px;
  color: inherit;
  text-align: left;
  background: var(--app-surface-subtle);
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
}

.novel-progress-item:hover,
.novel-progress-item:focus-visible {
  background: var(--color-brand-light);
  border-color: var(--color-brand-border);
  outline: none;
  transform: translateX(2px);
}

.novel-heading {
  display: flex;
  align-items: center;
  gap: 14px;
}

.novel-index {
  color: var(--app-text-muted);
  font-size: 10px;
}

.novel-info {
  min-width: 0;
  flex: 1;
}

.novel-title-row,
.novel-meta,
.novel-progress {
  display: flex;
  align-items: center;
}

.novel-title-row {
  gap: 8px;
}

.novel-title {
  overflow: hidden;
  color: var(--app-text-primary);
  font-size: 14px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.novel-meta {
  gap: 12px;
  margin-top: 4px;
  color: var(--app-text-muted);
  font-size: 10px;
}

.open-indicator {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  color: var(--app-text-muted);
}

.novel-progress {
  gap: 10px;
  margin: 11px 0 0 30px;
}

.novel-progress :deep(.n-progress) {
  flex: 1;
}

.progress-text {
  min-width: 34px;
  color: var(--app-text-muted);
  font-size: 10px;
  text-align: right;
}

.radar-loading {
  display: grid;
  min-height: 180px;
  place-items: center;
}

.radar-body {
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.radar-primary,
.radar-signal {
  width: 100%;
  color: inherit;
  text-align: left;
  border: 1px solid var(--app-border);
  cursor: pointer;
}

.radar-primary {
  display: flex;
  min-height: 104px;
  flex-direction: column;
  justify-content: center;
  padding: 17px;
  border-radius: 13px;
  background:
    linear-gradient(135deg, var(--color-brand-light), transparent 70%),
    var(--app-surface-subtle);
  transition: border-color 0.18s ease, transform 0.18s ease;
}

.radar-primary:hover:not(:disabled),
.radar-primary:focus-visible:not(:disabled) {
  border-color: var(--color-brand-border);
  outline: none;
  transform: translateY(-1px);
}

.radar-primary:disabled,
.radar-signal:disabled {
  cursor: default;
}

.radar-label {
  color: var(--app-text-muted);
  font-family: var(--font-mono);
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.radar-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  color: var(--app-text-primary);
}

.radar-heading strong {
  overflow: hidden;
  font-family: var(--font-serif);
  font-size: 17px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.radar-summary {
  margin-top: 4px;
  color: var(--app-text-muted);
  font-size: 10px;
}

.radar-secondary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.radar-signal {
  display: flex;
  min-width: 0;
  min-height: 82px;
  flex-direction: column;
  justify-content: center;
  padding: 13px;
  border-radius: 11px;
  background: var(--app-surface-subtle);
}

button.radar-signal:hover:not(:disabled),
button.radar-signal:focus-visible:not(:disabled) {
  border-color: var(--color-brand-border);
  outline: none;
}

.radar-signal strong {
  overflow: hidden;
  margin-top: 6px;
  color: var(--app-text-primary);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.radar-signal small {
  margin-top: 3px;
  color: var(--app-text-muted);
  font-size: 9px;
}

.radar-signal.data-state {
  cursor: default;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.quick-item {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-width: 0;
  padding: 12px;
  color: inherit;
  text-align: left;
  background: var(--app-surface-subtle);
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: border-color 0.18s ease, background 0.18s ease;
}

.quick-item:hover,
.quick-item:focus-visible {
  background: var(--color-brand-light);
  border-color: var(--color-brand-border);
  outline: none;
}

.quick-item.accent {
  border-color: var(--color-brand-border);
}

.quick-icon {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  color: var(--color-brand);
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 10px;
}

.quick-item > span:nth-child(2) {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.quick-item strong {
  color: var(--app-text-primary);
  font-size: 12px;
  font-weight: 650;
}

.quick-item small {
  margin-top: 2px;
  overflow: hidden;
  color: var(--app-text-muted);
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quick-arrow {
  color: var(--app-text-muted);
}

.guidance-panel {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 24px;
  overflow: hidden;
}

.guidance-panel::after {
  position: absolute;
  top: -80px;
  right: -60px;
  width: 180px;
  height: 180px;
  background: var(--color-brand-light);
  border-radius: 50%;
  content: '';
  pointer-events: none;
}

.guidance-mark {
  display: grid;
  z-index: 1;
  width: 46px;
  height: 46px;
  place-items: center;
  color: var(--color-brand);
  background: var(--color-brand-light);
  border: 1px solid var(--color-brand-border);
  border-radius: 14px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.guidance-copy {
  z-index: 1;
  min-width: 0;
}

.guidance-copy h2 {
  margin: 4px 0 7px;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 650;
}

.guidance-copy p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 11px;
  line-height: 1.65;
}

.guidance-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.guidance-tags span {
  padding: 3px 7px;
  color: var(--app-text-secondary);
  background: var(--app-surface-subtle);
  border: 1px solid var(--app-border);
  border-radius: 999px;
  font-size: 9px;
}

.guidance-action {
  z-index: 1;
}

@media (max-width: 1080px) {
  .command-hero {
    grid-template-columns: minmax(0, 1.3fr) minmax(290px, 0.8fr);
  }

  .hero-copy {
    padding: 36px;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .secondary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .dashboard {
    padding: 18px;
  }

  .command-hero,
  .primary-grid {
    grid-template-columns: 1fr;
  }

  .hero-status {
    min-height: 230px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 0;
  }

  .empty-state {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .empty-state > :last-child {
    grid-column: 2;
    justify-self: start;
  }
}

@media (max-width: 560px) {
  .dashboard {
    padding: 12px;
  }

  .command-hero,
  .surface-panel,
  .metric-card {
    border-radius: 14px;
  }

  .hero-copy,
  .hero-status,
  .progress-panel,
  .trend-panel,
  .quick-panel,
  .guidance-panel {
    padding: 20px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-eyebrow > span:last-child {
    display: none;
  }

  .hero-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .metrics-grid,
  .quick-grid {
    grid-template-columns: 1fr;
  }

  .empty-state {
    grid-template-columns: 1fr;
    justify-items: start;
    padding: 20px;
  }

  .empty-state > :last-child {
    grid-column: 1;
  }

  .panel-header {
    align-items: flex-start;
  }

  .guidance-panel {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .guidance-action {
    grid-column: 2;
    justify-self: start;
  }
}
</style>
