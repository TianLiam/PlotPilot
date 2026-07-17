<template>
  <div class="dashboard">
    <div class="dashboard-bg" aria-hidden="true" />

    <div class="dashboard-inner">
      <section class="welcome-section">
        <div class="welcome-left">
          <h1 class="welcome-title">
            你好，创作者 👋
          </h1>
          <p class="welcome-subtitle">
            今天是 {{ todayStr }}，来看看市场趋势和你的创作进度吧
          </p>
        </div>
        <div class="welcome-right">
          <n-button type="primary" size="large" round @click="goCreateNovel">
            <template #icon>
              <n-icon :component="IconSpark" :size="18" />
            </template>
            新建小说
          </n-button>
        </div>
      </section>

      <section class="stats-section">
        <n-grid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
          <n-gi>
            <div class="stat-card stat-total">
              <div class="stat-icon">📚</div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalNovels }}</div>
                <div class="stat-label">在写小说</div>
              </div>
            </div>
          </n-gi>
          <n-gi>
            <div class="stat-card stat-words">
              <div class="stat-icon">✍️</div>
              <div class="stat-info">
                <div class="stat-value">{{ formatWordCount(stats.totalWords) }}</div>
                <div class="stat-label">总字数</div>
              </div>
            </div>
          </n-gi>
          <n-gi>
            <div class="stat-card stat-chapters">
              <div class="stat-icon">📄</div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalChapters }}</div>
                <div class="stat-label">章节数</div>
              </div>
            </div>
          </n-gi>
          <n-gi>
            <div class="stat-card stat-trend">
              <div class="stat-icon">🔥</div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.hotTopics }}</div>
                <div class="stat-label">今日热门题材</div>
              </div>
            </div>
          </n-gi>
        </n-grid>
      </section>

      <n-grid :cols="3" :x-gap="20" :y-gap="20" responsive="screen" class="content-grid">
        <n-gi :span="2">
          <n-card class="panel-card" :bordered="false">
            <template #header>
              <div class="panel-header">
                <span class="panel-title">创作进度</span>
                <n-button text type="primary" size="small" @click="goLibrary">
                  查看全部
                </n-button>
              </div>
            </template>

            <div v-if="loading" class="loading-state">
              <n-spin size="medium" />
            </div>

            <div v-else-if="novels.length === 0" class="empty-state">
              <span class="empty-icon">📖</span>
              <p>还没有小说，开始你的第一部作品吧</p>
              <n-button type="primary" size="small" round @click="goCreateNovel">
                立即创建
              </n-button>
            </div>

            <div v-else class="novel-progress-list">
              <div
                v-for="novel in displayNovels"
                :key="novel.slug"
                class="novel-progress-item"
                @click="goNovel(novel.slug)"
              >
                <div class="novel-info">
                  <div class="novel-title-row">
                    <span class="novel-dot" :class="`dot-${novel.stage}`"></span>
                    <span class="novel-title">{{ novel.title }}</span>
                    <n-tag :type="getStageType(novel.stage)" size="small" round borderable>
                      {{ novel.stage_label }}
                    </n-tag>
                  </div>
                  <div class="novel-meta">
                    <span>{{ novel.chapter_count }} 章</span>
                    <span>·</span>
                    <span>{{ formatWordCount(novel.word_count || 0) }}</span>
                  </div>
                </div>
                <div class="novel-progress">
                  <n-progress
                    type="line"
                    :percentage="novel.progress || 0"
                    :show-indicator="false"
                    :height="6"
                    :color="getProgressColor(novel.stage)"
                  />
                  <span class="progress-text">{{ novel.progress || 0 }}%</span>
                </div>
              </div>
            </div>
          </n-card>
        </n-gi>

        <n-gi :span="1">
          <n-card class="panel-card" :bordered="false">
            <template #header>
              <div class="panel-header">
                <span class="panel-title">🔥 今日趋势</span>
                <n-button text type="primary" size="small" @click="goMarket">
                  去市场
                </n-button>
              </div>
            </template>

            <div class="trend-list">
              <div
                v-for="(item, idx) in hotTrends"
                :key="idx"
                class="trend-item"
              >
                <div class="trend-rank" :class="`rank-${idx + 1}`">{{ idx + 1 }}</div>
                <div class="trend-info">
                  <div class="trend-name">{{ item.name }}</div>
                  <div class="trend-meta">
                    <span class="trend-platform">{{ item.platform }}</span>
                  </div>
                </div>
                <div class="trend-value" :class="item.direction">
                  <span v-if="item.direction === 'up'">↑</span>
                  <span v-else-if="item.direction === 'down'">↓</span>
                  <span v-else>—</span>
                  {{ item.change }}
                </div>
              </div>
            </div>
          </n-card>
        </n-gi>

        <n-gi :span="1">
          <n-card class="panel-card quick-card" :bordered="false">
            <template #header>
              <div class="panel-header">
                <span class="panel-title">⚡ 快捷入口</span>
              </div>
            </template>

            <div class="quick-grid">
              <div class="quick-item" @click="goMarket">
                <div class="quick-icon quick-icon-market">📊</div>
                <span class="quick-label">市场分析</span>
              </div>
              <div class="quick-item" @click="goResearch">
                <div class="quick-icon quick-icon-research">🔬</div>
                <span class="quick-label">题材研究</span>
              </div>
              <div class="quick-item" @click="goDeconstruction">
                <div class="quick-icon quick-icon-deconstruct">🧬</div>
                <span class="quick-label">爆款拆书</span>
              </div>
              <div class="quick-item" @click="goCreateNovel">
                <div class="quick-icon quick-icon-create">✨</div>
                <span class="quick-label">新建小说</span>
              </div>
            </div>
          </n-card>
        </n-gi>

        <n-gi :span="2">
          <n-card class="panel-card" :bordered="false">
            <template #header>
              <div class="panel-header">
                <span class="panel-title">💡 AI 推荐</span>
              </div>
            </template>

            <div class="ai-suggestions">
              <div class="suggestion-item">
                <div class="suggestion-badge">热门题材</div>
                <div class="suggestion-title">都市+签到流 持续走热</div>
                <p class="suggestion-desc">
                  近 7 天都市签到类小说登上番茄榜首 12 次，读者留存率比平均高 23%。
                  建议结合「系统流+打脸」节奏，开局 3 章内触发第一次金手指。
                </p>
                <n-button text type="primary" size="small" @click="goResearch">
                  查看详细研究 →
                </n-button>
              </div>

              <div class="suggestion-item">
                <div class="suggestion-badge suggestion-badge-warn">写作建议</div>
                <div class="suggestion-title">你的《{{ latestNovelTitle }}》第 15 章节奏偏慢</div>
                <p class="suggestion-desc">
                  与同类爆款对比，本章冲突密度偏低 35%，建议在下一章加入反转或铺垫。
                  可使用「节奏规划」功能调整节拍分布。
                </p>
                <n-button text type="primary" size="small" v-if="latestNovelSlug" @click="goNovel(latestNovelSlug)">
                  前往调整 →
                </n-button>
              </div>
            </div>
          </n-card>
        </n-gi>
      </n-grid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon, useMessage } from 'naive-ui'
import { novelApi, type NovelDTO } from '../api/novel'
import {
  getNovelStageLabel,
  getNovelStageTagType,
} from '@/domain/novel'
import { parseGenreWorldFromPremise } from '@/utils/premisePresets'

const router = useRouter()
const message = useMessage()

const IconSpark = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M13 2L3 14h8l-1 8 10-12h-8l1-8z' }))

const todayStr = computed(() => {
  const d = new Date()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getMonth() + 1}月${d.getDate()}日 ${weekdays[d.getDay()]}`
})

const loading = ref(false)
const novels = ref<any[]>([])

const stats = computed(() => ({
  totalNovels: novels.value.length,
  totalChapters: novels.value.reduce((sum, n) => sum + (n.chapter_count || 0), 0),
  totalWords: novels.value.reduce((sum, n) => sum + (n.word_count || 0), 0),
  hotTopics: 12,
}))

const hotTrends = ref([
  { name: '都市签到流', platform: '番茄', change: '+28%', direction: 'up' },
  { name: '玄幻无敌流', platform: '起点', change: '+15%', direction: 'up' },
  { name: '重生年代文', platform: '七猫', change: '+12%', direction: 'up' },
  { name: '系统赘婿', platform: '番茄', change: '+8%', direction: 'up' },
  { name: '末世求生', platform: '起点', change: '-3%', direction: 'down' },
])

const displayNovels = computed(() => {
  return novels.value.slice(0, 4).map(n => ({
    ...n,
    progress: n.target_chapters
      ? Math.round(((n.chapter_count || 0) / n.target_chapters) * 100)
      : Math.round((n.chapter_count || 0) / 100 * 100),
  }))
})

const latestNovelTitle = computed(() => {
  return novels.value[0]?.title || '你的小说'
})

const latestNovelSlug = computed(() => {
  return novels.value[0]?.slug || ''
})

const fetchNovels = async () => {
  loading.value = true
  try {
    const data = await novelApi.listNovels()
    novels.value = data.map((novel: NovelDTO) => {
      const fromPrefix = parseGenreWorldFromPremise(novel.premise || '').genre
      const g = novel.locked_genre?.trim() || fromPrefix || ''
      return {
        slug: novel.id,
        title: novel.title,
        stage: novel.stage,
        stage_label: getNovelStageLabel(novel.stage),
        genre: g,
        chapter_count: novel.chapters?.length || 0,
        word_count: novel.total_word_count,
        target_chapters: novel.target_chapters || 100,
      }
    })
  } catch {
    // 静默失败
  } finally {
    loading.value = false
  }
}

const formatWordCount = (count: number): string => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count + ''
}

const getStageType = (stage: string) => getNovelStageTagType(stage)

const getProgressColor = (stage: string) => {
  const map: Record<string, string> = {
    planning: '#3b82f6',
    writing: '#f59e0b',
    reviewing: '#8b5cf6',
    completed: '#10b981',
  }
  return map[stage] || '#3b82f6'
}

const goCreateNovel = () => {
  router.push('/home')
}

const goLibrary = () => {
  router.push('/library')
}

const goMarket = () => {
  router.push('/market')
}

const goResearch = () => {
  router.push('/market/research')
}

const goDeconstruction = () => {
  router.push('/market/deconstruction')
}

const goNovel = (slug: string) => {
  router.push(`/book/${slug}/workbench`)
}

onMounted(() => {
  fetchNovels()
})
</script>

<style scoped>
.dashboard {
  position: relative;
  min-height: 100%;
  padding: 24px;
}

.dashboard-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, var(--color-brand-light), transparent 60%),
    radial-gradient(ellipse 40% 40% at 100% 0%, rgba(245, 158, 11, 0.08), transparent 50%);
  pointer-events: none;
}

.dashboard-inner {
  position: relative;
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.welcome-title {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 700;
  color: var(--app-text-primary);
  letter-spacing: -0.02em;
}

.welcome-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: var(--app-surface);
  border-radius: 14px;
  border: 1px solid var(--app-border);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  border-radius: 12px;
  background: var(--app-surface-subtle);
  flex-shrink: 0;
}

.stat-total .stat-icon { background: rgba(59, 130, 246, 0.1); }
.stat-words .stat-icon { background: rgba(16, 185, 129, 0.1); }
.stat-chapters .stat-icon { background: rgba(139, 92, 246, 0.1); }
.stat-trend .stat-icon { background: rgba(245, 158, 11, 0.1); }

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--app-text-primary);
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 13px;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.content-grid {
  margin-top: 4px;
}

.panel-card {
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--app-text-muted);
  gap: 12px;
}

.empty-icon {
  font-size: 36px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.novel-progress-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.novel-progress-item {
  padding: 14px 16px;
  border-radius: 10px;
  background: var(--app-surface-subtle);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.novel-progress-item:hover {
  background: var(--color-brand-light);
  border-color: var(--color-brand-border);
}

.novel-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.novel-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.novel-dot.dot-planning { background: #3b82f6; }
.novel-dot.dot-writing { background: #f59e0b; }
.novel-dot.dot-reviewing { background: #8b5cf6; }
.novel-dot.dot-completed { background: #10b981; }

.novel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.novel-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--app-text-muted);
}

.novel-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.novel-progress :deep(.n-progress) {
  flex: 1;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text-secondary);
  min-width: 36px;
  text-align: right;
}

.trend-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.trend-item:hover {
  background: var(--app-surface-subtle);
}

.trend-rank {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  border-radius: 6px;
  background: var(--app-surface-subtle);
  color: var(--app-text-muted);
  flex-shrink: 0;
}

.trend-rank.rank-1 { background: linear-gradient(135deg, #ef4444, #f97316); color: #fff; }
.trend-rank.rank-2 { background: linear-gradient(135deg, #f97316, #f59e0b); color: #fff; }
.trend-rank.rank-3 { background: linear-gradient(135deg, #f59e0b, #eab308); color: #fff; }

.trend-info {
  flex: 1;
  min-width: 0;
}

.trend-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--app-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.trend-meta {
  font-size: 11px;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.trend-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text-secondary);
}

.trend-value.up { color: #10b981; }
.trend-value.down { color: #ef4444; }

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.quick-item:hover {
  background: var(--app-surface-subtle);
  border-color: var(--app-border);
}

.quick-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  border-radius: 12px;
}

.quick-icon-market { background: rgba(59, 130, 246, 0.1); }
.quick-icon-research { background: rgba(139, 92, 246, 0.1); }
.quick-icon-deconstruct { background: rgba(16, 185, 129, 0.1); }
.quick-icon-create { background: rgba(245, 158, 11, 0.1); }

.quick-label {
  font-size: 12px;
  color: var(--app-text-secondary);
  font-weight: 500;
}

.ai-suggestions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  padding: 16px;
  border-radius: 10px;
  background: var(--app-surface-subtle);
  border-left: 3px solid var(--color-brand);
}

.suggestion-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  margin-bottom: 8px;
}

.suggestion-badge-warn {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.suggestion-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin-bottom: 6px;
}

.suggestion-desc {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--app-text-secondary);
  line-height: 1.6;
}

@media (max-width: 900px) {
  .dashboard {
    padding: 16px;
  }

  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .stats-section :deep(.n-grid) {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-value {
    font-size: 22px;
  }
}
</style>
