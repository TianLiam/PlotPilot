<template>
  <n-spin :show="pageLoading" class="chapter-spin" description="加载章节…">
  <div class="chapter-page">
    <header class="chapter-header">
      <div class="chapter-header-shell">
        <button class="chapter-back" type="button" @click="goBack">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M19 12H5m6-6-6 6 6 6" />
          </svg>
          <span>返回工作台</span>
        </button>

        <div class="chapter-heading-row">
          <div class="chapter-heading-copy">
            <span class="chapter-eyebrow">CHAPTER WRITING</span>
            <h1>第 {{ chapterId }} 章</h1>
            <p>专注写作的纯净空间 · Ctrl+S 快捷保存</p>
          </div>
          <div class="chapter-heading-actions">
            <n-space :size="8" :wrap="false">
              <n-button-group>
                <n-button size="small" @click="prevChapter" :disabled="!canPrev">
                  <template #icon>
                    <span class="ico-tiny">◀</span>
                  </template>
                  上一章
                </n-button>
                <n-button size="small" @click="nextChapter" :disabled="!canNext">
                  下一章
                  <template #icon>
                    <span class="ico-tiny">▶</span>
                  </template>
                </n-button>
              </n-button-group>

              <n-dropdown :options="toolOptions" @select="handleToolSelect">
                <n-button size="small" secondary>工具</n-button>
              </n-dropdown>

              <n-button size="small" quaternary @click="goCastGraph">关系图</n-button>

              <n-button type="primary" size="small" round :loading="saving" @click="saveContent" :disabled="!contentDirty">
                保存
              </n-button>
            </n-space>
          </div>
        </div>

        <div class="chapter-status-bar">
          <n-tag :type="saveStatus === 'saved' ? 'success' : saveStatus === 'saving' ? 'warning' : 'default'" round size="small">
            {{ saveStatusText }}
          </n-tag>
          <span v-if="lastSaveTime" class="last-save-time">上次保存 {{ lastSaveTime }}</span>
        </div>
      </div>
    </header>

    <div class="chapter-content">
      <n-split direction="horizontal" :default-size="0.72" :min="0.55" :max="0.88">
        <template #1>
          <div class="editor-card">
            <div class="editor-area">
              <n-input
                v-model:value="content"
                type="textarea"
                class="content-editor"
                placeholder="开始写作…&#10;&#10;Ctrl+S 保存 · 自动保存约 30 秒"
                @update:value="onInput"
                :autosize="{ minRows: 22 }"
              />
              <div class="editor-footer">
                <n-space>
                  <n-text depth="3">{{ wordCount }} 字</n-text>
                  <n-divider vertical />
                  <n-text depth="3">{{ lineCount }} 行</n-text>
                </n-space>
                <n-button size="small" quaternary @click="showPreview = !showPreview">
                  {{ showPreview ? '隐藏预览' : 'Markdown 预览' }}
                </n-button>
              </div>

              <transition name="preview-slide">
                <div v-if="showPreview" class="preview-panel">
                  <n-divider title-placement="left">预览</n-divider>
                  <div class="preview-content markdown-body md-body" v-html="previewHtml" />
                </div>
              </transition>
            </div>
          </div>
        </template>

        <template #2>
          <div class="review-card">
            <n-tabs type="segment" animated class="review-tabs">
              <n-tab-pane name="review" tab="审定">
                <n-form label-placement="top" class="review-form">
                  <n-form-item label="状态">
                    <n-radio-group v-model:value="reviewStatus" name="review-status">
                      <n-space>
                        <n-radio value="pending">待阅</n-radio>
                        <n-radio value="ok">已定稿</n-radio>
                        <n-radio value="revise">需修订</n-radio>
                      </n-space>
                    </n-radio-group>
                  </n-form-item>
                  <n-form-item label="批注">
                    <n-input v-model:value="reviewMemo" type="textarea" :rows="10" placeholder="审读意见…" />
                  </n-form-item>
                  <n-space vertical :size="8" style="width: 100%">
                    <n-button block :loading="savingAiReview" secondary @click="runAiReview(false)">
                      生成审读意见
                    </n-button>
                    <n-button block :loading="savingAiReview" type="info" secondary @click="runAiReview(true)">
                      生成并写入审定
                    </n-button>
                    <n-text depth="3" style="font-size: 11px; line-height: 1.45">
                      基于合并正文（含 chapters/NNN 下分场景 parts）与大纲一句纲；「生成意见」仅填入上方表单项。
                    </n-text>
                  </n-space>
                  <n-button type="primary" block round :loading="savingReview" @click="saveReview">保存审定</n-button>
                </n-form>
              </n-tab-pane>

              <n-tab-pane name="inference">
                <template #tab>
                  <span data-testid="chapter-tab-inference">推断证据</span>
                </template>
                <n-spin :show="inferenceLoading">
                  <n-space vertical :size="12" style="width: 100%">
                    <n-alert v-if="inferenceHint" type="info" :title="inferenceHintTitle" style="font-size: 12px">
                      {{ inferenceHint }}
                    </n-alert>
                    <n-space justify="space-between" align="center">
                      <n-text depth="3" style="font-size: 12px">
                        来自章节元素自动推断的 <code>chapter_inferred</code> 三元组及证据链
                      </n-text>
                      <n-space :size="8">
                        <n-button
                          size="tiny"
                          quaternary
                          data-testid="chapter-inference-refresh"
                          :loading="inferenceLoading"
                          @click="loadInferenceEvidence"
                        >
                          刷新
                        </n-button>
                        <n-popconfirm @positive-click="revokeAllInference">
                          <template #trigger>
                            <n-button
                              size="tiny"
                              type="error"
                              secondary
                              :disabled="!storyNodeId"
                              :loading="revokeAllLoading"
                            >
                              撤销本章全部推断
                            </n-button>
                          </template>
                          将删除本章节点下的溯源；无剩余证据的推断三元组会被移除。确定？
                        </n-popconfirm>
                      </n-space>
                    </n-space>
                    <n-empty v-if="!inferenceLoading && !inferenceFacts.length" description="暂无本章推断记录" size="small" />
                    <n-collapse v-else accordion>
                      <n-collapse-item
                        v-for="item in inferenceFacts"
                        :key="item.fact.id"
                        :title="`${item.fact.subject} —${item.fact.predicate}→ ${item.fact.object}`"
                        :name="item.fact.id"
                      >
                        <n-space vertical :size="8" style="width: 100%">
                          <n-descriptions label-placement="left" :column="1" size="small" bordered>
                            <n-descriptions-item label="ID">{{ item.fact.id }}</n-descriptions-item>
                            <n-descriptions-item label="置信度">
                              {{ item.fact.confidence != null ? item.fact.confidence : '—' }}
                            </n-descriptions-item>
                          </n-descriptions>
                          <n-text depth="3" style="font-size: 11px">证据链（rule / 元素行 / role）</n-text>
                          <ul class="inf-prov-list">
                            <li v-for="p in item.provenance" :key="p.id">
                              <code>{{ p.rule_id }}</code>
                              <span v-if="p.chapter_element_id"> · 元素 {{ p.chapter_element_id }}</span>
                              · {{ p.role }}
                            </li>
                          </ul>
                          <n-button
                            size="small"
                            type="warning"
                            secondary
                            :loading="revokingId === item.fact.id"
                            @click="revokeOneInference(item.fact.id)"
                          >
                            撤销此条推断
                          </n-button>
                        </n-space>
                      </n-collapse-item>
                    </n-collapse>
                  </n-space>
                </n-spin>
              </n-tab-pane>

              <n-tab-pane name="info" tab="信息">
                <n-space vertical :size="16" class="info-stats">
                  <n-statistic label="字数" :value="wordCount" />
                  <n-statistic label="行数" :value="lineCount" />
                  <n-statistic label="段落" :value="paragraphCount" />
                  <n-divider />
                  <div v-if="chapterStructure">
                    <n-statistic label="分析字数" :value="chapterStructure.word_count" />
                    <n-statistic label="分析段落" :value="chapterStructure.paragraph_count" />
                    <n-statistic label="对话占比" :value="(chapterStructure.dialogue_ratio * 100).toFixed(1) + '%'" />
                    <n-statistic label="场景数" :value="chapterStructure.scene_count" />
                    <n-text depth="3" class="meta-line">节奏：{{ chapterStructure.pacing }}</n-text>
                  </div>
                  <n-divider />
                  <n-text depth="3" class="meta-line">创建：{{ createTime }}</n-text>
                  <n-text depth="3" class="meta-line">修改：{{ updateTime }}</n-text>
                </n-space>
              </n-tab-pane>
            </n-tabs>
          </div>
        </template>
      </n-split>
    </div>
  </div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { chapterApi } from '../api/chapter'
import { runtimePerformance } from '../config/performance'
import { useDebouncedTask } from '../composables/useDebouncedTask'
import { knowledgeGraphApi, type InferenceFactBundle } from '../api/knowledgeGraph'
import { useStatsStore } from '../stores/statsStore'
import { formatApiError } from '../utils/apiError'

const statusToNew = (oldStatus: string): string => {
  const map: Record<string, string> = {
    'pending': 'draft',
    'ok': 'approved',
    'revise': 'reviewed'
  }
  return map[oldStatus] || 'draft'
}

const statusToOld = (newStatus: string): string => {
  const map: Record<string, string> = {
    'draft': 'pending',
    'approved': 'ok',
    'reviewed': 'revise'
  }
  return map[newStatus] || 'pending'
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const statsStore = useStatsStore()

const inferenceLoading = ref(false)
const inferenceFacts = ref<InferenceFactBundle[]>([])
const inferenceHint = ref('')
const inferenceHintTitle = ref('提示')
const storyNodeId = ref<string | null>(null)
const revokeAllLoading = ref(false)
const revokingId = ref<string | null>(null)

const slug = route.params.slug as string
const chapterId = computed(() => {
  const id = Number(route.params.id as string)
  if (isNaN(id) || id <= 0) {
    message.error('无效的章节ID')
    return null
  }
  return id
})

const goHome = () => {
  const n = chapterId.value
  router.push(
    n != null
      ? { path: `/book/${slug}/workbench`, query: { chapter: String(n) } }
      : `/book/${slug}/workbench`
  )
}

watch(chapterId, (newId) => {
  if (newId === null) {
    goHome()
  }
}, { immediate: true })

const content = ref('')
const saving = ref(false)
const saveStatus = ref<'unsaved' | 'saving' | 'saved'>('saved')
const lastSaveTime = ref('')

const reviewStatus = ref('pending')
const reviewMemo = ref('')
const savingReview = ref(false)
const savingAiReview = ref(false)
const chapterStructure = ref<{
  word_count: number
  paragraph_count: number
  dialogue_ratio: number
  scene_count: number
  pacing: string
} | null>(null)

const showPreview = ref(false)
const chapterIds = ref<number[]>([])
const pageLoading = ref(true)

const wordCount = computed(() => content.value.replace(/\s/g, '').length)
const lineCount = computed(() => (content.value ? content.value.split('\n').length : 0))
const paragraphCount = computed(() =>
  content.value ? content.value.split(/\n\s*\n/).filter(p => p.trim()).length : 0
)

const previewHtml = ref<string>('')

const parseMarkdown = () => {
  const html = marked.parse(content.value, { breaks: true, async: false }) as string
  const sanitizedHtml = DOMPurify.sanitize(html)
  previewHtml.value = sanitizedHtml
}

const previewTask = useDebouncedTask(
  parseMarkdown,
  runtimePerformance.editor.chapterPreviewDebounceMs,
)

const updatePreview = (debounce = false) => {
  if (debounce) {
    previewTask.schedule()
  } else {
    previewTask.cancel()
    parseMarkdown()
  }
}

const saveStatusText = computed(() => {
  const map = { unsaved: '未保存', saving: '保存中…', saved: '已保存' }
  return map[saveStatus.value]
})

const contentDirty = computed(() => saveStatus.value === 'unsaved')

const currentChapterIndex = computed(() => {
  const cid = chapterId.value
  return cid == null ? -1 : chapterIds.value.indexOf(cid)
})

const canPrev = computed(() => {
  const i = currentChapterIndex.value
  return i > 0
})

const canNext = computed(() => {
  const i = currentChapterIndex.value
  return i >= 0 && i < chapterIds.value.length - 1
})

const createTime = ref('—')
const updateTime = ref('—')

const toolOptions = [
  { label: '复制全文', key: 'copy' },
  { label: '清空正文', key: 'clear' },
]

const handleToolSelect = (key: string) => {
  if (key === 'copy') {
    void navigator.clipboard.writeText(content.value).then(
      () => message.success('已复制'),
      () => message.error('复制失败')
    )
  }
  if (key === 'clear') {
    content.value = ''
    onInput()
    updatePreview(false)
  }
}

const saveContent = async (fromAutosave = false) => {
  const cid = chapterId.value
  if (cid == null || saving.value) return
  if (fromAutosave && saveStatus.value === 'saved') return
  saving.value = true
  saveStatus.value = 'saving'

  try {
    await chapterApi.updateChapter(slug, cid, {
      content: content.value
    })
    saveStatus.value = 'saved'
    lastSaveTime.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    updateTime.value = new Date().toLocaleString('zh-CN', { hour12: false })
    message.success('已保存')
    statsStore.onChapterSaved(slug, cid)
  } catch (error) {
    console.error('Failed to save content:', error)
    saveStatus.value = 'unsaved'
    message.error('保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

const autosaveTask = useDebouncedTask(
  () => saveContent(true),
  runtimePerformance.editor.chapterAutosaveMs,
  {
    onError: error => {
      console.error('Autosave failed:', error)
    },
  },
)

const onInput = () => {
  saveStatus.value = 'unsaved'
  autosaveTask.schedule()
  updatePreview(true)
}

const saveReview = async () => {
  const cid = chapterId.value
  if (cid == null) return
  savingReview.value = true
  try {
    const newStatus = statusToNew(reviewStatus.value)
    await chapterApi.saveChapterReview(slug, cid, newStatus, reviewMemo.value)
    message.success('审定已保存')
    statsStore.onChapterSaved(slug, cid)
  } catch (error) {
    console.error('Failed to save review:', error)
    message.error('保存失败，请稍后重试')
  } finally {
    savingReview.value = false
  }
}

const runAiReview = async (save: boolean) => {
  const cid = chapterId.value
  if (cid == null) return
  savingAiReview.value = true
  try {
    const r = await chapterApi.reviewChapterAi(slug, cid, save)
    reviewStatus.value = statusToOld(r.status)
    reviewMemo.value = r.memo
    message.success(save ? '已写入审定意见' : '已填入审读意见')
  } catch (e: unknown) {
    message.error(formatApiError(e, '生成失败'))
  } finally {
    savingAiReview.value = false
  }
}

const goBack = () => {
  const n = chapterId.value
  router.push(
    n != null
      ? { path: `/book/${slug}/workbench`, query: { chapter: String(n) } }
      : `/book/${slug}/workbench`
  )
}

const goCastGraph = () => {
  const cid = chapterId.value
  router.push({ path: `/book/${slug}/cast`, query: cid == null ? {} : { chapter: String(cid) } })
}

const prevChapter = () => {
  const i = currentChapterIndex.value
  if (i > 0) router.push(`/book/${slug}/chapter/${chapterIds.value[i - 1]}`)
}

const nextChapter = () => {
  const i = currentChapterIndex.value
  if (i >= 0 && i < chapterIds.value.length - 1) {
    router.push(`/book/${slug}/chapter/${chapterIds.value[i + 1]}`)
  }
}

const onKeySave = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    void saveContent()
  }
}

const loadChapter = async () => {
  const cid = chapterId.value
  if (cid === null) {
    return
  }

  const [chaptersList, chapterData, rev, structureResult] = await Promise.allSettled([
    chapterApi.listChapters(slug),
    chapterApi.getChapter(slug, cid),
    chapterApi.getChapterReview(slug, cid),
    chapterApi.getChapterStructure(slug, cid)
  ])

  if (chaptersList.status === 'fulfilled') {
    chapterIds.value = chaptersList.value.map(c => c.number).sort((a, b) => a - b)
  } else {
    console.error('Failed to load chapter list:', chaptersList.reason)
  }

  if (chapterData.status === 'fulfilled') {
    content.value = chapterData.value.content || ''
    if (content.value) {
      createTime.value = new Date(chapterData.value.created_at).toLocaleString('zh-CN', { hour12: false })
      updateTime.value = new Date(chapterData.value.updated_at).toLocaleString('zh-CN', { hour12: false })
    }
    updatePreview(false)
  } else {
    console.error('Failed to load chapter:', chapterData.reason)
  }

  if (rev.status === 'fulfilled') {
    reviewStatus.value = statusToOld(rev.value.status)
    reviewMemo.value = rev.value.memo
  }

  if (structureResult.status === 'fulfilled') {
    chapterStructure.value = {
      word_count: structureResult.value.word_count,
      paragraph_count: structureResult.value.paragraph_count,
      dialogue_ratio: structureResult.value.dialogue_ratio,
      scene_count: structureResult.value.scene_count,
      pacing: structureResult.value.pacing,
    }
  } else {
    console.warn('Failed to load chapter structure:', structureResult.reason)
    chapterStructure.value = null
  }

  saveStatus.value = 'saved'
  await loadInferenceEvidence()
}

const loadInferenceEvidence = async () => {
  const cid = chapterId.value
  if (cid === null) return
  inferenceLoading.value = true
  inferenceHint.value = ''
  try {
    const res = await knowledgeGraphApi.getChapterInferenceEvidence(slug, cid)
    const d = res.data
    storyNodeId.value = d.story_node_id
    inferenceFacts.value = d.facts || []
    if (d.story_node_id) {
      inferenceHint.value = ''
    }
    if (d.hint) {
      inferenceHintTitle.value = '无结构节点'
      inferenceHint.value = d.hint
    } else if (!d.story_node_id) {
      inferenceHintTitle.value = '无结构节点'
      inferenceHint.value = '未匹配到故事结构中的章节节点，推断证据为空。'
    }
  } catch (e) {
    console.error('inference evidence', e)
    inferenceHintTitle.value = '加载失败'
    inferenceHint.value = '无法加载推断证据（请确认后端与 SQLite 可用）。'
    inferenceFacts.value = []
    storyNodeId.value = null
  } finally {
    inferenceLoading.value = false
  }
}

const revokeOneInference = (tripleId: string) => {
  dialog.warning({
    title: '撤销此条推断',
    content: '将删除该 chapter_inferred 三元组及其溯源，确定？',
    positiveText: '撤销',
    negativeText: '取消',
    onPositiveClick: async () => {
      revokingId.value = tripleId
      try {
        await knowledgeGraphApi.revokeInferredTriple(slug, tripleId)
        message.success('已撤销')
        await loadInferenceEvidence()
      } catch (err: unknown) {
        message.error(formatApiError(err, '撤销失败'))
      } finally {
        revokingId.value = null
      }
      return true
    },
  })
}

const revokeAllInference = async () => {
  const cid = chapterId.value
  if (cid === null) return
  revokeAllLoading.value = true
  try {
    const r = await knowledgeGraphApi.revokeChapterInference(slug, cid)
    message.success(
      `已处理：删除 ${r.data.deleted_inferred_facts} 条推断三元组（涉及 ${r.data.removed_provenance_triples} 条证据关联）`
    )
    await loadInferenceEvidence()
  } catch (err: unknown) {
    message.error(formatApiError(err, '撤销失败'))
  } finally {
    revokeAllLoading.value = false
  }
}

watch(
  () => route.params.id,
  async () => {
    if (route.name !== 'Chapter') return
    autosaveTask.cancel()
    previewTask.cancel()
    pageLoading.value = true
    try {
      await loadChapter()
    } catch (error) {
      console.error('Failed to load chapter:', error)
      message.error('加载章节失败')
    } finally {
      pageLoading.value = false
    }
  }
)

onMounted(async () => {
  window.addEventListener('keydown', onKeySave)
  try {
    await loadChapter()
  } catch (error) {
    console.error('Failed to load chapter:', error)
    message.error('加载章节失败')
  } finally {
    pageLoading.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeySave)
})
</script>

<style scoped>
.inf-prov-list {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  line-height: 1.5;
}

.chapter-spin {
  height: 100vh;
  min-height: 0;
}

.chapter-spin :deep(.n-spin-content) {
  min-height: 100%;
  height: 100%;
}

.chapter-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 8% 0%, var(--color-brand-light), transparent 28%),
    var(--app-page-bg);
}

.chapter-header {
  flex-shrink: 0;
  border-bottom: 1px solid var(--app-border);
  background:
    radial-gradient(circle at 78% -40%, rgba(79, 70, 229, 0.12), transparent 35%),
    var(--app-surface);
}

.chapter-header-shell {
  width: min(1400px, calc(100% - 48px));
  margin: 0 auto;
  padding-top: 18px;
}

.chapter-back {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--app-text-muted);
  font: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: color 160ms ease;
}

.chapter-back:hover {
  color: #4f46e5;
}

.chapter-back svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.chapter-heading-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  padding: 22px 0 16px;
}

.chapter-heading-copy {
  min-width: 0;
}

.chapter-eyebrow {
  display: block;
  margin-bottom: 8px;
  color: #4f46e5;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.chapter-heading-copy h1 {
  margin: 0;
  color: var(--app-text-primary);
  font-family: "Noto Serif SC", "Source Han Serif SC", Georgia, serif;
  font-size: clamp(28px, 3vw, 40px);
  font-weight: 800;
  letter-spacing: -0.045em;
  line-height: 1.12;
}

.chapter-heading-copy p {
  max-width: 680px;
  margin: 10px 0 0;
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.7;
}

.chapter-heading-actions {
  flex: 0 0 auto;
}

.chapter-status-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
}

.last-save-time {
  font-size: 12px;
  color: var(--app-text-muted);
}

.chapter-content {
  flex: 1;
  min-height: 0;
  padding: clamp(22px, 3vw, 38px);
}

.chapter-content :deep(.n-split) {
  height: 100%;
  min-height: 0;
}

.editor-card {
  height: 100%;
  min-height: 0;
  padding: 26px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 18px;
  box-shadow: var(--app-shadow-sm);
}

.editor-area {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.content-editor {
  flex: 1;
  min-height: 0;
  font-size: 16px;
  line-height: 1.85;
}

.content-editor :deep(textarea) {
  font-family: 'Source Han Serif SC', 'Noto Serif SC', Georgia, serif;
  line-height: 1.85;
}

.editor-footer {
  padding: 10px 0 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-slide-enter-active,
.preview-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.preview-slide-enter-from,
.preview-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.preview-panel {
  margin-top: 8px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--app-surface-subtle);
  border: 1px solid var(--app-border);
  max-height: 42vh;
  overflow: auto;
}

.preview-content {
  font-size: 14px;
}

.review-card {
  height: 100%;
  min-height: 0;
  padding: 26px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 18px;
  box-shadow: var(--app-shadow-sm);
  display: flex;
  flex-direction: column;
}

.review-tabs {
  flex: 1;
  min-height: 0;
}

.review-tabs :deep(.n-tab-pane) {
  padding-top: 12px;
}

.review-form {
  max-width: 100%;
}

.info-stats {
  padding: 8px 0;
}

.meta-line {
  font-size: 13px;
}

.meta-mono {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 12px;
  word-break: break-all;
}

.ico-tiny {
  font-size: 10px;
  opacity: 0.8;
}

@media (max-width: 760px) {
  .chapter-header-shell {
    width: min(100% - 28px, 1400px);
    padding-top: 14px;
  }

  .chapter-heading-row {
    align-items: flex-start;
    flex-direction: column;
    gap: 16px;
    padding: 18px 0 20px;
  }

  .chapter-heading-actions {
    width: 100%;
  }

  .chapter-content {
    padding: 16px;
  }

  .editor-card,
  .review-card {
    padding: 18px;
  }
}
</style>