<template>
  <div class="home">
    <div class="home-content">
      <div class="home-bg" aria-hidden="true" />

      <div class="container">
        <!-- Header -->
        <header class="header">
          <div class="header-content">
            <span class="page-eyebrow">开始写作</span>
            <h1 class="title">创建新作品</h1>
            <p class="subtitle">
              只需填写书名和故事梗概，AI 会自动帮你完成其余设置。
            </p>
          </div>
        </header>

        <!-- Create Card -->
        <n-card class="create-card" :bordered="false">
          <n-space vertical :size="20">
            <div class="create-header">
              <div class="create-title-wrap">
                <span class="create-icon">✍</span>
                <h3 class="create-title">开始你的故事</h3>
              </div>
            </div>

            <div>
              <n-input
                v-model:value="newBook.title"
                placeholder="输入书名"
                :disabled="creating"
                size="large"
                class="title-input"
              />

              <n-input
                ref="createInputRef"
                v-model:value="newBook.premise"
                type="textarea"
                placeholder="用一段话描述你的故事…&#10;&#10;例如：废柴赘婿觉醒签到系统，从被退婚到一方巨擘。"
                :rows="5"
                :disabled="creating"
                size="large"
                class="premise-input"
                show-count
                :maxlength="PREMISE_MAX_LEN"
              />

              <n-space justify="end">
                <n-button
                  type="primary"
                  size="large"
                  round
                  :loading="creating"
                  :disabled="!newBook.premise.trim()"
                  @click="handleCreate"
                >
                  <template #icon>
                    <n-icon><IconSpark /></n-icon>
                  </template>
                  创建作品
                </n-button>
              </n-space>
            </div>

            <div class="create-collapsed">
              <p class="create-collapsed-desc">已有 {{ books.length }} 部作品</p>
              <n-button
                type="primary"
                size="large"
                round
                @click="focusCreateInput()"
              >
                <template #icon>
                  <n-icon><IconSpark /></n-icon>
                </template>
                创建新作品
              </n-button>
            </div>
          </n-space>
        </n-card>

        <!-- Books Section -->
        <section class="books-section">
          <div class="section-header">
            <div class="section-left">
              <h2 class="section-title">我的书目</h2>
              <span class="book-count" v-if="!loading">{{ filteredBooks.length }} 本</span>
            </div>
            <div class="section-right">
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
              <n-button
                v-if="selectedBooks.length > 0"
                type="error"
                secondary
                @click="showBatchDeleteConfirm = true"
              >
                <template #icon>
                  <n-icon><IconTrash /></n-icon>
                </template>
                删除选中 ({{ selectedBooks.length }})
              </n-button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="loading-state">
            <n-spin size="large" />
            <p>加载中…</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="books.length === 0" class="empty-state">
            <div class="empty-illustration">
              <span class="empty-icon">墨</span>
            </div>
            <h3 class="empty-title">还没有作品</h3>
            <p class="empty-desc">在上方写下故事核心，建立第一部叙事工程。</p>
            <n-button type="primary" size="large" round @click="focusCreateInput">
              <template #icon>
                <n-icon><IconSpark /></n-icon>
              </template>
              创建第一部作品
            </n-button>
          </div>

          <!-- No Results State -->
          <div v-else-if="filteredBooks.length === 0" class="no-results-state">
            <span class="no-results-icon">🔍</span>
            <p>未找到匹配「{{ searchQuery }}」的书目</p>
            <n-button text type="primary" @click="searchQuery = ''">清除搜索</n-button>
          </div>

          <!-- Books Grid -->
          <template v-else>
            <!-- Selection Bar (仅搜索模式下显示) -->
            <div class="selection-bar" v-if="filteredBooks.length > 0 && searchQuery">
              <n-checkbox
                :checked="isAllSelected"
                :indeterminate="isPartialSelected"
                @update:checked="toggleSelectAll"
              >
                全选
              </n-checkbox>
              <span class="selection-hint" v-if="selectedBooks.length > 0">
                已选择 {{ selectedBooks.length }} 本
              </span>
            </div>

            <!-- 书目卡片：响应式网格布局 -->
            <div class="books-grid">
              <div
                v-for="(book, idx) in filteredBooks"
                :key="book.slug"
                class="book-card"
                :class="{ 'is-selected': selectedBooks.includes(book.slug) }"
                :style="{ animationDelay: `${idx * 0.04}s` }"
                @click="navigateToBook(book.slug)"
              >
                <div class="card-top">
                  <span class="book-dot" :class="`dot-${book.stage}`"></span>
                  <span class="book-card-title">{{ book.title }}</span>
                </div>
                <div class="card-meta">
                  <n-tag :type="getStageType(book.stage)" size="small" round borderable>
                    {{ book.stage_label }}
                  </n-tag>
                  <span class="meta-genre">{{ book.genre || '未分类' }}</span>
                </div>
                <div class="card-stats" v-if="book.chapter_count || book.word_count">
                  <template v-if="book.chapter_count">
                    <span>{{ book.chapter_count }} 章</span>
                  </template>
                  <template v-if="book.word_count">
                    <span>{{ formatWordCount(book.word_count) }}</span>
                  </template>
                </div>
                <div class="card-actions" @click.stop>
                  <n-checkbox
                    :checked="selectedBooks.includes(book.slug)"
                    @update:checked="(val: boolean) => toggleBookSelection(book.slug, val)"
                  />
                  <n-popconfirm
                    positive-text="删除"
                    negative-text="取消"
                    @positive-click="() => handleDeleteBook(book.slug)"
                  >
                    <template #trigger>
                      <n-button
                        quaternary
                        circle
                        size="tiny"
                        type="error"
                        :loading="deletingSlug === book.slug"
                        aria-label="删除书目"
                      >
                        <template #icon>
                          <n-icon><IconTrash /></n-icon>
                        </template>
                      </n-button>
                    </template>
                    将删除「{{ book.title }}」及本地全部章节与设定，且不可恢复。确定删除吗？
                  </n-popconfirm>
                </div>
              </div>
            </div>
          </template>
        </section>

        <!-- 底部版权 -->
        <footer class="home-footer">
          <span class="footer-brand">{{ BRAND.productName }}</span>
          <span class="footer-sep">·</span>
          <span class="footer-sub">{{ BRAND.chineseName }}</span>
          <span class="footer-text">{{ BRAND.credit }}</span>
        </footer>
      </div>
    </div>

    <!-- Batch Delete Confirm Modal -->
    <n-modal v-model:show="showBatchDeleteConfirm" preset="confirm" type="error" title="确认批量删除">
      <template #default>
        确定要删除选中的 <strong>{{ selectedBooks.length }}</strong> 本书籍吗？此操作不可恢复。
      </template>
      <template #action>
        <n-space>
          <n-button @click="showBatchDeleteConfirm = false">取消</n-button>
          <n-button type="error" :loading="batchDeleting" @click="handleBatchDelete">
            确认删除
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 新书向导：仅挂载一次且 show 恒为 true，避免「先关再开」的双过渡（原 newNovelId + showSetupGuide 分步更新导致） -->
    <NovelSetupGuide
      v-if="setupWizard"
      :key="setupWizard.novelId"
      :novel-id="setupWizard.novelId"
      :target-chapters="setupWizard.targetChapters"
      :show="true"
      @update:show="(open) => { if (!open) setupWizard = null }"
      @complete="handleSetupComplete"
      @skip="handleSetupSkip"
    />

  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, h, ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NIcon } from 'naive-ui'
import { novelApi, type NovelDTO } from '../api/novel'
import { isWizardCompleted } from '@/utils/wizardStageCache'
import { parseGenreWorldFromPremise } from '@/utils/premisePresets'
import { useStatsStore } from '@/stores/statsStore'
import { formatApiError } from '@/utils/apiError'
import { BRAND } from '@/constants/brand'
import {
  NOVEL_LENGTH_TIER_OPTIONS,
  getNovelStageLabel,
  getNovelStageTagType,
  type NovelLengthTier,
} from '@/domain/novel'

const MarketTaxonomyPicker = defineAsyncComponent(
  () => import('@/components/taxonomy/MarketTaxonomyPicker.vue'),
)
const NovelSetupGuide = defineAsyncComponent(
  () => import('@/components/onboarding/NovelSetupGuide.vue'),
)

// Icons
const IconSpark = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M13 2L3 14h8l-1 8 10-12h-8l1-8z' }))

const IconSearch = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z' }))

const IconTrash = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z' }))



interface BookListItem {
  slug: string
  title: string
  stage: string
  stage_label: string
  genre: string
  chapter_count?: number
  word_count?: number
}

const router = useRouter()
const message = useMessage()
const statsStore = useStatsStore()

const createInputRef = ref<any>(null)
const creating = ref(false)
const loading = ref(false)
const books = ref<BookListItem[]>([])
const searchQuery = ref('')
const deletingSlug = ref<string | null>(null)
/** 有值时挂载向导；与 show 分离，挂载后始终 :show="true"，避免 Modal 先 false 再 true 闪烁 */
const setupWizard = ref<{ novelId: string; targetChapters: number } | null>(null)

// Batch delete
const selectedBooks = ref<string[]>([])
const showBatchDeleteConfirm = ref(false)
const batchDeleting = ref(false)

const PREMISE_MAX_LEN = 2000

const newBook = ref({
  title: '',
  premise: '',
})

const filteredBooks = computed(() => {
  if (!searchQuery.value.trim()) {
    return books.value
  }
  const query = searchQuery.value.toLowerCase()
  return books.value.filter(
    book =>
      book.title.toLowerCase().includes(query) ||
      (book.genre && book.genre.toLowerCase().includes(query))
  )
})



const isAllSelected = computed(() => {
  return filteredBooks.value.length > 0 && selectedBooks.value.length === filteredBooks.value.length
})

const isPartialSelected = computed(() => {
  return selectedBooks.value.length > 0 && selectedBooks.value.length < filteredBooks.value.length
})

const fetchBooks = async () => {
  loading.value = true
  try {
    const novels = await novelApi.listNovels()
    books.value = novels.map((novel: NovelDTO) => {
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
    return (count / 10000).toFixed(1) + '万字'
  }
  return count + '字'
}

const handleCreate = async () => {
  if (!newBook.value.premise.trim()) {
    message.warning('请输入故事梗概')
    return
  }

  creating.value = true
  try {
    const title = newBook.value.title || newBook.value.premise.substring(0, 20)
    const novelId = `novel-${Date.now()}`

    const result = await novelApi.createNovel({
      novel_id: novelId,
      title: title,
      author: '作者',
      premise: newBook.value.premise.trim(),
      genre: '通用',
      world_preset: '默认',
      story_structure: '三幕式',
      pacing_control: '适中',
      writing_style: '流畅',
      special_requirements: '',
      length_tier: 'standard',
      target_chapters: 0,
    })
    message.success('创建成功')

    setupWizard.value = {
      novelId: result.id,
      targetChapters: result.target_chapters,
    }
  } catch (error: unknown) {
    message.error(formatApiError(error, '创建失败'))
  } finally {
    creating.value = false
  }
}

const handleSetupComplete = () => {
  const id = setupWizard.value?.novelId
  setupWizard.value = null
  if (id) router.push(`/book/${id}/workbench`)
}

const handleSetupSkip = () => {
  const id = setupWizard.value?.novelId
  setupWizard.value = null
  if (id) router.push(`/book/${id}/workbench`)
}

const navigateToBook = (novelId: string) => {
  // 未完成向导的书重新打开向导
  if (!isWizardCompleted(novelId)) {
    // 查找该书的 target_chapters
    const novel = books.value.find(b => b.slug === novelId)
    setupWizard.value = {
      novelId,
      targetChapters: 100, // 默认值，向导内部会从 API 获取真实值
    }
    return
  }
  router.push(`/book/${novelId}/workbench`)
}

const handleDeleteBook = async (slug: string) => {
  deletingSlug.value = slug
  try {
    await novelApi.deleteNovel(slug)
    message.success('书目已删除')
    books.value = books.value.filter(b => b.slug !== slug)
    selectedBooks.value = selectedBooks.value.filter(s => s !== slug)
    await statsStore.loadGlobalStats(true)
  } catch (error: unknown) {
    message.error(formatApiError(error, '删除失败'))
  } finally {
    deletingSlug.value = null
  }
}

const toggleBookSelection = (slug: string, selected: boolean) => {
  if (selected) {
    if (!selectedBooks.value.includes(slug)) {
      selectedBooks.value.push(slug)
    }
  } else {
    selectedBooks.value = selectedBooks.value.filter(s => s !== slug)
  }
}

const toggleSelectAll = (checked: boolean) => {
  if (checked) {
    selectedBooks.value = filteredBooks.value.map(b => b.slug)
  } else {
    selectedBooks.value = []
  }
}

const handleBatchDelete = async () => {
  batchDeleting.value = true
  try {
    let successCount = 0
    let failCount = 0
    
    for (const slug of selectedBooks.value) {
      try {
        await novelApi.deleteNovel(slug)
        successCount++
      } catch {
        failCount++
      }
    }
    
    if (successCount > 0) {
      message.success(`成功删除 ${successCount} 本书目`)
      books.value = books.value.filter(b => !selectedBooks.value.includes(b.slug))
      selectedBooks.value = []
      await statsStore.loadGlobalStats(true)
    }
    if (failCount > 0) {
      message.warning(`${failCount} 本删除失败`)
    }
    showBatchDeleteConfirm.value = false
  } finally {
    batchDeleting.value = false
  }
}

const focusCreateInput = () => {
  nextTick(() => {
    createInputRef.value?.focus()
  })
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleRefreshList = async () => {
  await fetchBooks()
  message.success('列表已刷新')
}

const getStageType = (stage: string) => {
  return getNovelStageTagType(stage)
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.home-content {
  min-height: 100vh;
  padding: 32px;
  position: relative;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

/* 顶栏：与 StatsTopBar 同款渐变，AI 控制台 / 提示词广场 / 设置 */

.home-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 110% 80% at 50% -30%, var(--color-brand-light), transparent 55%),
    radial-gradient(ellipse 60% 50% at 100% 20%, rgba(14, 165, 233, 0.12), transparent 45%),
    radial-gradient(ellipse 50% 40% at 0% 60%, var(--color-gold-dim), transparent 50%),
    linear-gradient(180deg, var(--app-page-bg) 0%, var(--app-surface-subtle) 45%, var(--app-page-bg) 100%);
  z-index: 0;
}

.container {
  position: relative;
  z-index: 1;
  max-width: 1240px;
  margin: 0 auto;
}

.header {
  position: relative;
  text-align: left;
  margin-bottom: 24px;
  animation: fade-up 0.55s ease both;
}

.header-content {
  padding: 0 52px 0 0;
}

.page-eyebrow {
  display: block;
  margin-bottom: 7px;
  color: var(--color-brand);
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.title {
  margin-bottom: 8px;
  font-family: var(--font-serif);
  font-size: clamp(30px, 4vw, 42px);
  font-weight: 680;
  letter-spacing: -0.035em;
  color: var(--app-text-primary);
}

.subtitle {
  max-width: 720px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--app-text-secondary);
  margin: 0;
  font-weight: 400;
}


.create-card {
  margin-bottom: 32px;
  border-radius: 20px;
  box-shadow: var(--app-shadow-sm);
  border: 1px solid var(--app-border);
  animation: fade-up 0.55s ease 0.08s both;
}

.create-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.create-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.create-icon {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  color: var(--color-brand);
  background: var(--color-brand-light);
  border: 1px solid var(--color-brand-border);
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 9px;
}

.create-collapsed {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.create-collapsed-desc {
  margin: 0;
  font-size: 13px;
  color: var(--app-text-muted);
}

.create-title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
}

.premise-input :deep(textarea) {
  font-size: 15px;
  line-height: 1.6;
}

.taxonomy-block {
  margin-top: 4px;
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.02);
  border: 1px solid var(--app-border);
}
.taxonomy-block-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}
.taxonomy-block-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--app-text-primary);
  letter-spacing: 0.04em;
}
.taxonomy-block-sub {
  font-size: 12px;
  color: var(--app-text-muted);
  line-height: 1.45;
}

.length-tier-block {
  margin-top: 8px;
  padding: 4px 0 4px;
}

.length-tier-label {
  font-size: 13px;
  color: var(--app-text-secondary);
  margin-bottom: 10px;
}

.length-tier-space {
  width: 100%;
}

.length-tier-group :deep(.n-radio) {
  align-items: flex-start;
}

.length-tier-radio {
  flex: 1 1 200px;
  min-width: min(200px, 100%);
}

.length-tier-option-inner {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
  max-width: 280px;
}

.length-tier-title {
  font-weight: 600;
  line-height: 1.35;
}

.length-tier-hint {
  font-size: 12px;
  color: var(--app-text-muted);
  line-height: 1.45;
}

.advanced-settings {
  padding: 16px;
  background: rgba(79, 70, 229, 0.04);
  border-radius: 12px;
  border: 1px solid rgba(79, 70, 229, 0.1);
}

.w-full {
  width: 100%;
}

.books-section {
  background: var(--app-surface);
  border-radius: 20px;
  padding: 28px;
  box-shadow: var(--app-shadow-sm);
  border: 1px solid var(--app-border);
  animation: fade-up 0.55s ease 0.14s both;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.section-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.book-count {
  font-size: 13px;
  color: var(--app-text-muted);
  background: var(--app-surface-subtle);
  padding: 4px 10px;
  border-radius: 12px;
}

.section-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.selection-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: var(--app-surface-subtle);
  border-radius: 10px;
  margin-bottom: 20px;
}

.selection-hint {
  font-size: 13px;
  color: var(--app-text-muted);
}

.loading-state,
.empty-state,
.no-results-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 72px 20px;
  color: var(--app-text-muted);
}

.loading-state p {
  margin-top: 16px;
  font-size: 14px;
}

.empty-state {
  gap: 16px;
}

.empty-illustration {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, var(--app-surface-subtle) 0%, var(--app-border) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-brand-border);
}

.empty-icon {
  font-size: 24px;
  color: var(--color-brand);
  font-family: var(--font-serif);
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
  color: var(--app-text-muted);
}

.no-results-state {
  gap: 12px;
}

.no-results-icon {
  font-size: 40px;
}

.no-results-state p {
  margin: 0;
  font-size: 14px;
}

/* ── 书目：响应式网格布局 ── */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

/* 卡片 */
.book-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  animation: fade-up 0.35s ease both;
  overflow: hidden;
}

.book-card:hover {
  border-color: var(--color-brand, #4f46e5);
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.1);
  transform: translateY(-2px);
}

.book-card.is-selected {
  border-color: var(--color-brand, #4f46e5);
  background: var(--color-brand-light, rgba(79, 70, 229, 0.04));
}

/* 阶段状态小圆点 */
.book-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-block;
}

.book-dot.dot-planning { background: #3b82f6; }
.book-dot.dot-writing { background: #f59e0b; }
.book-dot.dot-reviewing { background: #8b5cf6; }
.book-dot.dot-completed { background: #10b981; }

/* 卡片顶部：标题 + 圆点 */
.card-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.book-card-title {
  font-size: 15px;
  font-weight: 650;
  color: var(--app-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

/* 卡片元信息行：标签 + 类型 */
.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.meta-genre {
  font-size: 12px;
  color: var(--app-text-muted);
}

/* 卡片统计信息 */
.card-stats {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: var(--app-text-muted);
  margin-bottom: 12px;
  flex: 1;
}

/* 卡片操作按钮 */
.card-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.18s ease;
  padding-top: 4px;
  border-top: 1px solid transparent;
}

.book-card:hover .card-actions {
  opacity: 1;
}



@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 1200px) {
  .home-content {
    padding: 24px;
  }


}

/* ── 底部版权 ──────────────────────────────── */
.home-footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 28px 20px 32px;
  margin-top: 40px;
  border-top: 1px solid var(--app-border);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--app-text-muted);
  line-height: 1.6;
}

.footer-brand {
  font-weight: 700;
  color: var(--color-gold);
  letter-spacing: 0.03em;
}

.footer-sep {
  opacity: 0.4;
}

.footer-sub {
  font-weight: 600;
  color: var(--color-gold-light);
  opacity: 0.8;
}

.footer-text {
  color: var(--app-text-muted);
}

.footer-link {
  color: var(--color-gold);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dashed var(--color-gold-border);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.footer-link:hover {
  color: var(--color-gold-light);
  border-bottom-style: solid;
  box-shadow: 0 0 8px var(--color-glow-gold);
}

@media (max-width: 768px) {
  .home-content {
    margin-left: 0;
    padding: 16px;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .section-right {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }

  .card-actions {
    opacity: 1; /* 移动端始终显示操作按钮 */
  }
}

/* ── 查看全部书目弹窗样式 ── */
.all-books-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

</style>
