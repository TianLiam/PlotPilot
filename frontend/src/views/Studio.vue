<template>
  <div class="studio-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">创作工坊</h1>
        <p class="page-subtitle">系统化地完成你的小说创作</p>
      </div>
    </div>

    <div v-if="!selectedNovel" class="select-novel">
      <div class="select-card">
        <span class="select-icon">📖</span>
        <h3>选择一本小说开始创作</h3>
        <p>从书架中选择你要继续创作的小说</p>
        <n-button type="primary" size="large" round @click="goLibrary">
          前往书架
        </n-button>
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

          <div class="step-placeholder">
            <span class="placeholder-icon">{{ currentStepInfo.icon }}</span>
            <h3>{{ currentStepInfo.title }}</h3>
            <p>{{ currentStepInfo.placeholder }}</p>
            <n-button type="primary" size="large" round @click="goWorkbench">
              进入工作台
            </n-button>
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

const roadmapSteps = [
  { key: 'planning', title: '选题策划', desc: '确定题材与金手指', status: 'done', icon: '💡', todo: '完成题材研究，确定核心梗和金手指设计', placeholder: '从市场研究开始，找到属于你的爆款选题' },
  { key: 'character', title: '人物设计', desc: '主角团与反派设定', status: 'current', icon: '👤', todo: '设计主角、配角、反派的人物档案和关系网', placeholder: '设计立体的人物，让故事活起来' },
  { key: 'worldview', title: '世界观', desc: '设定与规则体系', status: 'pending', icon: '🌍', todo: '构建完整的世界观设定和力量体系', placeholder: '构建独特的世界观，奠定故事基石' },
  { key: 'pacing', title: '节奏规划', desc: '大纲与节拍表', status: 'pending', icon: '📊', todo: '制定全书大纲、幕次结构和章节节拍', placeholder: '精心设计节奏，让读者欲罢不能' },
  { key: 'writing', title: '章节写作', desc: '正文创作', status: 'pending', icon: '✍️', todo: '按节奏规划逐章创作正文内容', placeholder: '开始写作，让故事绽放' },
  { key: 'quality', title: '质量检测', desc: '审校与优化', status: 'pending', icon: '✅', todo: '检查行文质量、一致性和AI痕迹', placeholder: '精雕细琢，打造精品' },
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

.step-placeholder {
  text-align: center;
  padding: 60px 20px;
}

.placeholder-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.step-placeholder h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--app-text-primary);
}

.step-placeholder p {
  margin: 0 0 24px;
  color: var(--app-text-muted);
  font-size: 14px;
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
</style>
