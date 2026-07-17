<template>
  <div class="studio-page">
    <div class="page-header">
      <div>
        <span class="page-eyebrow">Writing workflow</span>
        <h1 class="page-title">创作工坊</h1>
        <p class="page-subtitle">把选题、设定、结构、写作与审校串成一条可持续推进的工作流。</p>
      </div>
    </div>

    <div v-if="!selectedNovel" class="select-novel">
      <div class="select-card">
        <div class="select-copy">
          <span class="select-kicker">Start with a project</span>
          <h2>先确定一部作品，<br>再让每一步创作都有上下文。</h2>
          <p>创作工坊会根据作品当前阶段，组织选题研究、角色设定、世界观、节奏规划、章节写作和质量校验。</p>
          <div class="select-actions">
            <n-button type="primary" size="large" @click="goLibrary">从作品库选择</n-button>
            <n-button size="large" @click="goCreate">新建作品</n-button>
          </div>
        </div>
        <div class="workflow-preview" aria-label="创作流程预览">
          <div v-for="(label, index) in workflowPreview" :key="label" class="workflow-preview-item">
            <span class="workflow-index">{{ String(index + 1).padStart(2, '0') }}</span>
            <strong>{{ label }}</strong>
            <i v-if="index < workflowPreview.length - 1" />
          </div>
        </div>
      </div>
    </div>

    <div v-else class="studio-content">
      <div class="studio-sidebar">
        <div class="novel-selector" @click="showNovelList = true">
          <div class="novel-info">
            <div class="novel-cover-mini">{{ selectedNovel.title.charAt(0) }}</div>
            <div>
              <div class="novel-name">{{ selectedNovel.title }}</div>
              <div class="novel-stage">{{ selectedNovel.stage_label }}</div>
            </div>
          </div>
          <n-icon :component="IconChevronDown" :size="16" />
        </div>

        <div class="roadmap-title">创作路线图</div>

        <div class="roadmap-steps">
          <div
            v-for="(step, idx) in roadmapSteps"
            :key="step.key"
            class="roadmap-step"
            :class="{
              'is-active': activeStep === step.key,
              'is-done': step.status === 'done',
              'is-current': step.status === 'current',
              'is-pending': step.status === 'pending',
            }"
            @click="goStep(step)"
          >
            <div class="step-indicator">
              <span v-if="step.status === 'done'" class="step-dot step-dot-done">✓</span>
              <span v-else class="step-dot">{{ idx + 1 }}</span>
            </div>
            <div class="step-content">
              <div class="step-title">{{ step.title }}</div>
              <div class="step-desc">{{ step.desc }}</div>
            </div>
            <div v-if="idx < roadmapSteps.length - 1" class="step-line"></div>
          </div>
        </div>
      </div>

      <div class="studio-main">
        <div class="step-header">
          <h2 class="step-title-main">{{ currentStepInfo.title }}</h2>
          <p class="step-desc-main">{{ currentStepInfo.desc }}</p>
        </div>

        <div class="step-actions">
          <n-button
            v-if="currentStepIndex > 0"
            size="medium"
            @click="prevStep"
          >
            上一步
          </n-button>
          <n-button
            v-if="currentStepIndex < roadmapSteps.length - 1"
            type="primary"
            size="medium"
            @click="nextStep"
          >
            下一步
          </n-button>
        </div>

        <div class="step-content-area">
          <n-alert v-if="currentStepInfo.todo" type="info" :show-icon="true" style="margin-bottom: 16px">
            <template #title>本阶段目标</template>
            {{ currentStepInfo.todo }}
          </n-alert>

          <div class="step-tools">
            <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen">
              <n-gi v-for="tool in currentStepInfo.tools" :key="tool.name">
                <div class="tool-card" @click="(tool as any).action ? (tool as any).action() : goWorkbench()">
                  <div class="tool-icon">{{ tool.name.slice(0, 1) }}</div>
                  <div class="tool-name">{{ tool.name }}</div>
                  <div class="tool-desc">{{ tool.desc }}</div>
                  <n-button text type="primary" size="small" class="tool-btn">
                    {{ tool.actionLabel || '进入' }} →
                  </n-button>
                </div>
              </n-gi>
            </n-grid>
          </div>
        </div>
      </div>
    </div>

    <n-modal v-model:show="showNovelList" preset="card" title="选择小说" :style="{ width: '520px' }">
      <div class="novel-picker-list">
        <div
          v-for="novel in novels"
          :key="novel.slug"
          class="novel-picker-item"
          :class="{ 'is-selected': selectedNovel?.slug === novel.slug }"
          @click="selectNovel(novel)"
        >
          <div class="picker-cover">{{ novel.title.charAt(0) }}</div>
          <div class="picker-info">
            <div class="picker-title">{{ novel.title }}</div>
            <div class="picker-meta">
              <n-tag :type="getStageType(novel.stage)" size="small" round borderable>
                {{ novel.stage_label }}
              </n-tag>
              <span>{{ novel.chapter_count }} 章 · {{ formatWordCount(novel.word_count || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon, useMessage } from 'naive-ui'
import { novelApi, type NovelDTO } from '../api/novel'
import {
  getNovelStageLabel,
  getNovelStageTagType,
} from '@/domain/novel'

const router = useRouter()
const route = useRoute()
const message = useMessage()

const IconChevronDown = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z' }))

const novels = ref<any[]>([])
const selectedNovel = ref<any>(null)
const activeStep = ref('planning')
const showNovelList = ref(false)
const workflowPreview = ['选题策划', '人物设计', '世界观', '节奏规划', '章节写作', '质量检测']

const roadmapSteps = [
  {
    key: 'planning', title: '选题策划', desc: '确定题材与金手指', status: 'done', icon: '💡',
    todo: '完成题材研究，确定核心梗和金手指设计',
    tools: [
      { name: '题材研究', desc: '分析题材成功率与趋势', icon: '🔬', actionLabel: '去研究', action: () => router.push('/market/research') },
      { name: '趋势大盘', desc: '查看市场热门趋势', icon: '📈', actionLabel: '去查看', action: () => router.push('/market/trends') },
      { name: '爆款拆书', desc: '拆解热门小说套路', icon: '🧬', actionLabel: '去拆书', action: () => router.push('/market/deconstruction') },
      { name: 'DNA模板库', desc: '复用爆款基因模板', icon: '🧪', actionLabel: '去浏览', action: () => router.push('/market') },
    ],
  },
  {
    key: 'character', title: '人物设计', desc: '主角团与反派设定', status: 'current', icon: '👤',
    todo: '设计主角、配角、反派的人物档案和关系网',
    tools: [
      { name: '人物档案', desc: '创建/编辑人物设定', icon: '👤', actionLabel: '去编辑' },
      { name: '人物关系图', desc: '可视化人物关系网络', icon: '🕸️', actionLabel: '去查看' },
      { name: '对话生成', desc: 'AI辅助生成人物对话', icon: '💬', actionLabel: '去生成' },
    ],
  },
  {
    key: 'worldview', title: '世界观', desc: '设定与规则体系', status: 'pending', icon: '🌍',
    todo: '构建完整的世界观设定和力量体系',
    tools: [
      { name: '世界设定', desc: '编辑世界观与规则', icon: '🌍', actionLabel: '去编辑' },
      { name: '地点图谱', desc: '地图与场景管理', icon: '🗺️', actionLabel: '去查看' },
      { name: '道具管理', desc: '法宝、道具设定', icon: '⚔️', actionLabel: '去管理' },
    ],
  },
  {
    key: 'pacing', title: '节奏规划', desc: '大纲与节拍表', status: 'pending', icon: '📊',
    todo: '制定全书大纲、幕次结构和章节节拍',
    tools: [
      { name: '大纲规划', desc: '宏观结构与大纲', icon: '📋', actionLabel: '去规划' },
      { name: '幕次管理', desc: '分幕与转折点设计', icon: '🎭', actionLabel: '去管理' },
      { name: '节拍表', desc: '章节节拍与节奏控制', icon: '🥁', actionLabel: '去编排' },
    ],
  },
  {
    key: 'writing', title: '章节写作', desc: '正文创作', status: 'pending', icon: '✍️',
    todo: '按节奏规划逐章创作正文内容',
    tools: [
      { name: '章节列表', desc: '查看与管理所有章节', icon: '📄', actionLabel: '去写作' },
      { name: 'AI续写', desc: 'AI辅助生成正文', icon: '🤖', actionLabel: '去生成' },
      { name: '伏笔系统', desc: '管理伏笔与回收', icon: '🪝', actionLabel: '去管理' },
      { name: '知识图谱', desc: '维护故事一致性', icon: '🧠', actionLabel: '去维护' },
    ],
  },
  {
    key: 'quality', title: '质量检测', desc: '审校与优化', status: 'pending', icon: '✅',
    todo: '检查行文质量、一致性和AI痕迹',
    tools: [
      { name: '文风检测', desc: '检测文风一致性', icon: '📝', actionLabel: '去检测' },
      { name: 'AI痕迹检测', desc: '降低AI痕迹', icon: '🔍', actionLabel: '去检测' },
      { name: '一致性检查', desc: '人物/设定一致性', icon: '✅', actionLabel: '去检查' },
    ],
  },
]

const currentStepIndex = computed(() =>
  roadmapSteps.findIndex(s => s.key === activeStep.value)
)

const currentStepInfo = computed(() =>
  roadmapSteps.find(s => s.key === activeStep.value) || roadmapSteps[0]
)

const fetchNovels = async () => {
  try {
    const data = await novelApi.listNovels()
    novels.value = data.map((novel: NovelDTO) => ({
      slug: novel.id,
      title: novel.title,
      stage: novel.stage,
      stage_label: getNovelStageLabel(novel.stage),
      chapter_count: novel.chapters?.length || 0,
      word_count: novel.total_word_count,
    }))

    if (novels.value.length > 0) {
      const defaultNovel = novels.value[0]
      selectedNovel.value = defaultNovel

      const stageMap: Record<string, string> = {
        planning: 'planning',
        writing: 'writing',
        reviewing: 'quality',
        completed: 'quality',
      }
      activeStep.value = stageMap[defaultNovel.stage] || 'planning'
      updateStepStatuses()
    }
  } catch {
    // ignore
  }
}

const updateStepStatuses = () => {
  const idx = currentStepIndex.value
  roadmapSteps.forEach((step, i) => {
    if (i < idx) step.status = 'done'
    else if (i === idx) step.status = 'current'
    else step.status = 'pending'
  })
}

const selectNovel = (novel: any) => {
  selectedNovel.value = novel
  showNovelList.value = false

  const stageMap: Record<string, string> = {
    planning: 'planning',
    writing: 'writing',
    reviewing: 'quality',
    completed: 'quality',
  }
  activeStep.value = stageMap[novel.stage] || 'planning'
  updateStepStatuses()
}

const goStep = (step: any) => {
  activeStep.value = step.key
  updateStepStatuses()
}

const prevStep = () => {
  const idx = currentStepIndex.value
  if (idx > 0) {
    activeStep.value = roadmapSteps[idx - 1].key
    updateStepStatuses()
  }
}

const nextStep = () => {
  const idx = currentStepIndex.value
  if (idx < roadmapSteps.length - 1) {
    activeStep.value = roadmapSteps[idx + 1].key
    updateStepStatuses()
  }
}

const formatWordCount = (count: number): string => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万字'
  }
  return count + '字'
}

const getStageType = (stage: string) => getNovelStageTagType(stage)

const goLibrary = () => {
  router.push('/library')
}

const goCreate = () => {
  router.push('/home')
}

const goWorkbench = () => {
  if (selectedNovel.value) {
    router.push(`/book/${selectedNovel.value.slug}/workbench`)
  }
}

onMounted(() => {
  fetchNovels()
})
</script>

<style scoped>
.studio-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 20px;
  flex-shrink: 0;
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

.select-novel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.select-card {
  text-align: center;
  padding: 48px;
  background: var(--app-surface);
  border-radius: 16px;
  border: 1px solid var(--app-border);
}

.select-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.select-card h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--app-text-primary);
}

.select-card p {
  margin: 0 0 20px;
  color: var(--app-text-muted);
  font-size: 14px;
}

.studio-content {
  flex: 1;
  display: flex;
  gap: 20px;
  min-height: 0;
}

.studio-sidebar {
  width: 280px;
  flex-shrink: 0;
  background: var(--app-surface);
  border-radius: 14px;
  border: 1px solid var(--app-border);
  padding: 16px;
  overflow-y: auto;
}

.novel-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 10px;
  background: var(--app-surface-subtle);
  cursor: pointer;
  margin-bottom: 20px;
  transition: all 0.2s ease;
}

.novel-selector:hover {
  background: var(--color-brand-light);
}

.novel-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.novel-cover-mini {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}

.novel-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.novel-stage {
  font-size: 12px;
  color: var(--app-text-muted);
}

.roadmap-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text-secondary);
  margin-bottom: 12px;
  padding: 0 4px;
}

.roadmap-steps {
  position: relative;
}

.roadmap-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.roadmap-step:hover {
  background: var(--app-surface-subtle);
}

.roadmap-step.is-active {
  background: var(--color-brand-light);
}

.step-indicator {
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.step-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--app-surface-subtle);
  color: var(--app-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.step-dot-done {
  background: #10b981;
  color: #fff;
}

.roadmap-step.is-current .step-dot {
  background: var(--color-brand);
  color: #fff;
  box-shadow: 0 0 0 4px var(--color-brand-light);
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin-bottom: 2px;
}

.roadmap-step.is-pending .step-title {
  color: var(--app-text-muted);
}

.step-desc {
  font-size: 12px;
  color: var(--app-text-muted);
}

.step-line {
  position: absolute;
  left: 22px;
  top: 38px;
  width: 2px;
  height: calc(100% - 10px);
  background: var(--app-border);
  z-index: 0;
}

.roadmap-step.is-done .step-line {
  background: #10b981;
}

.studio-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--app-surface);
  border-radius: 14px;
  border: 1px solid var(--app-border);
  padding: 24px;
  overflow-y: auto;
}

.step-header {
  margin-bottom: 16px;
}

.step-title-main {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text-primary);
}

.step-desc-main {
  margin: 0;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.step-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--app-border);
}

.step-content-area {
  flex: 1;
}

.step-tools {
  padding: 8px 0;
}

.tool-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 24px 16px;
  border-radius: 12px;
  background: var(--app-surface-subtle);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 100%;
}

.tool-card:hover {
  background: var(--color-brand-light);
  border-color: var(--color-brand-border);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.08);
}

.tool-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  border-radius: 14px;
  background: var(--app-surface);
  margin-bottom: 12px;
}

.tool-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin-bottom: 4px;
}

.tool-desc {
  font-size: 12px;
  color: var(--app-text-muted);
  line-height: 1.5;
  margin-bottom: 10px;
}

.novel-picker-list {
  max-height: 400px;
  overflow-y: auto;
}

.novel-picker-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-bottom: 4px;
}

.novel-picker-item:hover {
  background: var(--app-surface-subtle);
}

.novel-picker-item.is-selected {
  background: var(--color-brand-light);
}

.picker-cover {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.picker-info {
  flex: 1;
  min-width: 0;
}

.picker-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.picker-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--app-text-muted);
}

@media (max-width: 900px) {
  .studio-page {
    padding: 16px;
    height: auto;
    min-height: calc(100vh - 60px);
  }

  .studio-content {
    flex-direction: column;
  }

  .studio-sidebar {
    width: 100%;
    max-height: none;
  }

  .roadmap-steps {
    display: flex;
    overflow-x: auto;
    gap: 8px;
  }

  .roadmap-step {
    flex-shrink: 0;
    width: 100px;
    flex-direction: column;
    text-align: center;
    gap: 6px;
  }

  .step-line {
    display: none;
  }
}

/* Match the calmer editorial language used by the overview. */
.studio-page {
  max-width: 1440px;
  height: calc(100vh - 68px);
  padding: clamp(22px, 3vw, 38px);
  background:
    radial-gradient(circle at 8% 0%, var(--color-brand-light), transparent 28%),
    var(--app-page-bg);
}

.page-header {
  margin-bottom: 24px;
}

.page-eyebrow,
.select-kicker {
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
  max-width: 680px;
  font-size: 13px;
  line-height: 1.65;
}

.select-novel {
  align-items: flex-start;
}

.select-card {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  width: 100%;
  min-height: 430px;
  padding: 0;
  overflow: hidden;
  text-align: left;
  background: var(--app-surface);
  border-radius: 22px;
  box-shadow: var(--app-shadow-md);
}

.select-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: clamp(34px, 5vw, 66px);
}

.select-copy h2 {
  margin: 0;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: clamp(30px, 3.5vw, 44px);
  font-weight: 680;
  line-height: 1.26;
  letter-spacing: -0.035em;
}

.select-copy p {
  max-width: 620px;
  margin: 20px 0 0;
  color: var(--app-text-secondary);
  font-size: 13px;
  line-height: 1.8;
}

.select-actions {
  display: flex;
  gap: 10px;
  margin-top: 28px;
}

.workflow-preview {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 38px;
  color: #f7f8fc;
  background:
    radial-gradient(circle at 90% 10%, color-mix(in srgb, var(--color-brand) 42%, transparent), transparent 42%),
    linear-gradient(150deg, #20283c, #111827 72%);
}

.workflow-preview-item {
  position: relative;
  display: grid;
  grid-template-columns: 38px 1fr;
  align-items: center;
  min-height: 53px;
  gap: 12px;
}

.workflow-preview-item i {
  position: absolute;
  top: 36px;
  bottom: -17px;
  left: 14px;
  width: 1px;
  background: rgba(255, 255, 255, 0.15);
}

.workflow-index {
  display: grid;
  z-index: 1;
  width: 28px;
  height: 28px;
  place-items: center;
  color: rgba(255, 255, 255, 0.68);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 9px;
}

.workflow-preview-item strong {
  font-size: 13px;
  font-weight: 600;
}

.studio-sidebar,
.studio-main {
  border-radius: 18px;
  box-shadow: var(--app-shadow-sm);
}

.tool-card {
  align-items: flex-start;
  padding: 20px;
  text-align: left;
}

.tool-icon {
  width: 42px;
  height: 42px;
  color: var(--color-brand);
  background: var(--color-brand-light);
  border: 1px solid var(--color-brand-border);
  border-radius: 11px;
  font-family: var(--font-serif);
  font-size: 16px;
}

@media (max-width: 900px) {
  .studio-page {
    height: auto;
  }

  .select-card {
    grid-template-columns: 1fr;
  }

  .workflow-preview {
    min-height: 340px;
  }
}

@media (max-width: 560px) {
  .studio-page {
    padding: 16px;
  }

  .select-copy,
  .workflow-preview {
    padding: 24px;
  }

  .select-actions {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
