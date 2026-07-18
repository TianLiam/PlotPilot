<template>
  <div class="pipeline-page">
    <div class="pipeline-header">
      <div class="header-inner">
        <div class="header-left">
          <h1 class="page-title">自动驾驶流水线</h1>
          <p class="page-subtitle">展示后端真实阶段、章节进度与审阅状态</p>
        </div>
        <div class="header-right">
          <n-space>
            <n-select
              v-model:value="selectedNovel"
              :options="novelOptions"
              placeholder="选择小说"
              style="width: 200px"
            />
            <n-button
              type="primary"
              size="large"
              :loading="actionLoading"
              :disabled="!selectedNovel || pipelineStatus === 'running' || pipelineStatus === 'paused'"
              @click="startPipeline"
            >
              <template #icon><n-icon><IconPlay /></n-icon></template>
              启动流水线
            </n-button>
          </n-space>
        </div>
      </div>
    </div>

    <div class="pipeline-content">
      <n-grid :cols="3" :x-gap="20" :y-gap="20" responsive="screen">
        <n-gi :span="2">
          <n-card :bordered="false" class="timeline-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">📊 执行进度</span>
                <n-space>
                  <span class="progress-text">已完成章节 {{ completedChapters }}/{{ targetChapters }}</span>
                  <n-button text size="small" :loading="statusLoading" @click="refreshStatus">刷新</n-button>
                </n-space>
              </div>
            </template>

            <div class="progress-bar-wrapper">
              <n-progress
                type="line"
                :percentage="totalProgress"
                :height="8"
                color="#4f46e5"
              />
            </div>

            <n-alert v-if="loadError" type="error" :show-icon="true" style="margin-bottom: 16px">
              {{ loadError }}
            </n-alert>

            <div class="timeline-container">
              <div
                v-for="(agent, idx) in agents"
                :key="agent.id"
                class="agent-item"
                :class="{
                  'is-completed': agent.status === 'completed',
                  'is-running': agent.status === 'running',
                  'is-paused': agent.status === 'paused',
                  'is-pending': agent.status === 'pending',
                  'is-failed': agent.status === 'failed',
                }"
              >
                <div class="agent-timeline">
                  <div class="timeline-dot">
                    <n-icon v-if="agent.status === 'completed'" :component="IconCheck" :size="14" />
                    <n-icon v-else-if="agent.status === 'running'" :component="IconLoader" :size="14" />
                    <n-icon v-else-if="agent.status === 'paused'" :component="IconPause" :size="14" />
                    <n-icon v-else-if="agent.status === 'failed'" :component="IconError" :size="14" />
                    <span v-else>{{ idx + 1 }}</span>
                  </div>
                  <div v-if="idx < agents.length - 1" class="timeline-line"></div>
                </div>

                <div class="agent-card">
                  <div class="agent-header">
                    <span class="agent-icon">{{ agent.icon }}</span>
                    <div class="agent-info">
                      <div class="agent-name">{{ agent.name }}</div>
                      <div class="agent-desc">{{ agent.description }}</div>
                    </div>
                    <div class="agent-status">
                      <n-tag :type="getStatusType(agent.status)" round>
                        {{ getStatusLabel(agent.status) }}
                      </n-tag>
                    </div>
                  </div>

                  <div v-if="agent.status === 'running'" class="agent-progress">
                    <n-progress
                      type="line"
                      :percentage="agent.progress"
                      :height="4"
                      :color="getProgressColor(agent.status)"
                    />
                    <span class="progress-num">{{ agent.progress }}%</span>
                  </div>

                  <div v-if="agent.output" class="agent-output">
                    <n-text strong class="output-label">输出结果：</n-text>
                    <p class="output-content">{{ agent.output }}</p>
                  </div>

                  <div v-if="agent.error" class="agent-error">
                    <n-icon :component="IconAlertCircle" :size="14" />
                    <span>{{ agent.error }}</span>
                  </div>

                </div>
              </div>
            </div>
          </n-card>
        </n-gi>

        <n-gi :span="1">
          <n-card :bordered="false" class="info-card">
            <template #header>📋 流水线信息</template>
            <n-descriptions :column="1" size="small">
              <n-descriptions-item label="当前状态">
                <n-tag :type="getPipelineStatusType(pipelineStatus)">
                  {{ getPipelineStatusLabel(pipelineStatus) }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="最后状态时间">
                {{ lastStatusTime || '尚未获取' }}
              </n-descriptions-item>
              <n-descriptions-item label="当前阶段">
                {{ currentStageLabel }}
              </n-descriptions-item>
              <n-descriptions-item label="当前小说">
                {{ selectedNovelTitle || '未选择' }}
              </n-descriptions-item>
            </n-descriptions>
          </n-card>

          <n-card :bordered="false" class="info-card">
            <template #header>🎯 阶段说明</template>
            <div class="agent-legend">
              <div class="legend-item">
                <span class="legend-dot completed"></span>
                <span>已完成</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot running"></span>
                <span>运行中</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot pending"></span>
                <span>等待中</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot failed"></span>
                <span>失败</span>
              </div>
            </div>
          </n-card>

          <n-card :bordered="false" class="info-card">
            <template #header>⚙️ 操作</template>
            <n-space vertical size="medium">
              <n-button size="small" :loading="actionLoading" @click="resumePipeline" :disabled="pipelineStatus !== 'paused'">
                <template #icon><n-icon><IconPlay /></n-icon></template>
                通过审阅并恢复
              </n-button>
              <n-button size="small" type="warning" :loading="actionLoading" @click="stopPipeline" :disabled="pipelineStatus === 'idle' || pipelineStatus === 'completed'">
                <template #icon><n-icon><IconStop /></n-icon></template>
                终止流水线
              </n-button>
              <n-button size="small" :loading="actionLoading" @click="resetCircuitBreaker" :disabled="pipelineStatus !== 'failed'">
                <template #icon><n-icon><IconRefresh /></n-icon></template>
                重置熔断
              </n-button>
              <n-button size="small" :loading="statusLoading" @click="refreshStatus" :disabled="!selectedNovel">
                <template #icon><n-icon><IconRefresh /></n-icon></template>
                刷新真实状态
              </n-button>
            </n-space>
          </n-card>
        </n-gi>
      </n-grid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { autopilotApi, isAutopilotNotFoundError, type AutopilotStatus } from '@/api/autopilot'
import { novelApi, type NovelDTO } from '@/api/novel'
import { toAutopilotDAGDisplayStatus } from '@/workbench/autopilotStatus'

type PipelineStatus = 'idle' | 'running' | 'paused' | 'completed' | 'failed'
type StageStatus = 'completed' | 'running' | 'paused' | 'pending' | 'failed'
type StageItem = {
  id: number
  key: string
  name: string
  icon: string
  description: string
  status: StageStatus
  progress: number
  output: string | null
  error: string | null
}

const message = useMessage()

const icon = (path: string, attrs: Record<string, unknown> = {}) => () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', ...attrs, d: path }))

const IconPlay = icon('M8 5v14l11-7z')
const IconPause = icon('M6 19h4V5H6v14zm8-14v14h4V5h-4z')
const IconStop = icon('M6 6h12v12H6z')
const IconCheck = icon('M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z')
const IconLoader = icon('M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z')
const IconError = icon('M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z')
const IconAlertCircle = IconError
const IconRefresh = icon('M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z')

const stageDefinitions = [
  { key: 'macro_planning', name: '宏观规划', icon: '🧭', description: '生成部、卷、幕的整体结构' },
  { key: 'act_planning', name: '幕级规划', icon: '🎵', description: '规划当前幕的章节链与承接' },
  { key: 'writing', name: '章节写作', icon: '✍️', description: '组装上下文并生成、落盘正文' },
  { key: 'auditing', name: '质量审计', icon: '🔍', description: '检查文风、张力、一致性与 Anti-AI' },
  { key: 'syncing', name: '数据同步', icon: '🔄', description: '同步章节状态、记忆和知识图谱' },
  { key: 'paused_for_review', name: '人工审阅', icon: '👀', description: '等待用户确认后继续下一阶段' },
  { key: 'completed', name: '全书完成', icon: '✅', description: '达到目标章节数并完成收尾' },
]

const selectedNovel = ref('')
const novels = ref<NovelDTO[]>([])
const status = ref<AutopilotStatus | null>(null)
const statusLoading = ref(false)
const actionLoading = ref(false)
const loadError = ref('')
const lastStatusTime = ref('')
let pollTimer: ReturnType<typeof setInterval> | null = null

const novelOptions = computed(() => novels.value.map(item => ({ label: item.title, value: item.id })))
const selectedNovelData = computed(() => novels.value.find(item => item.id === selectedNovel.value) ?? null)
const selectedNovelTitle = computed(() => selectedNovelData.value?.title ?? '')
const completedChapters = computed(() => Number(
  status.value?.completed_chapters ?? status.value?.current_auto_chapters ?? status.value?.manuscript_chapters ?? 0,
))
const targetChapters = computed(() => Math.max(1, Number(
  status.value?.target_chapters ?? selectedNovelData.value?.target_chapters ?? 1,
)))
const totalProgress = computed(() => Math.min(100, Math.round(
  (completedChapters.value / targetChapters.value) * 100,
)))

const pipelineStatus = computed<PipelineStatus>(() => {
  const display = toAutopilotDAGDisplayStatus(status.value)
  return display === 'error' ? 'failed' : display
})

function normalizedStage(raw: unknown): string {
  const value = String(raw ?? '').trim().toLowerCase()
  if (value === 'planning') return 'macro_planning'
  if (value === 'reviewing') return 'paused_for_review'
  return value || 'macro_planning'
}

const currentStageLabel = computed(() => {
  const current = normalizedStage(status.value?.current_stage)
  const stage = stageDefinitions.find(item => item.key === current)
  const substep = String(status.value?.writing_substep_label ?? '').trim()
  return substep || stage?.name || current
})

function statusErrorText(current: AutopilotStatus | null): string | null {
  if (!current) return null
  const raw = current.last_error ?? current.autopilot_recovery_reason
  if (!raw) return null
  if (typeof raw === 'string') return raw
  if (typeof raw === 'object' && raw && 'message' in raw) return String(raw.message || '') || null
  return String(raw)
}

function activeStageOutput(current: AutopilotStatus, stageKey: string): string | null {
  if (stageKey === 'writing') {
    const chapter = Number(current.current_chapter_number ?? completedChapters.value + 1)
    const substep = String(current.writing_substep_label ?? current.writing_substep ?? '').trim()
    const words = Number(current.accumulated_words ?? 0)
    return [`第 ${chapter} 章`, substep, words > 0 ? `已生成 ${words} 字` : ''].filter(Boolean).join(' · ')
  }
  if (stageKey === 'auditing') return String(current.audit_progress ?? '正在执行章节审计')
  if (stageKey === 'paused_for_review') return String(current.autopilot_pause_reason ?? '等待人工审阅')
  if (stageKey === 'act_planning') return `当前第 ${Number(current.current_act ?? 0) + 1} 幕`
  if (stageKey === 'syncing') return String(current.active_pipeline_step ?? '正在同步叙事状态')
  return null
}

const agents = computed<StageItem[]>(() => {
  const current = status.value
  const currentKey = normalizedStage(current?.current_stage)
  const activeIndex = Math.max(0, stageDefinitions.findIndex(item => item.key === currentKey))
  const isCompleted = pipelineStatus.value === 'completed' || currentKey === 'completed'
  const errorText = statusErrorText(current)

  return stageDefinitions.map((definition, index) => {
    let stageStatus: StageStatus = 'pending'
    if (isCompleted) stageStatus = 'completed'
    else if (index < activeIndex) stageStatus = 'completed'
    else if (index === activeIndex && pipelineStatus.value === 'running') stageStatus = 'running'
    else if (index === activeIndex && pipelineStatus.value === 'paused') stageStatus = 'paused'
    else if (index === activeIndex && pipelineStatus.value === 'failed') stageStatus = 'failed'

    let progress = stageStatus === 'completed' ? 100 : 0
    if (stageStatus === 'running' || stageStatus === 'paused') {
      if (definition.key === 'writing') {
        const words = Number(current?.accumulated_words ?? 0)
        const target = Number(current?.chapter_target_words ?? selectedNovelData.value?.target_words_per_chapter ?? 2500)
        progress = target > 0 ? Math.min(99, Math.round((words / target) * 100)) : 0
      } else {
        progress = 50
      }
    }

    return {
      id: index + 1,
      ...definition,
      status: stageStatus,
      progress,
      output: current && index === activeIndex ? activeStageOutput(current, definition.key) : null,
      error: stageStatus === 'failed' ? errorText || '自动驾驶已进入错误状态' : null,
    }
  })
})

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

async function loadStatus(silent = false) {
  if (!selectedNovel.value) {
    status.value = null
    return
  }
  if (!silent) statusLoading.value = true
  try {
    status.value = await autopilotApi.getStatus(selectedNovel.value)
    loadError.value = ''
    lastStatusTime.value = new Date().toLocaleString()
  } catch (error) {
    if (isAutopilotNotFoundError(error)) {
      status.value = null
      loadError.value = '该小说尚未加载到自动驾驶运行态，可直接点击“启动流水线”。'
    } else {
      loadError.value = `读取自动驾驶状态失败：${errorMessage(error)}`
    }
  } finally {
    if (!silent) statusLoading.value = false
  }
}

async function refreshStatus() {
  await loadStatus(false)
}

async function startPipeline() {
  const novel = selectedNovelData.value
  if (!novel) {
    message.warning('请先选择小说')
    return
  }
  actionLoading.value = true
  try {
    await autopilotApi.start(novel.id, {
      max_auto_chapters: 9999,
      target_chapters: Math.max(1, novel.target_chapters),
      target_words_per_chapter: novel.target_words_per_chapter ?? 2500,
    })
    await loadStatus(true)
    message.success('自动驾驶流水线已启动')
  } catch (error) {
    message.error(`启动失败：${errorMessage(error)}`)
  } finally {
    actionLoading.value = false
  }
}

async function resumePipeline() {
  if (!selectedNovel.value) return
  actionLoading.value = true
  try {
    await autopilotApi.resume(selectedNovel.value)
    await loadStatus(true)
    message.success('已通过审阅并恢复自动驾驶')
  } catch (error) {
    message.error(`恢复失败：${errorMessage(error)}`)
  } finally {
    actionLoading.value = false
  }
}

async function stopPipeline() {
  if (!selectedNovel.value) return
  actionLoading.value = true
  try {
    await autopilotApi.stop(selectedNovel.value)
    await loadStatus(true)
    message.info('自动驾驶已终止')
  } catch (error) {
    message.error(`终止失败：${errorMessage(error)}`)
  } finally {
    actionLoading.value = false
  }
}

async function resetCircuitBreaker() {
  if (!selectedNovel.value) return
  actionLoading.value = true
  try {
    await autopilotApi.resetCircuitBreaker(selectedNovel.value)
    await loadStatus(true)
    message.success('熔断计数已重置，请确认状态后重新启动')
  } catch (error) {
    message.error(`重置失败：${errorMessage(error)}`)
  } finally {
    actionLoading.value = false
  }
}

function getStatusType(stageStatus: StageStatus) {
  return ({ completed: 'success', running: 'primary', paused: 'warning', pending: 'default', failed: 'error' } as const)[stageStatus]
}

function getStatusLabel(stageStatus: StageStatus) {
  return ({ completed: '已通过', running: '运行中', paused: '待审阅', pending: '等待中', failed: '失败' } as const)[stageStatus]
}

function getProgressColor(stageStatus: StageStatus) {
  return ({ completed: '#10b981', running: '#4f46e5', paused: '#f59e0b', pending: '#94a3b8', failed: '#ef4444' } as const)[stageStatus]
}

function getPipelineStatusType(value: PipelineStatus) {
  return ({ idle: 'default', running: 'primary', paused: 'warning', completed: 'success', failed: 'error' } as const)[value]
}

function getPipelineStatusLabel(value: PipelineStatus) {
  return ({ idle: '空闲', running: '运行中', paused: '待审阅', completed: '已完成', failed: '失败' } as const)[value]
}

watch(selectedNovel, () => { void loadStatus(false) })

onMounted(async () => {
  statusLoading.value = true
  try {
    novels.value = await novelApi.listNovels()
    if (novels.value.length > 0) selectedNovel.value = novels.value[0].id
  } catch (error) {
    loadError.value = `加载小说列表失败：${errorMessage(error)}`
  } finally {
    statusLoading.value = false
  }
  pollTimer = setInterval(() => { void loadStatus(true) }, 4000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.pipeline-page {
  min-height: calc(100vh - 60px);
  background: var(--app-page-bg);
}

.pipeline-header {
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  padding: 0 24px;
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 0 16px;
}

.page-title {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  color: var(--app-text-primary);
  letter-spacing: -0.02em;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--app-text-muted);
}

.pipeline-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.timeline-card {
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.progress-text {
  font-size: 13px;
  color: var(--app-text-secondary);
}

.progress-bar-wrapper {
  padding: 8px 0 16px;
}

.timeline-container {
  padding-left: 4px;
}

.agent-item {
  display: flex;
  gap: 12px;
  padding-bottom: 4px;
}

.agent-timeline {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
  flex-shrink: 0;
}

.timeline-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--app-surface-subtle);
  color: var(--app-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  z-index: 1;
}

.agent-item.is-completed .timeline-dot {
  background: #10b981;
  color: #fff;
}

.agent-item.is-running .timeline-dot {
  background: var(--color-brand);
  color: #fff;
  animation: pulse 1.5s infinite;
}

.agent-item.is-paused .timeline-dot {
  background: #f59e0b;
  color: #fff;
}

.agent-item.is-failed .timeline-dot {
  background: #ef4444;
  color: #fff;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(79, 70, 229, 0); }
  100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }
}

.timeline-line {
  width: 2px;
  flex: 1;
  min-height: 40px;
  background: var(--app-border);
  margin-top: 4px;
}

.agent-item.is-completed .timeline-line {
  background: #10b981;
}

.agent-card {
  flex: 1;
  background: var(--app-surface-subtle);
  border-radius: 10px;
  padding: 14px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.agent-item.is-completed .agent-card {
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(16, 185, 129, 0.04);
}

.agent-item.is-running .agent-card {
  border-color: rgba(79, 70, 229, 0.3);
  background: rgba(79, 70, 229, 0.04);
}

.agent-item.is-paused .agent-card {
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.04);
}

.agent-item.is-failed .agent-card {
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.04);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.agent-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--app-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.agent-desc {
  font-size: 12px;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.agent-status {
  flex-shrink: 0;
}

.agent-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.progress-num {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-brand);
  min-width: 36px;
  text-align: right;
}

.agent-output {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--app-border);
}

.output-label {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.output-content {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--app-text-primary);
  line-height: 1.5;
}

.agent-error {
  margin-top: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.agent-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.info-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.info-card :deep(.n-card-header) {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.agent-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--app-text-secondary);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-dot.completed { background: #10b981; }
.legend-dot.running { background: var(--color-brand); }
.legend-dot.pending { background: #cbd5e1; }
.legend-dot.failed { background: #ef4444; }

@media (max-width: 900px) {
  .pipeline-content {
    padding: 16px;
  }
}
</style>
