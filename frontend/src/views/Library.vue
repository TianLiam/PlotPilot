<template>
  <div class="library-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">我的书架</h1>
        <p class="page-subtitle">共 {{ filteredBooks.length }} 本小说</p>
      </div>
      <div class="header-actions">
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

    <div class="filter-bar">
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

    <div v-else-if="books.length === 0" class="empty-state">
      <div class="empty-illustration">
        <span class="empty-icon">📚</span>
      </div>
      <h3 class="empty-title">书架空空如也</h3>
      <p class="empty-desc">创建你的第一本小说，开启创作之旅</p>
      <n-button type="primary" size="large" round @click="goCreate">
        <template #icon>
          <n-icon><IconPlus /></n-icon>
        </template>
        立即创建
      </n-button>
    </div>

    <div v-else-if="filteredBooks.length === 0" class="empty-state">
      <span class="empty-icon">🔍</span>
      <p>没有找到匹配的小说</p>
      <n-button text type="primary" @click="clearFilter">清除筛选</n-button>
    </div>

    <div v-else class="books-grid">
      <div
        v-for="book in filteredBooks"
        :key="book.slug"
        class="book-card"
        @click="openBook(book.slug)"
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
</style>
