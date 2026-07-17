<template>
  <div class="market-page">
    <div class="market-header">
      <n-page-header title="市场分析中心" :subtitle="subtitle">
        <template #header-extra>
          <n-space :size="12">
            <n-button @click="goHome">
              <template #icon>
                <n-icon><IconHome /></n-icon>
              </template>
              返回首页
            </n-button>
            <n-button type="primary" @click="handleCrawlRankings">
              <template #icon>
                <n-icon><IconRefresh /></n-icon>
              </template>
              刷新榜单
            </n-button>
            <n-button type="success" @click="handleCrawlHotTopics">
              <template #icon>
                <n-icon><IconFlame /></n-icon>
              </template>
              更新热点
            </n-button>
            <n-button type="info" @click="goResearch">
              <template #icon>
                <n-icon><IconSearch /></n-icon>
              </template>
              创作前研究
            </n-button>
          </n-space>
        </template>
      </n-page-header>
    </div>

    <n-space vertical :size="24" class="market-content">
      <n-tabs v-model:value="activeTab" class="market-tabs">
        <n-tab-pane name="trends" tab="📈 题材趋势">
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
                  <span class="score-value">{{ (item.score * 100).toFixed(0) }}</span>
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

        <n-tab-pane name="golden-fingers" tab="✨ 金手指模板">
          <n-card :bordered="false" class="templates-card">
            <div class="templates-header">
              <h3>金手指模板</h3>
              <n-space :size="8">
                <n-select
                  v-model:value="selectedGoldenFingerGenre"
                  placeholder="选择题材"
                  size="small"
                  class="genre-select"
                >
                  <n-option value="" label="全部" />
                  <n-option value="都市" label="都市" />
                  <n-option value="玄幻" label="玄幻" />
                  <n-option value="科幻" label="科幻" />
                </n-select>
                <n-button size="small" @click="loadGoldenFingers">
                  <template #icon>
                    <n-icon><IconRefresh /></n-icon>
                  </template>
                  刷新
                </n-button>
              </n-space>
            </div>
            <n-grid :cols="2" :x-gap="16" :y-gap="16">
              <n-card
                v-for="template in goldenFingers"
                :key="template.id"
                :bordered="false"
                class="template-card"
                hoverable
              >
                <div class="template-header">
                  <span class="template-name">{{ template.name }}</span>
                  <n-tag size="small" borderable>{{ template.genre }}</n-tag>
                </div>
                <p class="template-desc">{{ template.description }}</p>
                <div class="template-footer">
                  <n-space :size="16">
                    <span class="template-meta">
                      <n-icon><IconStar /></n-icon>
                      {{ template.popularity }}
                    </span>
                    <span class="template-meta">
                      <n-icon><IconUsers /></n-icon>
                      {{ template.usage_count }} 次使用
                    </span>
                  </n-space>
                  <n-button size="small" type="primary" @click="useTemplate(template)">
                    使用模板
                  </n-button>
                </div>
              </n-card>
            </n-grid>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="characters" tab="🧑 人物模板">
          <n-card :bordered="false" class="templates-card">
            <div class="templates-header">
              <h3>人物模板</h3>
              <n-space :size="8">
                <n-select
                  v-model:value="selectedCharacterGenre"
                  placeholder="选择题材"
                  size="small"
                  class="genre-select"
                >
                  <n-option value="" label="全部" />
                  <n-option value="都市" label="都市" />
                  <n-option value="玄幻" label="玄幻" />
                </n-select>
                <n-button size="small" @click="loadCharacters">
                  <template #icon>
                    <n-icon><IconRefresh /></n-icon>
                  </template>
                  刷新
                </n-button>
              </n-space>
            </div>
            <n-grid :cols="2" :x-gap="16" :y-gap="16">
              <n-card
                v-for="template in characters"
                :key="template.id"
                :bordered="false"
                class="template-card"
                hoverable
              >
                <div class="template-header">
                  <span class="template-name">{{ template.name }}</span>
                  <n-tag size="small" borderable>{{ template.genre }}</n-tag>
                </div>
                <p class="template-desc">{{ template.description }}</p>
                <div class="template-footer">
                  <n-space :size="16">
                    <span class="template-meta">
                      <n-icon><IconStar /></n-icon>
                      {{ template.popularity }}
                    </span>
                    <span class="template-meta">
                      <n-icon><IconUsers /></n-icon>
                      {{ template.usage_count }} 次使用
                    </span>
                  </n-space>
                  <n-button size="small" type="primary" @click="useTemplate(template)">
                    使用模板
                  </n-button>
                </div>
              </n-card>
            </n-grid>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="worldviews" tab="🌍 世界观模板">
          <n-card :bordered="false" class="templates-card">
            <div class="templates-header">
              <h3>世界观模板</h3>
              <n-space :size="8">
                <n-select
                  v-model:value="selectedWorldviewGenre"
                  placeholder="选择题材"
                  size="small"
                  class="genre-select"
                >
                  <n-option value="" label="全部" />
                  <n-option value="都市" label="都市" />
                  <n-option value="玄幻" label="玄幻" />
                  <n-option value="科幻" label="科幻" />
                </n-select>
                <n-button size="small" @click="loadWorldviews">
                  <template #icon>
                    <n-icon><IconRefresh /></n-icon>
                  </template>
                  刷新
                </n-button>
              </n-space>
            </div>
            <n-grid :cols="2" :x-gap="16" :y-gap="16">
              <n-card
                v-for="template in worldviews"
                :key="template.id"
                :bordered="false"
                class="template-card"
                hoverable
              >
                <div class="template-header">
                  <span class="template-name">{{ template.name }}</span>
                  <n-tag size="small" borderable>{{ template.genre }}</n-tag>
                </div>
                <p class="template-desc">{{ template.description }}</p>
                <div class="template-footer">
                  <n-space :size="16">
                    <span class="template-meta">
                      <n-icon><IconStar /></n-icon>
                      {{ template.popularity }}
                    </span>
                    <span class="template-meta">
                      <n-icon><IconUsers /></n-icon>
                      {{ template.usage_count }} 次使用
                    </span>
                  </n-space>
                  <n-button size="small" type="primary" @click="useTemplate(template)">
                    使用模板
                  </n-button>
                </div>
              </n-card>
            </n-grid>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="cool-points" tab="🔥 爽点模板">
          <n-card :bordered="false" class="templates-card">
            <div class="templates-header">
              <h3>爽点模板</h3>
              <n-button size="small" @click="loadCoolPoints">
                <template #icon>
                  <n-icon><IconRefresh /></n-icon>
                </template>
                刷新
              </n-button>
            </div>
            <n-grid :cols="2" :x-gap="16" :y-gap="16">
              <n-card
                v-for="template in coolPoints"
                :key="template.id"
                :bordered="false"
                class="template-card"
                hoverable
              >
                <div class="template-header">
                  <span class="template-name">{{ template.name }}</span>
                  <n-tag size="small" borderable>{{ template.genre }}</n-tag>
                </div>
                <p class="template-desc">{{ template.description }}</p>
                <div class="template-footer">
                  <n-space :size="16">
                    <span class="template-meta">
                      <n-icon><IconStar /></n-icon>
                      {{ template.popularity }}
                    </span>
                    <span class="template-meta">
                      <n-icon><IconUsers /></n-icon>
                      {{ template.usage_count }} 次使用
                    </span>
                  </n-space>
                  <n-button size="small" type="primary" @click="useTemplate(template)">
                    使用模板
                  </n-button>
                </div>
              </n-card>
            </n-grid>
          </n-card>
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
import { h, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NIcon } from 'naive-ui'
import { marketApi, type Template, type GenreRecommendation } from '../api'

const router = useRouter()
const nMessage = useMessage()

const activeTab = ref('trends')
const subtitle = ref('基于市场数据的智能题材推荐与模板库')

const genreRecommendations = ref<GenreRecommendation[]>([])
const goldenFingers = ref<Template[]>([])
const characters = ref<Template[]>([])
const worldviews = ref<Template[]>([])
const coolPoints = ref<Template[]>([])

const selectedGoldenFingerGenre = ref('')
const selectedCharacterGenre = ref('')
const selectedWorldviewGenre = ref('')

const templateDetailVisible = ref(false)
const selectedTemplate = ref<Template | null>(null)
const templateDetailContent = ref('')

const IconHome = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z' }))

const IconRefresh = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z' }))

const IconFlame = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 23c-4.5 0-8.5-3.5-8.5-8 0-2.5 1.5-4.5 4-6 0 0-2-4 1.5-7 1.5-1.5 5 1 7 1s5.5-2.5 7-1c3.5 3 1.5 7 1.5 7 2.5 1.5 4 3.5 4 6 0 4.5-4 8-8.5 8z' }))

const IconStar = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z' }))

const IconUsers = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' }))

const loadGenreRecommendations = async () => {
  try {
    const res = await marketApi.getGenreRecommendations(6)
    genreRecommendations.value = res
  } catch (e) {
    console.error('Failed to load genre recommendations:', e)
  }
}

const loadGoldenFingers = async () => {
  try {
    const res = await marketApi.getGoldenFingers(selectedGoldenFingerGenre.value || undefined, 10)
    goldenFingers.value = res
  } catch (e) {
    console.error('Failed to load golden fingers:', e)
  }
}

const loadCharacters = async () => {
  try {
    const res = await marketApi.getCharacters(selectedCharacterGenre.value || undefined, 10)
    characters.value = res
  } catch (e) {
    console.error('Failed to load characters:', e)
  }
}

const loadWorldviews = async () => {
  try {
    const res = await marketApi.getWorldviews(selectedWorldviewGenre.value || undefined, 10)
    worldviews.value = res
  } catch (e) {
    console.error('Failed to load worldviews:', e)
  }
}

const loadCoolPoints = async () => {
  try {
    const res = await marketApi.getCoolPoints(undefined, 10)
    coolPoints.value = res
  } catch (e) {
    console.error('Failed to load cool points:', e)
  }
}

const goHome = () => {
  router.push('/')
}

const goResearch = () => {
  router.push('/research')
}

const handleCrawlRankings = async () => {
  try {
    nMessage.info('正在爬取榜单数据...')
    await marketApi.crawlRankings()
    nMessage.info('正在生成市场分析...')
    await marketApi.generateAnalysis(7)
    await loadGenreRecommendations()
    nMessage.success('榜单刷新成功')
  } catch (e) {
    console.error('Failed to crawl rankings:', e)
    nMessage.error('榜单刷新失败')
  }
}

const handleCrawlHotTopics = async () => {
  try {
    nMessage.info('正在爬取热点数据...')
    await marketApi.crawlHotTopics()
    nMessage.info('正在生成市场分析...')
    await marketApi.generateAnalysis(7)
    await loadGenreRecommendations()
    nMessage.success('热点更新成功')
  } catch (e) {
    console.error('Failed to crawl hot topics:', e)
    nMessage.error('热点更新失败')
  }
}

const getTrendTagType = (trend: string) => {
  switch (trend) {
    case 'up':
      return 'success'
    case 'down':
      return 'error'
    default:
      return 'default'
  }
}

const getTrendLabel = (trend: string) => {
  switch (trend) {
    case 'up':
      return '📈 上升'
    case 'down':
      return '📉 下降'
    default:
      return '➡️ 稳定'
  }
}

const selectGenre = (item: GenreRecommendation) => {
  activeTab.value = 'golden-fingers'
}

const useTemplate = async (template: Template) => {
  try {
    const res = await marketApi.getTemplateDetail(template.id)
    selectedTemplate.value = res
    templateDetailContent.value = res.content || ''
    templateDetailVisible.value = true
  } catch (e) {
    console.error('Failed to get template detail:', e)
  }
}

onMounted(() => {
  loadGenreRecommendations()
  loadGoldenFingers()
  loadCharacters()
  loadWorldviews()
  loadCoolPoints()
})
</script>

<style scoped>
.market-page {
  padding: 24px;
  min-height: 100vh;
}

.market-header {
  margin-bottom: 24px;
}

.market-content {
  max-width: 1400px;
  margin: 0 auto;
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
</style>