<template>
  <div class="library-page">
    <div class="page-header">
      <div class="page-heading">
        <span class="page-eyebrow">Project library</span>
        <h1 class="page-title">作品库</h1>
        <p class="page-subtitle">管理长篇项目、查看创作阶段，并快速回到最近的写作现场。</p>
      </div>
      <div v-if="books.length > 0" class="header-actions">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索书名或类型…"
          clearable
          round
          class="search-input"
        >
          <template #prefix>
            <n-icon><IconSearch /></n-icon>
          </template>
        </n-input>
        <n-button type="primary" size="large" round @click="goCreate">
          <template #icon>
            <n-icon><IconPlus /></n-icon>
          </template>
          新建小说
        </n-button>
      </div>
    </div>

    <div v-if="books.length > 0" class="filter-bar">
      <n-radio-group v-model:value="filterStage" size="medium">
        <n-radio-button value="all">全部</n-radio-button>
        <n-radio-button value="planning">策划中</n-radio-button>
        <n-radio-button value="writing">写作中</n-radio-button>
        <n-radio-button value="reviewing">审阅中</n-radio-button>
        <n-radio-button value="completed">已完成</n-radio-button>
      </n-radio-group>

      <div class="filter-right">
        <n-select
          v-model:value="sortBy"
          :options="sortOptions"
          size="medium"
          style="width: 140px"
        />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
      <p>加载中…</p>
    </div>

    <div v-else-if="books.length === 0" class="empty-state empty-library">
      <div class="empty-copy">
        <span class="empty-kicker">Your first narrative project</span>
        <h2 class="empty-title">作品库还没有内容，<br>先建立第一部叙事工程。</h2>
        <p class="empty-desc">只需要一个故事核心和题材方向。角色、世界观、结构与章节计划可以在后续流程中逐步完善。</p>
        <n-button type="primary" size="large" @click="goCreate">
          <template #icon>
            <n-icon><IconPlus /></n-icon>
          </template>
          新建第一部作品
        </n-button>
      </div>
      <div class="empty-roadmap" aria-label="作品建立流程">
        <div v-for="(step, index) in libraryOnboardingSteps" :key="step.title" class="empty-roadmap-item">
          <span>{{ String(index + 1).padStart(2, '0') }}</span>
          <div><strong>{{ step.title }}</strong><small>{{ step.desc }}</small></div>
        </div>
      </div>
    </div>

    <div v-else-if="filteredBooks.length === 0" class="empty-state">
      <n-icon :component="IconSearch" :size="34" />
      <p>没有找到匹配的小说</p>
      <n-button text type="primary" @click="clearFilter">清除筛选</n-button>
    </div>

    <div v-else class="books-grid">
      <div
        v-for="book in filteredBooks"
        :key="book.slug"
        class="book-card"
        role="button"
        tabindex="0"
        @click="openBook(book.slug)"
        @keydown.enter="openBook(book.slug)"
      >
        <div class="book-cover" :class="`cover-${book.stage}`">
          <span class="cover-text">{{ book.title.charAt(0) }}</span>
          <n-tag
            :type="getStageType(book.stage)"
            size="small"
            round
            borderable
            class="cover-tag"
          >
            {{ book.stage_label }}
          </n-tag>
        </div>

        <div class="book-info">
          <h3 class="book-title" :title="book.title">{{ book.title }}</h3>
          <p class="book-genre">{{ book.genre || '未分类' }}</p>

          <div class="book-stats">
            <div class="stat-item">
              <span class="stat-num">{{ book.chapter_count }}</span>
              <span class="stat-label">章节</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">{{ formatWordCount(book.word_count || 0) }}</span>
              <span class="stat-label">字数</span>
            </div>
          </div>

          <div class="book-progress">
            <n-progress
              type="line"
              :percentage="book.progress || 0"
              :show-indicator="false"
              :height="4"
              :color="getProgressColor(book.stage)"
            />
            <span class="progress-text">{{ book.progress || 0 }}%</span>
          </div>
        </div>

        <div class="book-actions" @click.stop>
          <n-button quaternary size="small" @click="openBook(book.slug)">
            继续创作
          </n-button>
        </div>
      </div>
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

const IconSearch = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z' }))

const IconPlus = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z' }))

const loading = ref(false)
const books = ref<any[]>([])
const searchQuery = ref('')
const filterStage = ref('all')
const sortBy = ref('updated')

const sortOptions = [
  { label: '最近更新', value: 'updated' },
  { label: '创建时间', value: 'created' },
  { label: '字数最多', value: 'words' },
  { label: '章节最多', value: 'chapters' },
]

const libraryOnboardingSteps = [
  { title: '故事核心', desc: '一句话梗概与题材方向' },
  { title: '叙事骨架', desc: '角色、世界观与结构规划' },
  { title: '持续创作', desc: '章节推进与一致性校验' },
]

const filteredBooks = computed(() => {
  let result = [...books.value]

  if (filterStage.value !== 'all') {
    result = result.filter(b => b.stage === filterStage.value)
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(b =>
      b.title.toLowerCase().includes(q) ||
      (b.genre && b.genre.toLowerCase().includes(q))
    )
  }

  switch (sortBy.value) {
    case 'words':
      result.sort((a, b) => (b.word_count || 0) - (a.word_count || 0))
      break
    case 'chapters':
      result.sort((a, b) => (b.chapter_count || 0) - (a.chapter_count || 0))
      break
    case 'created':
      result.reverse()
      break
  }

  return result
})

const fetchBooks = async () => {
  loading.value = true
  try {
    const data = await novelApi.listNovels()
    books.value = data.map((novel: NovelDTO) => {
      const fromPrefix = parseGenreWorldFromPremise(novel.premise || '').genre
      const g = novel.locked_genre?.trim() || fromPrefix || ''
      const progress = novel.target_chapters
        ? Math.round(((novel.chapters?.length || 0) / novel.target_chapters) * 100)
        : Math.round(((novel.chapters?.length || 0) / 100) * 100)
      return {
        slug: novel.id,
        title: novel.title,
        stage: novel.stage,
        stage_label: getNovelStageLabel(novel.stage),
        genre: g,
        chapter_count: novel.chapters?.length || 0,
        word_count: novel.total_word_count,
        target_chapters: novel.target_chapters || 100,
        progress: Math.min(100, progress),
      }
    })
  } catch {
    message.error('加载失败')
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

const goCreate = () => {
  router.push('/home')
}

const openBook = (slug: string) => {
  router.push(`/book/${slug}/workbench`)
}

const clearFilter = () => {
  searchQuery.value = ''
  filterStage.value = 'all'
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.library-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
  gap: 16px;
}

.page-title {
  margin: 0 0 4px;
  font-size: 24px;
  font-weight: 700;
  color: var(--app-text-primary);
  letter-spacing: -0.02em;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--app-text-muted);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--app-surface);
  border-radius: 12px;
  border: 1px solid var(--app-border);
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--app-text-muted);
  gap: 12px;
}

.loading-state p {
  margin: 0;
  font-size: 14px;
}

.empty-icon {
  font-size: 48px;
}

.empty-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.empty-desc {
  margin: 0;
  font-size: 14px;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.book-card {
  display: flex;
  flex-direction: column;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
  border-color: var(--color-brand-border);
}

.book-cover {
  position: relative;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.book-cover.cover-planning { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.book-cover.cover-writing { background: linear-gradient(135deg, #f59e0b, #d97706); }
.book-cover.cover-reviewing { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.book-cover.cover-completed { background: linear-gradient(135deg, #10b981, #059669); }

.cover-text {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  opacity: 0.9;
}

.cover-tag {
  position: absolute;
  top: 12px;
  right: 12px;
}

.book-info {
  padding: 16px;
  flex: 1;
}

.book-title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-genre {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--app-text-muted);
}

.book-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-num {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.stat-label {
  font-size: 11px;
  color: var(--app-text-muted);
}

.stat-divider {
  width: 1px;
  height: 24px;
  background: var(--app-border);
}

.book-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-progress :deep(.n-progress) {
  flex: 1;
}

.progress-text {
  font-size: 11px;
  color: var(--app-text-muted);
  min-width: 30px;
  text-align: right;
}

.book-actions {
  padding: 0 16px 16px;
}

.book-actions .n-button {
  width: 100%;
}

@media (max-width: 768px) {
  .library-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .filter-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .books-grid {
    grid-template-columns: 1fr;
  }
}

/* Editorial project library */
.library-page {
  max-width: 1440px;
  min-height: 100%;
  padding: clamp(22px, 3vw, 38px);
  background:
    radial-gradient(circle at 8% 0%, var(--color-brand-light), transparent 28%),
    var(--app-page-bg);
}

.page-header {
  align-items: flex-end;
  margin-bottom: 24px;
}

.page-heading {
  max-width: 680px;
}

.page-eyebrow,
.empty-kicker {
  display: block;
  margin-bottom: 7px;
  color: var(--color-brand);
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.page-title {
  margin-bottom: 7px;
  font-family: var(--font-serif);
  font-size: clamp(28px, 3vw, 36px);
  font-weight: 680;
}

.page-subtitle {
  font-size: 13px;
  line-height: 1.65;
}

.filter-bar {
  padding: 7px 10px;
  border-radius: 14px;
  box-shadow: var(--app-shadow-sm);
}

.empty-library {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  min-height: 430px;
  padding: 0;
  overflow: hidden;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 22px;
  box-shadow: var(--app-shadow-md);
}

.empty-copy {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  justify-content: center;
  padding: clamp(34px, 5vw, 66px);
}

.empty-copy .empty-title {
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: clamp(30px, 3.5vw, 44px);
  font-weight: 680;
  line-height: 1.26;
  letter-spacing: -0.035em;
  text-align: left;
}

.empty-copy .empty-desc {
  max-width: 620px;
  margin: 18px 0 26px;
  color: var(--app-text-secondary);
  font-size: 13px;
  line-height: 1.8;
  text-align: left;
}

.empty-roadmap {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-self: stretch;
  width: 100%;
  padding: 42px;
  color: #f7f8fc;
  background:
    radial-gradient(circle at 90% 10%, color-mix(in srgb, var(--color-brand) 42%, transparent), transparent 42%),
    linear-gradient(150deg, #20283c, #111827 72%);
}

.empty-roadmap-item {
  display: grid;
  grid-template-columns: 40px 1fr;
  align-items: center;
  min-height: 76px;
  gap: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.empty-roadmap-item:last-child {
  border-bottom: 0;
}

.empty-roadmap-item > span {
  color: rgba(255, 255, 255, 0.46);
  font-family: var(--font-mono);
  font-size: 10px;
}

.empty-roadmap-item div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.empty-roadmap-item strong {
  font-size: 14px;
  font-weight: 650;
}

.empty-roadmap-item small {
  color: rgba(255, 255, 255, 0.58);
  font-size: 10px;
}

.book-card {
  border-radius: 18px;
  box-shadow: var(--app-shadow-sm);
}

.book-card:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 3px;
}

@media (max-width: 820px) {
  .empty-library {
    grid-template-columns: 1fr;
  }

  .empty-roadmap {
    min-height: 280px;
  }
}

@media (max-width: 560px) {
  .library-page {
    padding: 16px;
  }

  .empty-copy,
  .empty-roadmap {
    padding: 24px;
  }
}
</style>
