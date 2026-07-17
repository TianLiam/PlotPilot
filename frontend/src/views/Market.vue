<template>
  <div class="market-page">
    <MarketSectionHeader
      title="题材发现"
      subtitle="从实时榜单提炼热门题材、金手指、人物原型与爽点结构，再沉淀为可复用的创作模板。"
      back-to="/dashboard"
      back-label="返回创作总览"
    >
      <template #actions>
        <n-button
          secondary
          type="primary"
          size="medium"
          :loading="crawlLoading"
          @click="handleCrawlRankings"
        >
          刷新榜单并提炼
        </n-button>
      </template>
    </MarketSectionHeader>

    <n-space vertical :size="24" class="market-content">
      <section class="discovery-pipeline">
        <div class="pipeline-copy">
          <span class="pipeline-eyebrow">AUTOMATED DISCOVERY</span>
          <h2>热门榜单不是终点，它应该自动变成模板。</h2>
          <p>系统会抓取热门作品的免费章节，经 AI 识别共性结构后写入动态模板库；内置模板只作为无网络时的创作基线。</p>
        </div>
        <div class="pipeline-steps" aria-label="模板提炼流程">
          <div><span>01</span><strong>采集榜单</strong><small>平台热度与排名</small></div>
          <i>→</i>
          <div><span>02</span><strong>结构提炼</strong><small>正文样本与模式识别</small></div>
          <i>→</i>
          <div><span>03</span><strong>进入模板库</strong><small>{{ discoveredTemplateCount }} 个动态模板</small></div>
        </div>
        <n-button
          type="primary"
          secondary
          :loading="discoveryLoading"
          @click="handleDiscoverTemplates"
        >
          立即自动提炼
        </n-button>
      </section>

      <n-tabs v-model:value="activeTab" type="segment" animated class="market-tabs">
        <n-tab-pane name="trends" tab="热门题材">
          <n-card :bordered="false" class="trends-card">
            <div class="trends-header">
              <h3>热门题材推荐</h3>
              <span class="trends-hint">基于市场数据分析推荐</span>
            </div>
            <n-space :size="16" wrap class="trends-grid">
              <n-card
                v-for="item in genreRecommendations"
                :key="item.genre"
                :bordered="false"
                class="trend-card"
                hoverable
              >
                <div class="trend-card-header">
                  <span class="trend-genre">{{ item.genre }}</span>
                  <n-tag :type="getTrendTagType(item.trend)" round>
                    {{ getTrendLabel(item.trend) }}
                  </n-tag>
                </div>
                <div class="trend-score">
                  <span class="score-value">{{ formatHeatScore(item.score) }}</span>
                  <span class="score-unit">热度分</span>
                </div>
                <div class="trend-topics">
                  <span class="topics-label">热点标签:</span>
                  <n-space :size="4" wrap>
                    <n-tag
                      v-for="topic in (item.hot_topics || []).slice(0, 3)"
                      :key="topic"
                      size="small"
                      borderable
                    >
                      {{ topic }}
                    </n-tag>
                  </n-space>
                </div>
                <n-button size="small" type="primary" @click="selectGenre(item)">
                  选择这个题材
                </n-button>
              </n-card>
            </n-space>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="golden-fingers" tab="金手指模板">
          <TemplateCollectionPanel
            v-model="selectedGoldenFingerGenre"
            title="金手指模板"
            description="从热门作品中识别系统机制、能力边界与成长回路。"
            :templates="goldenFingers"
            :genre-options="genreOptions"
            :loading="templateLoading.goldenFinger"
            @reload="loadGoldenFingers"
            @use="useTemplate"
            @discover="handleDiscoverTemplates"
          />
        </n-tab-pane>

        <n-tab-pane name="characters" tab="人物模板">
          <TemplateCollectionPanel
            v-model="selectedCharacterGenre"
            title="人物模板"
            description="提炼人物动机、关系张力与可持续成长弧线。"
            :templates="characters"
            :genre-options="genreOptions"
            :loading="templateLoading.character"
            @reload="loadCharacters"
            @use="useTemplate"
            @discover="handleDiscoverTemplates"
          />
        </n-tab-pane>

        <n-tab-pane name="worldviews" tab="世界观模板">
          <TemplateCollectionPanel
            v-model="selectedWorldviewGenre"
            title="世界观模板"
            description="归纳力量体系、社会结构与长期冲突的承载方式。"
            :templates="worldviews"
            :genre-options="genreOptions"
            :loading="templateLoading.worldview"
            @reload="loadWorldviews"
            @use="useTemplate"
            @discover="handleDiscoverTemplates"
          />
        </n-tab-pane>

        <n-tab-pane name="cool-points" tab="爽点模板">
          <TemplateCollectionPanel
            v-model="selectedCoolPointGenre"
            title="爽点模板"
            description="按题材筛选情绪蓄压、释放时机与回报强度，避免机械重复。"
            :templates="coolPoints"
            :genre-options="genreOptions"
            :loading="templateLoading.coolPoint"
            @reload="loadCoolPoints"
            @use="useTemplate"
            @discover="handleDiscoverTemplates"
          />
        </n-tab-pane>
      </n-tabs>
    </n-space>

    <n-modal v-model:show="templateDetailVisible" :title="selectedTemplate?.name" preset="large">
      <div v-if="selectedTemplate" class="template-detail">
        <n-descriptions :column="2" bordered>
          <n-descriptions-item label="类型">{{ selectedTemplate.type }}</n-descriptions-item>
          <n-descriptions-item label="适用题材">{{ selectedTemplate.genre }}</n-descriptions-item>
          <n-descriptions-item label="热度">{{ selectedTemplate.popularity }}</n-descriptions-item>
          <n-descriptions-item label="使用次数">{{ selectedTemplate.usage_count }} 次</n-descriptions-item>
        </n-descriptions>
        <n-divider />
        <h4>模板详情</h4>
        <n-input
          v-model:value="templateDetailContent"
          type="textarea"
          :rows="15"
          readonly
          class="detail-content"
        />
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import MarketSectionHeader from '@/components/market/MarketSectionHeader.vue'
import TemplateCollectionPanel from '@/components/market/TemplateCollectionPanel.vue'
import {
  marketApi,
  type DiscoveredTemplate,
  type GenreRecommendation,
  type Template,
} from '@/api/market'

type TemplateKind = 'golden_finger' | 'character' | 'worldview' | 'cool_point'

const nMessage = useMessage()

const activeTab = ref('trends')
const genreRecommendations = ref<GenreRecommendation[]>([])
const goldenFingers = ref<Template[]>([])
const characters = ref<Template[]>([])
const worldviews = ref<Template[]>([])
const coolPoints = ref<Template[]>([])

const selectedGoldenFingerGenre = ref('')
const selectedCharacterGenre = ref('')
const selectedWorldviewGenre = ref('')
const selectedCoolPointGenre = ref('')
const crawlLoading = ref(false)
const discoveryLoading = ref(false)
const templateLoading = reactive({
  goldenFinger: false,
  character: false,
  worldview: false,
  coolPoint: false,
})

const templateDetailVisible = ref(false)
const selectedTemplate = ref<Template | null>(null)
const templateDetailContent = ref('')

const allTemplates = computed(() => [
  ...goldenFingers.value,
  ...characters.value,
  ...worldviews.value,
  ...coolPoints.value,
])

const genreOptions = computed(() => {
  const genres = new Set<string>(['都市', '玄幻', '科幻', '言情', '历史', '悬疑', '仙侠', '通用'])
  genreRecommendations.value.forEach(item => item.genre && genres.add(item.genre))
  allTemplates.value.forEach(item => item.genre && genres.add(item.genre))
  return [
    { label: '全部题材', value: '' },
    ...Array.from(genres).map(genre => ({ label: genre, value: genre })),
  ]
})

const discoveredTemplateCount = computed(() => {
  return new Set(
    allTemplates.value.filter(item => item.source === 'crawler').map(item => item.id),
  ).size
})

function toTemplate(item: DiscoveredTemplate): Template {
  return {
    id: item.id,
    name: item.name,
    type: item.pattern_type,
    genre: item.genre,
    description: item.description,
    popularity: Math.round((item.confidence_score || 0) * 100),
    usage_count: item.usage_count,
    content: item.content,
    source: 'crawler',
    confidence_score: item.confidence_score,
    occurrence_count: item.occurrence_count,
    trend: item.trend,
    tags: item.tags,
    source_novels: item.source_novels,
  }
}

function mergeTemplates(builtIn: Template[], discovered: DiscoveredTemplate[]): Template[] {
  const merged = [...discovered.map(toTemplate), ...builtIn.map(item => ({ ...item, source: 'built_in' as const }))]
  const seen = new Set<string>()
  return merged.filter(item => {
    const key = `${item.type}:${item.genre}:${item.name}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

async function loadTemplateGroup(
  kind: TemplateKind,
  genre: string,
  builtInLoader: () => Promise<Template[]>,
  target: { value: Template[] },
): Promise<void> {
  const [builtInResult, discoveredResult] = await Promise.allSettled([
    builtInLoader(),
    marketApi.getDiscoveredTemplates(kind, genre || undefined, 50),
  ])
  const builtIn = builtInResult.status === 'fulfilled' ? builtInResult.value : []
  const discovered = discoveredResult.status === 'fulfilled' ? discoveredResult.value : []
  target.value = mergeTemplates(builtIn, discovered)
  if (builtInResult.status === 'rejected' && discoveredResult.status === 'rejected') {
    throw builtInResult.reason
  }
}

async function loadGenreRecommendations(): Promise<void> {
  try {
    genreRecommendations.value = await marketApi.getGenreRecommendations(8)
  } catch (error) {
    console.error('Failed to load genre recommendations:', error)
  }
}

async function loadGoldenFingers(): Promise<void> {
  templateLoading.goldenFinger = true
  try {
    await loadTemplateGroup(
      'golden_finger',
      selectedGoldenFingerGenre.value,
      () => marketApi.getGoldenFingers(selectedGoldenFingerGenre.value || undefined, 30),
      goldenFingers,
    )
  } catch (error) {
    console.error('Failed to load golden finger templates:', error)
  } finally {
    templateLoading.goldenFinger = false
  }
}

async function loadCharacters(): Promise<void> {
  templateLoading.character = true
  try {
    await loadTemplateGroup(
      'character',
      selectedCharacterGenre.value,
      () => marketApi.getCharacters(selectedCharacterGenre.value || undefined, 30),
      characters,
    )
  } catch (error) {
    console.error('Failed to load character templates:', error)
  } finally {
    templateLoading.character = false
  }
}

async function loadWorldviews(): Promise<void> {
  templateLoading.worldview = true
  try {
    await loadTemplateGroup(
      'worldview',
      selectedWorldviewGenre.value,
      () => marketApi.getWorldviews(selectedWorldviewGenre.value || undefined, 30),
      worldviews,
    )
  } catch (error) {
    console.error('Failed to load worldview templates:', error)
  } finally {
    templateLoading.worldview = false
  }
}

async function loadCoolPoints(): Promise<void> {
  templateLoading.coolPoint = true
  try {
    await loadTemplateGroup(
      'cool_point',
      selectedCoolPointGenre.value,
      () => marketApi.getCoolPoints(selectedCoolPointGenre.value || undefined, 30),
      coolPoints,
    )
  } catch (error) {
    console.error('Failed to load cool point templates:', error)
  } finally {
    templateLoading.coolPoint = false
  }
}

async function loadAllTemplates(): Promise<void> {
  await Promise.all([loadGoldenFingers(), loadCharacters(), loadWorldviews(), loadCoolPoints()])
}

async function handleDiscoverTemplates(showStartedMessage = true): Promise<void> {
  discoveryLoading.value = true
  try {
    if (!genreRecommendations.value.length) await loadGenreRecommendations()
    const categories = Array.from(new Set(genreRecommendations.value.slice(0, 4).map(item => item.genre)))
    await marketApi.runDailyTemplateDiscovery({
      platforms: ['fanqie'],
      categories: categories.length ? categories : ['都市', '玄幻', '言情', '科幻'],
      top_n: 3,
    })
    if (showStartedMessage) {
      nMessage.success('已启动后台提炼；完成后刷新模板列表即可看到榜单模板')
    }
  } catch (error) {
    console.error('Failed to start template discovery:', error)
    nMessage.error('自动提炼启动失败，请检查榜单数据与模型配置')
  } finally {
    discoveryLoading.value = false
  }
}

async function handleCrawlRankings(): Promise<void> {
  crawlLoading.value = true
  try {
    nMessage.info('正在采集榜单并更新市场分析…')
    await marketApi.crawlRankings()
    await marketApi.generateAnalysis(7)
    await loadGenreRecommendations()
    await handleDiscoverTemplates(false)
    nMessage.success('榜单已更新，热门题材模板正在后台自动提炼')
  } catch (error) {
    console.error('Failed to refresh market intelligence:', error)
    nMessage.error('市场数据刷新失败')
  } finally {
    crawlLoading.value = false
  }
}

function getTrendTagType(trend: string) {
  if (trend === 'up') return 'success'
  if (trend === 'down') return 'error'
  return 'default'
}

function getTrendLabel(trend: string): string {
  if (trend === 'up') return '上升'
  if (trend === 'down') return '下降'
  return '稳定'
}

function formatHeatScore(score: number): number {
  const normalized = score <= 1 ? score * 100 : score
  return Math.max(0, Math.min(100, Math.round(normalized)))
}

function selectGenre(item: GenreRecommendation): void {
  selectedGoldenFingerGenre.value = item.genre
  selectedCharacterGenre.value = item.genre
  selectedWorldviewGenre.value = item.genre
  selectedCoolPointGenre.value = item.genre
  activeTab.value = 'golden-fingers'
}

async function useTemplate(template: Template): Promise<void> {
  try {
    if (template.source === 'crawler') {
      await marketApi.markDiscoveredTemplateUsed(template.id)
      selectedTemplate.value = { ...template, usage_count: template.usage_count + 1 }
    } else {
      await marketApi.useTemplate(template.id)
      selectedTemplate.value = await marketApi.getTemplateDetail(template.id)
    }
    templateDetailContent.value = selectedTemplate.value?.content || ''
    templateDetailVisible.value = true
    nMessage.success('模板已载入')
  } catch (error) {
    console.error('Failed to use template:', error)
    nMessage.error('模板载入失败')
  }
}

watch(selectedGoldenFingerGenre, loadGoldenFingers)
watch(selectedCharacterGenre, loadCharacters)
watch(selectedWorldviewGenre, loadWorldviews)
watch(selectedCoolPointGenre, loadCoolPoints)

onMounted(async () => {
  await Promise.all([loadGenreRecommendations(), loadAllTemplates()])
})
</script>

<style scoped>
.market-page {
  padding: 0;
  min-height: calc(100vh - 60px);
}

.market-header {
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  padding: 0 24px;
  margin-bottom: 0;
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

.sub-nav {
  display: flex;
  gap: 4px;
  max-width: 1400px;
  margin: 0 auto;
  padding-bottom: 0;
}

.sub-nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  text-decoration: none;
  color: var(--app-text-secondary);
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: all 0.2s ease;
  position: relative;
}

.sub-nav-item:hover {
  color: var(--app-text-primary);
}

.sub-nav-item.is-active {
  color: var(--color-brand);
  border-bottom-color: var(--color-brand);
  font-weight: 600;
}

.sub-nav-icon {
  font-size: 16px;
}

.sub-nav-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
  color: #fff;
  line-height: 1;
}

.market-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.market-tabs {
  width: 100%;
}

.trends-card {
  padding: 24px;
}

.trends-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.trends-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.trends-hint {
  font-size: 14px;
  color: #999;
}

.trends-grid {
  width: 100%;
}

.trend-card {
  width: 280px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.trend-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.trend-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.trend-genre {
  font-size: 16px;
  font-weight: 600;
}

.trend-score {
  margin-bottom: 16px;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  color: #4080ff;
}

.score-unit {
  font-size: 14px;
  color: #999;
  margin-left: 4px;
}

.trend-topics {
  margin-bottom: 16px;
}

.topics-label {
  font-size: 13px;
  color: #666;
  margin-right: 8px;
}

.templates-card {
  padding: 24px;
}

.templates-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.templates-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.genre-select {
  width: 120px;
}

.template-card {
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.template-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.template-name {
  font-size: 16px;
  font-weight: 600;
}

.template-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.template-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-meta {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #999;
  gap: 4px;
}

.template-detail {
  padding: 16px;
}

.detail-content {
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
}

/* Editorial workspace treatment shared with the creative overview. */
.market-page {
  min-height: 100%;
  padding: clamp(22px, 3vw, 38px);
  background:
    radial-gradient(circle at 8% 0%, var(--color-brand-light), transparent 28%),
    var(--app-page-bg);
}

.market-header {
  max-width: 1400px;
  margin: 0 auto 14px;
  padding: 0;
  background: transparent;
  border: 0;
}

.header-inner {
  align-items: flex-end;
  padding: 4px 2px 22px;
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

.page-title {
  margin-bottom: 7px;
  font-family: var(--font-serif);
  font-size: clamp(28px, 3vw, 36px);
  font-weight: 680;
}

.page-subtitle {
  max-width: 580px;
  font-size: 13px;
  line-height: 1.65;
}

.sub-nav {
  gap: 5px;
  padding: 5px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 14px;
  box-shadow: var(--app-shadow-sm);
}

.sub-nav-item {
  gap: 8px;
  min-height: 38px;
  margin: 0;
  padding: 0 14px;
  border: 0;
  border-radius: 9px;
  font-size: 13px;
}

.sub-nav-item:hover {
  background: var(--app-surface-subtle);
}

.sub-nav-item.is-active {
  background: var(--color-brand-light);
  border: 0;
}

.sub-nav-icon {
  color: var(--app-text-muted);
  font-family: var(--font-mono);
  font-size: 9px;
}

.sub-nav-badge {
  padding: 1px 5px;
  color: var(--color-brand);
  background: var(--color-brand-light);
  border: 1px solid var(--color-brand-border);
  border-radius: 999px;
  font-size: 9px;
}

.market-content {
  width: min(1240px, calc(100% - 48px));
  max-width: none;
  margin: 0 auto;
  padding: 26px 0 48px;
}

.discovery-pipeline {
  display: grid;
  grid-template-columns: minmax(260px, 1.15fr) minmax(460px, 1.6fr) auto;
  align-items: center;
  gap: 28px;
  padding: 24px 26px;
  border: 1px solid rgba(79, 70, 229, 0.16);
  border-radius: 18px;
  background:
    linear-gradient(120deg, rgba(79, 70, 229, 0.08), transparent 45%),
    var(--app-surface);
}

.pipeline-eyebrow {
  color: #4f46e5;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.pipeline-copy h2 {
  margin: 7px 0 6px;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 17px;
}

.pipeline-copy p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 11px;
  line-height: 1.65;
}

.pipeline-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.pipeline-steps div {
  display: flex;
  min-width: 110px;
  flex-direction: column;
  gap: 2px;
}

.pipeline-steps span {
  color: #818cf8;
  font-family: var(--font-mono);
  font-size: 9px;
}

.pipeline-steps strong {
  color: var(--app-text-primary);
  font-size: 12px;
}

.pipeline-steps small,
.pipeline-steps i {
  color: var(--app-text-muted);
  font-size: 10px;
  font-style: normal;
}

.market-tabs :deep(.n-tabs-nav) {
  max-width: 620px;
  margin-bottom: 14px;
}

.trends-card,
.templates-card {
  padding: 26px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 18px;
  box-shadow: var(--app-shadow-sm);
}

.trends-header,
.templates-header {
  margin-bottom: 22px;
}

.trends-header h3,
.templates-header h3 {
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 650;
}

.trends-hint {
  color: var(--app-text-muted);
  font-size: 11px;
}

.trends-grid :deep(.n-space-item) {
  min-width: min(290px, 100%);
  flex: 1 1 30%;
}

.trend-card,
.template-card {
  width: 100%;
  height: 100%;
  padding: 20px;
  background: var(--app-surface-subtle);
  border: 1px solid transparent;
  border-radius: 14px;
  box-shadow: none;
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
}

.trend-card:hover,
.template-card:hover {
  background: var(--color-brand-light);
  border-color: var(--color-brand-border);
  box-shadow: none;
  transform: translateY(-2px);
}

.trend-genre,
.template-name {
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 650;
}

.score-value {
  color: var(--color-brand);
  font-family: var(--font-mono);
  font-size: 30px;
}

.score-unit,
.topics-label,
.template-desc,
.template-meta {
  color: var(--app-text-muted);
}

@media (max-width: 720px) {
  .market-page {
    padding: 0;
  }

  .market-content {
    width: min(100% - 28px, 1240px);
    padding: 18px 0 36px;
  }

  .discovery-pipeline {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 20px;
  }

  .pipeline-steps {
    align-items: flex-start;
    flex-direction: column;
  }

  .pipeline-steps i {
    display: none;
  }

  .header-inner {
    align-items: flex-start;
    flex-direction: column;
    gap: 16px;
  }

  .sub-nav {
    overflow-x: auto;
  }

  .sub-nav-item {
    flex: 0 0 auto;
  }

  .trends-card,
  .templates-card {
    padding: 18px;
  }
}
</style>
