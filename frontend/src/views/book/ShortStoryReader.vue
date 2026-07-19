<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NSpin, NButton, NDrawer, NDrawerContent, NIcon } from 'naive-ui'
import { ArrowBackOutline, ListOutline, TextOutline, ChevronForwardOutline, ChevronBackOutline } from '@vicons/ionicons5'
import { novelApi, type NovelDTO, type ChapterDTO } from '@/api/novel'

// 路由参数
const route = useRoute()
const router = useRouter()
const novelId = computed(() => route.params.novelId as string)

// 数据
const novel = ref<NovelDTO | null>(null)
const chapters = ref<ChapterDTO[]>([])
const loading = ref(true)
const currentChapterIndex = ref(0)
const showToc = ref(false)
const showSettings = ref(false)
const fontSize = ref(17) // 14/17/20/24 四档

// 计算属性
const currentChapter = computed(() => chapters.value[currentChapterIndex.value])
const totalChapters = computed(() => chapters.value.length)
const readProgress = computed(() => {
  if (totalChapters.value === 0) return 0
  return Math.round(((currentChapterIndex.value + 1) / totalChapters.value) * 100)
})

// 方法
async function loadData() {
  loading.value = true
  try {
    const data = await novelApi.getNovel(novelId.value)
    novel.value = data
    chapters.value = data.chapters || []
    // 短篇默认从第一章开始
    currentChapterIndex.value = 0
  } catch (e) {
    console.error('加载短篇失败', e)
  } finally {
    loading.value = false
  }
}

function goPrevChapter() {
  if (currentChapterIndex.value > 0) {
    currentChapterIndex.value--
    scrollToTop()
  }
}

function goNextChapter() {
  if (currentChapterIndex.value < totalChapters.value - 1) {
    currentChapterIndex.value++
    scrollToTop()
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goBack() {
  router.push(`/book/${novelId.value}/overview`)
}

function jumpToChapter(index: number) {
  currentChapterIndex.value = index
  showToc.value = false
  scrollToTop()
}

function setFontSize(size: number) {
  fontSize.value = size
}

function formatContent(content: string): string {
  if (!content) return ''
  // 转义 HTML
  let html = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // 段落：空行分隔
  const paragraphs = html.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean)
  return paragraphs.map(p => `<p>${p.replace(/\n/g, '<br/>')}</p>`).join('')
}

// 滚动进度追踪
function handleScroll() {
  // 可选：实时滚动进度
}

onMounted(() => {
  loadData()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="short-story-reader" :class="{ loading }">
    <!-- 顶部栏 -->
    <header class="reader-header">
      <button class="header-btn" @click="goBack">
        <n-icon size="20"><ArrowBackOutline /></n-icon>
      </button>
      <div class="header-title">{{ novel?.title || '加载中...' }}</div>
      <div class="header-actions">
        <button class="header-btn" @click="showSettings = !showSettings" title="字号">
          <n-icon size="20"><TextOutline /></n-icon>
        </button>
        <button class="header-btn" @click="showToc = true" title="目录">
          <n-icon size="20"><ListOutline /></n-icon>
        </button>
      </div>
    </header>

    <!-- 字号调节面板 -->
    <transition name="slide-down">
      <div v-if="showSettings" class="font-size-panel">
        <span class="panel-label">字号</span>
        <div class="font-size-options">
          <button v-for="size in [14, 17, 20, 24]" :key="size"
            class="font-size-btn" :class="{ active: fontSize === size }"
            @click="setFontSize(size)">
            {{ size === 14 ? '小' : size === 17 ? '中' : size === 20 ? '大' : '超大' }}
          </button>
        </div>
      </div>
    </transition>

    <!-- 阅读内容 -->
    <main v-if="!loading && currentChapter" class="reader-main" :style="{ fontSize: fontSize + 'px' }">
      <article class="reader-article">
        <!-- 章节标题 -->
        <h2 class="chapter-title">
          <span class="chapter-number">【{{ currentChapter.number }}】</span>
          <span class="chapter-name">{{ currentChapter.title }}</span>
        </h2>

        <!-- 章节正文 -->
        <div class="chapter-content" v-html="formatContent(currentChapter.content || '')"></div>

        <!-- 章节导航 -->
        <nav class="chapter-nav">
          <button class="nav-btn" :disabled="currentChapterIndex === 0" @click="goPrevChapter">
            <n-icon size="16"><ChevronBackOutline /></n-icon>上一节
          </button>
          <span class="nav-progress">{{ currentChapterIndex + 1 }} / {{ totalChapters }}</span>
          <button class="nav-btn" :disabled="currentChapterIndex === totalChapters - 1" @click="goNextChapter">
            下一节<n-icon size="16"><ChevronForwardOutline /></n-icon>
          </button>
        </nav>
      </article>
    </main>

    <!-- 加载中 -->
    <div v-if="loading" class="reader-loading">
      <n-spin size="large" />
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && chapters.length === 0" class="reader-empty">
      <p>这篇短篇还没有内容</p>
      <n-button @click="goBack">返回作品页</n-button>
    </div>

    <!-- 底部进度条 -->
    <footer v-if="!loading && totalChapters > 0" class="reader-footer">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: readProgress + '%' }"></div>
      </div>
      <span class="progress-text">已读 {{ readProgress }}%</span>
    </footer>

    <!-- 目录抽屉 -->
    <n-drawer v-model:show="showToc" :width="360" placement="right">
      <n-drawer-content title="目录" closable>
        <div class="toc-list">
          <div v-for="(ch, idx) in chapters" :key="ch.id"
            class="toc-item" :class="{ active: idx === currentChapterIndex }"
            @click="jumpToChapter(idx)">
            <span class="toc-number">【{{ ch.number }}】</span>
            <span class="toc-title">{{ ch.title || `第${ch.number}节` }}</span>
          </div>
        </div>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<style scoped>
.short-story-reader {
  min-height: 100vh;
  background: #fafafa;
}

.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #eee;
  z-index: 100;
}

.header-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  color: #333;
  transition: background 0.2s;
  padding: 0;
}

.header-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.header-title {
  flex: 1;
  text-align: center;
  font-weight: 500;
  font-size: 15px;
  color: #1a1a1a;
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.font-size-panel {
  position: fixed;
  top: 64px;
  right: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  padding: 16px;
  z-index: 99;
  min-width: 200px;
}

.panel-label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
  font-weight: 500;
}

.font-size-options {
  display: flex;
  gap: 8px;
}

.font-size-btn {
  flex: 1;
  padding: 8px 0;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.2s;
}

.font-size-btn:hover {
  border-color: #2080f0;
  color: #2080f0;
}

.font-size-btn.active {
  background: #2080f0;
  border-color: #2080f0;
  color: white;
}

.reader-main {
  max-width: 680px;
  margin: 0 auto;
  padding: 80px 24px 100px;
}

.reader-article {
  background: transparent;
}

.chapter-title {
  text-align: center;
  font-size: 1.3em;
  font-weight: 600;
  margin-bottom: 32px;
  color: #1a1a1a;
  line-height: 1.4;
}

.chapter-number {
  margin-right: 4px;
  color: #888;
  font-weight: 500;
}

.chapter-name {
  color: #1a1a1a;
}

.chapter-content {
  color: #333;
}

.chapter-content :deep(p) {
  text-indent: 0;
  line-height: 1.8;
  margin-bottom: 20px;
  letter-spacing: 0.05em;
  color: #333;
  word-break: break-word;
}

.chapter-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 60px;
  padding: 20px 0;
  border-top: 1px solid #eee;
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.2s;
}

.nav-btn:hover:not(:disabled) {
  border-color: #2080f0;
  color: #2080f0;
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-progress {
  font-size: 13px;
  color: #888;
}

.reader-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding-top: 80px;
}

.reader-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  color: #888;
}

.reader-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-top: 1px solid #eee;
  z-index: 100;
}

.progress-bar {
  flex: 1;
  height: 3px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  margin-right: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2080f0, #36ad6a);
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #888;
  flex-shrink: 0;
}

.toc-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toc-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
  font-size: 14px;
  color: #333;
}

.toc-item:hover {
  background: #f5f5f5;
}

.toc-item.active {
  background: #e8f4ff;
  color: #2080f0;
}

.toc-number {
  color: #888;
  flex-shrink: 0;
}

.toc-item.active .toc-number {
  color: #2080f0;
}

.toc-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 680px) {
  .reader-main {
    padding: 72px 16px 80px;
  }

  .header-title {
    max-width: 200px;
  }

  .font-size-panel {
    right: 8px;
    min-width: 180px;
  }
}
</style>
