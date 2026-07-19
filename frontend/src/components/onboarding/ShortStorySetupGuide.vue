<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NModal, NSteps, NStep, NButton, NInput, NSelect, NTag, NAlert, NIcon, NSpace, NCard, NStatistic, NDivider } from 'naive-ui'
import { CreateOutline, SparklesOutline, CheckmarkCircleOutline, BookOutline } from '@vicons/ionicons5'
import { novelApi } from '@/api/novel'
import { YANXUAN_TEMPLATES, type YanxuanTemplate } from '@/utils/yanxuanPresets'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  'created': [novelId: string]
}>()

const currentStep = ref(1)
const selectedTemplateId = ref<string>('')
const storyIdea = ref('')
const customTitle = ref('')
const creating = ref(false)
const error = ref('')

const selectedTemplate = computed(() =>
  YANXUAN_TEMPLATES.find(t => t.id === selectedTemplateId.value)
)

// 根据 template 的 recommendedWords 推导章节数（每章 2000 字）
const targetChapters = computed(() => {
  if (!selectedTemplate.value) return 8
  return Math.max(4, Math.min(15, Math.ceil(selectedTemplate.value.recommendedWords / 2000)))
})

const targetWords = computed(() => selectedTemplate.value?.recommendedWords || 15000)

// 题材选项
const templateOptions = YANXUAN_TEMPLATES.map(t => ({
  label: t.name,
  value: t.id,
  description: t.description,
  tags: t.tags,
}))

// 拼接最终 premise
function buildPremise(): string {
  if (!selectedTemplate.value) return storyIdea.value
  const tpl = selectedTemplate.value
  const parts: string[] = []
  parts.push(`【题材：${tpl.name}】`)
  if (storyIdea.value.trim()) {
    parts.push(storyIdea.value.trim())
  } else {
    parts.push(tpl.premiseTemplate)
  }
  parts.push(`核心爽点：${tpl.coreAppeal}`)
  parts.push(`反转设计：${tpl.twistDesign}`)
  parts.push(`节奏要点：${tpl.pacingNotes}`)
  parts.push(`目标字数：约${tpl.recommendedWords}字，分${targetChapters.value}节`)
  return parts.join('\n')
}

async function handleCreate() {
  if (!selectedTemplateId.value) {
    error.value = '请先选择题材模板'
    return
  }
  if (!storyIdea.value.trim() && !selectedTemplate.value) {
    error.value = '请填写故事梗概'
    return
  }
  creating.value = true
  error.value = ''
  try {
    const novelId = 'short-' + Date.now()
    const title = customTitle.value.trim() || `${selectedTemplate.value!.name}短篇`
    const premise = buildPremise()

    const novel = await novelApi.createNovel({
      novel_id: novelId,
      title,
      author: '作者',
      target_chapters: targetChapters.value,
      premise,
      genre: selectedTemplate.value!.name,
      length_tier: 'micro_short',
      novel_form: 'short_story',
      target_words_per_chapter: 2000,
    })

    emit('created', novel.id)
    handleClose()
  } catch (e: any) {
    error.value = e?.message || '创建失败，请重试'
  } finally {
    creating.value = false
  }
}

function handleClose() {
  currentStep.value = 1
  selectedTemplateId.value = ''
  storyIdea.value = ''
  customTitle.value = ''
  error.value = ''
  emit('update:show', false)
}

function nextStep() {
  if (!selectedTemplateId.value) {
    error.value = '请先选择题材模板'
    return
  }
  error.value = ''
  currentStep.value = 2
}

function prevStep() {
  currentStep.value = 1
}
</script>

<template>
  <n-modal
    :show="show"
    @update:show="handleClose"
    :mask-closable="false"
    :close-on-esc="true"
    preset="card"
    title="短篇创作向导 · 知乎盐选"
    style="width: 92%; max-width: 720px; max-height: 90vh"
  >
    <n-steps :current="currentStep" size="small" class="wizard-steps">
      <n-step title="选题材 · 写梗概" description="选择盐选题材模板" />
      <n-step title="确认 · 开始创作" description="一键进入写作" />
    </n-steps>

    <div class="step-content">
      <!-- Step 1: 选题材 + 写梗概 -->
      <div v-if="currentStep === 1" class="step-panel">
        <n-alert type="info" :bordered="false" style="margin-bottom: 16px">
          知乎盐选短篇规范：8000-30000 字 · 第一人称 · 段落顶格 · 对话用破折号 · 每千字至少 1 个钩子
        </n-alert>

        <!-- 题材模板选择 -->
        <div class="field-group">
          <label class="field-label">题材模板</label>
          <div class="template-grid">
            <div
              v-for="tpl in YANXUAN_TEMPLATES"
              :key="tpl.id"
              class="template-card"
              :class="{ active: selectedTemplateId === tpl.id }"
              @click="selectedTemplateId = tpl.id"
            >
              <div class="template-header">
                <span class="template-name">{{ tpl.name }}</span>
                <n-tag v-if="selectedTemplateId === tpl.id" type="primary" size="small" :bordered="false">
                  已选
                </n-tag>
              </div>
              <p class="template-desc">{{ tpl.description }}</p>
              <div class="template-tags">
                <n-tag v-for="tag in tpl.tags" :key="tag" size="tiny" :bordered="false" type="info">
                  {{ tag }}
                </n-tag>
              </div>
              <div class="template-meta">
                <span>{{ tpl.recommendedWords }} 字</span>
                <span>·</span>
                <span>{{ tpl.recommendedSections }} 节</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 选中模板的详情 -->
        <div v-if="selectedTemplate" class="template-detail">
          <n-card size="small" :bordered="true">
            <div class="detail-row">
              <span class="detail-label">核心爽点</span>
              <span class="detail-value">{{ selectedTemplate.coreAppeal }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">反转设计</span>
              <span class="detail-value">{{ selectedTemplate.twistDesign }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">经典桥段</span>
              <div class="detail-tropes">
                <span v-for="trope in selectedTemplate.classicTropes" :key="trope" class="trope-item">
                  · {{ trope }}
                </span>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 故事梗概 -->
        <div class="field-group">
          <label class="field-label">故事梗概 <span class="optional">（可选，留空则用模板示例）</span></label>
          <n-input
            v-model:value="storyIdea"
            type="textarea"
            placeholder="用一两句话描述你的故事核心。比如：我发现丈夫的手机里有一个加密相册..."
            :rows="4"
            :maxlength="500"
            show-count
          />
        </div>

        <n-alert v-if="error" type="error" :bordered="false" style="margin-top: 12px">
          {{ error }}
        </n-alert>
      </div>

      <!-- Step 2: 确认参数 -->
      <div v-if="currentStep === 2" class="step-panel">
        <div class="confirm-section">
          <h3 class="confirm-title">
            <n-icon size="18"><CheckmarkCircleOutline /></n-icon>
            确认创作参数
          </h3>

          <div class="confirm-grid">
            <div class="confirm-item">
              <span class="confirm-label">题材</span>
              <span class="confirm-value">{{ selectedTemplate?.name }}</span>
            </div>
            <div class="confirm-item">
              <span class="confirm-label">目标字数</span>
              <span class="confirm-value">{{ targetWords }} 字</span>
            </div>
            <div class="confirm-item">
              <span class="confirm-label">章节数</span>
              <span class="confirm-value">{{ targetChapters }} 节（每节约 2000 字）</span>
            </div>
            <div class="confirm-item">
              <span class="confirm-label">形态</span>
              <span class="confirm-value">知乎盐选短篇</span>
            </div>
          </div>

          <n-divider />

          <!-- 标题 -->
          <div class="field-group">
            <label class="field-label">作品标题 <span class="optional">（可选）</span></label>
            <n-input
              v-model:value="customTitle"
              placeholder="留空则用题材名+短篇作为标题"
              :maxlength="50"
            />
          </div>

          <!-- premise 预览 -->
          <div class="field-group">
            <label class="field-label">梗概预览</label>
            <div class="premise-preview">{{ buildPremise() }}</div>
          </div>

          <n-alert type="warning" :bordered="false" style="margin-top: 12px">
            创建后将自动跳转到工作台，短篇模式会跳过宏观规划，直接进入写作。
          </n-alert>
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="wizard-footer">
        <n-button v-if="currentStep > 1" @click="prevStep">上一步</n-button>
        <div style="flex: 1"></div>
        <n-button @click="handleClose">取消</n-button>
        <n-button
          v-if="currentStep === 1"
          type="primary"
          @click="nextStep"
          :disabled="!selectedTemplateId"
        >
          下一步
        </n-button>
        <n-button
          v-if="currentStep === 2"
          type="primary"
          :loading="creating"
          @click="handleCreate"
        >
          <template #icon><n-icon><SparklesOutline /></n-icon></template>
          开始创作
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<style scoped>
.wizard-steps {
  margin-bottom: 24px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.template-card {
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  border-color: #2080f0;
  box-shadow: 0 2px 12px rgba(32, 128, 240, 0.1);
}

.template-card.active {
  border-color: #2080f0;
  background: #f0f9ff;
}

.template-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.template-name {
  font-weight: 600;
  font-size: 15px;
}

.template-desc {
  font-size: 12px;
  color: #666;
  margin: 8px 0;
}

.template-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.template-meta {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  display: flex;
  gap: 6px;
}

.template-detail {
  margin-top: 16px;
}

.detail-row {
  display: flex;
  margin-bottom: 8px;
  font-size: 13px;
}

.detail-label {
  width: 80px;
  color: #999;
  flex-shrink: 0;
}

.detail-value {
  color: #333;
  flex: 1;
}

.detail-tropes {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trope-item {
  font-size: 12px;
  color: #666;
}

.field-group {
  margin-bottom: 16px;
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.optional {
  font-weight: normal;
  color: #999;
  font-size: 12px;
}

.confirm-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.confirm-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.confirm-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.confirm-label {
  font-size: 12px;
  color: #999;
}

.confirm-value {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.premise-preview {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.wizard-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-panel {
  padding: 4px 0;
}
</style>
