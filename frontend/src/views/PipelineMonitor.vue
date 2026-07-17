<template>
  <div class="pipeline-page">
    <div class="pipeline-header">
      <div class="header-inner">
        <div class="header-left">
          <h1 class="page-title">多 Agent 流水线</h1>
          <p class="page-subtitle">9 个 AI Agent 协同完成全流程创作</p>
        </div>
        <div class="header-right">
          <n-space>
            <n-select
              v-model:value="selectedNovel"
              :options="novelOptions"
              placeholder="选择小说"
              style="width: 200px"
            />
            <n-button type="primary" size="large" @click="startPipeline">
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
                  <span class="progress-text">{{ completedCount }}/{{ agents.length }} 完成</span>
                  <n-button text size="small" @click="refreshStatus">刷新</n-button>
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

            <div class="timeline-container">
              <div
                v-for="(agent, idx) in agents"
                :key="agent.id"
                class="agent-item"
                :class="{
                  'is-completed': agent.status === 'completed',
                  'is-running': agent.status === 'running',
                  'is-pending': agent.status === 'pending',
                  'is-failed': agent.status === 'failed',
                }"
              >
                <div class="agent-timeline">
                  <div class="timeline-dot">
                    <n-icon v-if="agent.status === 'completed'" :component="IconCheck" :size="14" />
                    <n-icon v-else-if="agent.status === 'running'" :component="IconLoader" :size="14" />
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

                  <div class="agent-actions">
                    <n-button
                      v-if="agent.status === 'failed'"
                      size="small"
                      type="primary"
                      @click="retryAgent(agent.id)"
                    >
                      <template #icon><n-icon><IconRefresh /></n-icon></template>
                      重试
                    </n-button>
                    <n-button
                      v-if="agent.status === 'completed'"
                      size="small"
                      text
                      @click="viewDetail(agent.id)"
                    >
                      查看详情
                    </n-button>
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
              <n-descriptions-item label="开始时间">
                {{ startTime || '未开始' }}
              </n-descriptions-item>
              <n-descriptions-item label="预计剩余时间">
                {{ estimatedTime }}
              </n-descriptions-item>
              <n-descriptions-item label="当前小说">
                {{ selectedNovel || '未选择' }}
              </n-descriptions-item>
            </n-descriptions>
          </n-card>

          <n-card :bordered="false" class="info-card">
            <template #header>🎯 Agent 说明</template>
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
              <n-button size="small" @click="pausePipeline" :disabled="pipelineStatus === 'paused'">
                <template #icon><n-icon><IconPause /></n-icon></template>
                暂停流水线
              </n-button>
              <n-button size="small" @click="resumePipeline" :disabled="pipelineStatus !== 'paused'">
                <template #icon><n-icon><IconPlay /></n-icon></template>
                恢复流水线
              </n-button>
              <n-button size="small" type="warning" @click="stopPipeline" :disabled="pipelineStatus === 'idle'">
                <template #icon><n-icon><IconStop /></n-icon></template>
                终止流水线
              </n-button>
              <n-button size="small" @click="clearPipeline">
                <template #icon><n-icon><IconTrash /></n-icon></template>
                清空记录
              </n-button>
            </n-space>
          </n-card>
        </n-gi>
      </n-grid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { NIcon, useMessage } from 'naive-ui'

const message = useMessage()

const IconPlay = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M8 5v14l11-7z' }))

const IconPause = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M6 19h4V5H6v14zm8-14v14h4V5h-4z' }))

const IconStop = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M6 6h12v12H6z' }))

const IconCheck = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' }))

const IconLoader = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'none', stroke: 'currentColor', strokeWidth: '2', d: 'M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z' }))

const IconError = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z' }))

const IconAlertCircle = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z' }))

const IconRefresh = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z' }))

const IconTrash = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z' }))

const selectedNovel = ref('')
const novelOptions = [
  { label: '都市签到流测试', value: 'test-1' },
  { label: '玄幻无敌流测试', value: 'test-2' },
]

const pipelineStatus = ref('idle')
const startTime = ref('')
const estimatedTime = ref('5 分钟')

const agents = ref([
  { id: 1, name: '扫榜 Agent', icon: '📡', description: '扫描各大平台热门榜单', status: 'completed', progress: 100, output: '已扫描番茄、起点、七猫等平台榜单，发现都市签到流持续走热', error: null },
  { id: 2, name: '趋势分析 Agent', icon: '📈', description: '分析题材趋势和热度变化', status: 'completed', progress: 100, output: '都市签到流热度指数上涨 28%，推荐作为选题方向', error: null },
  { id: 3, name: '题材策划 Agent', icon: '💡', description: '策划具体题材和金手指', status: 'running', progress: 67, output: null, error: null },
  { id: 4, name: '人物设计 Agent', icon: '👤', description: '设计人物角色和关系', status: 'pending', progress: 0, output: null, error: null },
  { id: 5, name: '世界观设计 Agent', icon: '🌍', description: '构建世界观和规则体系', status: 'pending', progress: 0, output: null, error: null },
  { id: 6, name: '节奏规划 Agent', icon: '🎵', description: '规划全书节奏和节拍', status: 'pending', progress: 0, output: null, error: null },
  { id: 7, name: '章节写作 Agent', icon: '✍️', description: '逐章创作正文内容', status: 'pending', progress: 0, output: null, error: null },
  { id: 8, name: '质量检测 Agent', icon: '🔍', description: '检测行文质量和一致性', status: 'pending', progress: 0, output: null, error: null },
  { id: 9, name: '修文 Agent', icon: '✨', description: '优化文风降低AI痕迹', status: 'pending', progress: 0, output: null, error: null },
])

const completedCount = computed(() => agents.value.filter(a => a.status === 'completed').length)
const totalProgress = computed(() => Math.round((completedCount.value / agents.value.length) * 100))

function getStatusType(status: string) {
  const map: Record<string, string> = {
    completed: 'success',
    running: 'primary',
    pending: 'default',
    failed: 'error',
  }
  return map[status] || 'default'
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    completed: '已完成',
    running: '运行中',
    pending: '等待中',
    failed: '失败',
  }
  return map[status] || '未知'
}

function getProgressColor(status: string) {
  const map: Record<string, string> = {
    completed: '#10b981',
    running: '#4f46e5',
    pending: '#94a3b8',
    failed: '#ef4444',
  }
  return map[status] || '#4f46e5'
}

function getPipelineStatusType(status: string) {
  const map: Record<string, string> = {
    idle: 'default',
    running: 'primary',
    paused: 'warning',
    completed: 'success',
    failed: 'error',
  }
  return map[status] || 'default'
}

function getPipelineStatusLabel(status: string) {
  const map: Record<string, string> = {
    idle: '空闲',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || '未知'
}

function startPipeline() {
  if (!selectedNovel.value) {
    message.warning('请先选择小说')
    return
  }
  pipelineStatus.value = 'running'
  startTime.value = new Date().toLocaleString()
  message.success('流水线已启动')
}

function pausePipeline() {
  pipelineStatus.value = 'paused'
  message.info('流水线已暂停')
}

function resumePipeline() {
  pipelineStatus.value = 'running'
  message.info('流水线已恢复')
}

function stopPipeline() {
  pipelineStatus.value = 'idle'
  agents.value.forEach(a => {
    if (a.status === 'running') a.status = 'pending'
    a.progress = 0
  })
  message.info('流水线已终止')
}

function clearPipeline() {
  pipelineStatus.value = 'idle'
  startTime.value = ''
  agents.value.forEach(a => {
    a.status = 'pending'
    a.progress = 0
    a.output = null
    a.error = null
  })
  message.info('记录已清空')
}

function refreshStatus() {
  message.info('已刷新')
}

function retryAgent(id: number) {
  const agent = agents.value.find(a => a.id === id)
  if (agent) {
    agent.status = 'running'
    agent.progress = 0
    agent.error = null
    message.success(`${agent.name} 已重试`)
  }
}

function viewDetail(id: number) {
  const agent = agents.value.find(a => a.id === id)
  if (agent) {
    message.info(`${agent.name} 详情已展开`)
  }
}
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
