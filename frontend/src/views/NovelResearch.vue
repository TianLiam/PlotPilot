<template>
  <div class="novel-research">
    <MarketSectionHeader
      title="题材研究"
      subtitle="在开书之前验证题材组合、金手指冲突与市场饱和度，把直觉变成可以复盘的决策。"
    >
      <template #actions>
        <n-tag :type="researchStatusType" round>
          {{ researchStatusText }}
        </n-tag>
      </template>
    </MarketSectionHeader>

    <div class="research-content">
      <section class="research-workspace">
        <aside class="research-brief">
          <span class="brief-index">RESEARCH / 01</span>
          <h2>先验证组合，再投入长篇成本。</h2>
          <p>研究报告会同时检查市场窗口、同类样本、开局结构与金手指冲突，不直接替你决定题材。</p>
          <div class="brief-steps">
            <div><span>01</span><strong>定义题材组合</strong><small>主赛道、金手指、目标体量</small></div>
            <div><span>02</span><strong>先做快速预检</strong><small>查看饱和度与设定冲突</small></div>
            <div><span>03</span><strong>生成完整研究</strong><small>形成可保存的创作依据</small></div>
          </div>
        </aside>

        <n-card title="研究参数" class="research-form-card" :bordered="false">
      <n-form :model="formData" label-placement="top">
        <n-grid cols="1 m:2" responsive="screen" :x-gap="16">
          <n-gi>
            <n-form-item label="目标平台">
              <n-select
                v-model:value="formData.platform"
                :options="platformOptions"
                clearable
                placeholder="综合市场"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="题材组合（可多选）">
              <n-select
                v-model:value="formData.genres"
                multiple
                :options="genreOptions"
                placeholder="选择题材，如：末日、系统、种田"
                max-tag-count="responsive"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="金手指（可多选）">
              <n-select
                v-model:value="formData.golden_fingers"
                multiple
                :options="goldenFingerOptions"
                placeholder="选择金手指设定"
                max-tag-count="responsive"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="目标字数">
              <n-input-number
                v-model:value="formData.target_word_count"
                placeholder="例如 1000000"
                :min="0"
                :step="10000"
                style="width: 100%"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="目标章节数">
              <n-input-number
                v-model:value="formData.target_chapter_count"
                placeholder="例如 1000"
                :min="0"
                :step="100"
                style="width: 100%"
              />
            </n-form-item>
          </n-gi>
          <n-gi :span="2">
            <n-form-item label="关键词（逗号分隔）">
              <n-input
                v-model:value="keywordsText"
                placeholder="例如：末世、囤货、觉醒、进化"
              />
            </n-form-item>
          </n-gi>
          <n-gi :span="2">
            <n-form-item label="补充说明（可选）">
              <n-input
                v-model:value="formData.additional_notes"
                type="textarea"
                placeholder="可以描述你的灵感来源、目标读者群、特别想突出或避免的元素..."
                :rows="3"
              />
            </n-form-item>
          </n-gi>
        </n-grid>

        <n-space>
          <n-button
            type="primary"
            size="large"
            :loading="loading"
            @click="conductResearch"
            :disabled="!canResearch"
          >
            生成完整研究
          </n-button>
          <n-button
            size="large"
            :loading="quickCheckLoading"
            @click="quickCheck"
          >
            快速预检
          </n-button>
        </n-space>
      </n-form>
        </n-card>
      </section>

    <!-- 快速预检结果 -->
    <n-card
      v-if="quickCheckResult"
      title="快速预检结果"
      class="result-card"
    >
      <n-alert v-if="quickCheckResult.saturation" type="info" style="margin-bottom: 16px">
        市场饱和度：{{ quickCheckResult.saturation.message }}
        （评分：{{ (quickCheckResult.saturation.score * 100).toFixed(0) }}%）
      </n-alert>

      <n-grid v-if="quickCheckResult.conflict_check?.conflicts?.length" :cols="1">
        <n-gi>
          <n-text strong>金手指冲突检测：</n-text>
          <n-list>
            <n-list-item v-for="(c, i) in quickCheckResult.conflict_check.conflicts" :key="i">
              <n-tag :type="c.severity === 'warning' ? 'warning' : 'info'">
                {{ c.golden_finger }}
              </n-tag>
              <span style="margin-left: 8px">{{ c.message }}</span>
            </n-list-item>
          </n-list>
        </n-gi>
      </n-grid>
    </n-card>

    <!-- 完整研究报告 -->
    <n-card
      v-if="research"
      :title="`研究报告 · ${research.research_id}`"
      class="result-card research-report"
    >
      <template #header-extra>
        <n-space>
          <n-tag :type="getScoreType(research.overall_score)">
            综合评分: {{ research.overall_score }}/100
          </n-tag>
          <n-tag :type="getRiskType(research.risk_level)">
            风险: {{ getRiskLabel(research.risk_level) }}
          </n-tag>
        </n-space>
      </template>

      <!-- 摘要 -->
      <n-card v-if="research.ai_summary" type="inner" title="综合评估" class="section">
        <p style="white-space: pre-wrap">{{ research.ai_summary }}</p>
      </n-card>

      <!-- 时机分析 -->
      <n-card
        v-if="research.timing_advice"
        type="inner"
        title="时机分析"
        class="section"
      >
        <n-space vertical>
          <n-progress
            type="line"
            :percentage="research.timing_score"
            :status="getTimingStatus(research.timing_score)"
          />
          <p>{{ research.timing_advice }}</p>
        </n-space>
      </n-card>

      <!-- 题材统计 -->
      <n-card
        v-if="research.genre_stats?.length"
        type="inner"
        title="题材数据统计"
        class="section"
      >
        <n-grid :cols="2" :x-gap="16">
          <n-gi v-for="(stats, i) in research.genre_stats" :key="i">
            <n-card hoverable embedded>
              <template #header>
                <n-space>
                  <n-text strong>{{ stats.genre }}</n-text>
                  <n-tag :type="getTrendType(stats.trend)">
                    {{ getTrendLabel(stats.trend) }} {{ stats.trend_change }}%
                  </n-tag>
                </n-space>
              </template>
              <n-descriptions :column="1" size="small">
                <n-descriptions-item label="样本数">
                  {{ stats.total_novels }} (成功: {{ stats.successful_novels }})
                </n-descriptions-item>
                <n-descriptions-item label="成功率">
                  <n-text :type="getSuccessRateType(stats.success_rate)">
                    {{ (stats.success_rate * 100).toFixed(1) }}%
                  </n-text>
                </n-descriptions-item>
                <n-descriptions-item label="平均字数">
                  {{ formatNumber(stats.avg_word_count) }}
                </n-descriptions-item>
                <n-descriptions-item label="平均章节">
                  {{ stats.avg_chapter_count }}
                </n-descriptions-item>
                <n-descriptions-item label="推荐章节字数">
                  {{ stats.optimal_chapter_words }}
                </n-descriptions-item>
                <n-descriptions-item label="平均排名">
                  #{{ stats.avg_peak_rank }}
                </n-descriptions-item>
              </n-descriptions>
            </n-card>
          </n-gi>
        </n-grid>
      </n-card>

      <!-- 成功开局 -->
      <n-card
        v-if="research.opening_patterns?.length"
        type="inner"
        title="成功开局模式"
        class="section"
      >
        <n-list>
          <n-list-item v-for="(p, i) in research.opening_patterns" :key="i">
            <template #prefix>
              <n-tag :type="p.success_rate > 0.3 ? 'success' : 'default'">
                {{ (p.success_rate * 100).toFixed(0) }}%
              </n-tag>
            </template>
            <n-thing :title="p.name" :description="p.description">
              <template #header-extra>
                <n-text depth="3">
                  样本: {{ p.success_count }} | 热度: {{ formatNumber(p.avg_popularity) }}
                </n-text>
              </template>
              <n-space size="small" style="margin-top: 8px">
                <n-tag v-for="kp in p.key_points" :key="kp" size="small" type="info">
                  {{ kp }}
                </n-tag>
              </n-space>
              <div v-if="p.sample_novels?.length" style="margin-top: 8px">
                <n-text depth="3">参考：</n-text>
                <n-tag
                  v-for="sn in p.sample_novels.slice(0, 3)"
                  :key="sn"
                  size="small"
                  style="margin-left: 4px"
                >
                  {{ sn }}
                </n-tag>
              </div>
            </n-thing>
          </n-list-item>
        </n-list>
      </n-card>

      <!-- 建议 -->
      <n-card
        v-if="research.recommendations?.length"
        type="inner"
        title="建议清单"
        class="section"
      >
        <n-list>
          <n-list-item v-for="(r, i) in research.recommendations" :key="i">
            <template #prefix>
              <n-tag :type="getRecType(r.type)">
                {{ getRecLabel(r.type) }}
              </n-tag>
            </template>
            <n-thing :title="r.title">
              <p style="white-space: pre-wrap">{{ r.description }}</p>
              <n-text v-if="r.reason" depth="3" style="margin-top: 4px">
                理由：{{ r.reason }}
              </n-text>
            </n-thing>
          </n-list-item>
        </n-list>
      </n-card>

      <!-- 警告 -->
      <n-card
        v-if="research.ai_warnings"
        type="inner"
        title="风险警告"
        class="section"
      >
        <n-alert type="warning" :show-icon="false">
          <p style="white-space: pre-wrap">{{ research.ai_warnings }}</p>
        </n-alert>
      </n-card>

      <!-- 竞品分析 -->
      <n-card
        v-if="research.ai_suggestions"
        type="inner"
        title="竞品分析"
        class="section"
      >
        <p style="white-space: pre-wrap">{{ research.ai_suggestions }}</p>
      </n-card>
      </n-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { marketApi } from '@/api/market'
import MarketSectionHeader from '@/components/market/MarketSectionHeader.vue'

const message = useMessage()

const platformOptions = [
  { label: '番茄小说', value: 'fanqie' },
  { label: '起点中文网', value: 'qidian' },
  { label: '七猫小说', value: 'qimao' },
]

// 表单数据
const formData = ref({
  genres: [],
  golden_fingers: [],
  keywords: [],
  target_word_count: 0,
  target_chapter_count: 0,
  additional_notes: '',
  platform: null,
})

const keywordsText = ref('')

// 状态
const loading = ref(false)
const quickCheckLoading = ref(false)
const research = ref(null)
const quickCheckResult = ref(null)

// 选项
const genreOptions = ref([])
const goldenFingerOptions = ref([])

const canResearch = computed(() =>
  formData.value.genres.length > 0 || formData.value.golden_fingers.length > 0
)

const researchStatusType = computed(() => {
  if (!research.value) return 'default'
  if (research.value.status === 'completed') return 'success'
  if (research.value.status === 'analyzing') return 'info'
  if (research.value.status === 'failed') return 'error'
  return 'default'
})

const researchStatusText = computed(() => {
  if (!research.value) return '未开始'
  const map = {
    pending: '等待中',
    analyzing: '分析中...',
    completed: '已完成',
    failed: '失败',
  }
  return map[research.value.status] || research.value.status
})

onMounted(async () => {
  await loadOptions()
})

async function loadOptions() {
  try {
    const [genresRes, gfsRes] = await Promise.all([
      marketApi.getGenreOptions(),
      marketApi.getGoldenFingerOptions(),
    ])
    genreOptions.value = genresRes.genres.map(g => ({
      label: g.label,
      value: g.value,
    }))
    goldenFingerOptions.value = gfsRes.golden_fingers.map(g => ({
      label: `${g.label} (${g.category})`,
      value: g.value,
    }))
  } catch (e) {
    console.error('Failed to load options:', e)
  }
}

async function conductResearch() {
  if (!canResearch.value) {
    message.warning('请至少选择题材或金手指')
    return
  }

  // 解析关键词
  formData.value.keywords = keywordsText.value
    .split(/[,，\s]+/)
    .filter(k => k.trim())

  loading.value = true
  research.value = null

  try {
    const result = await marketApi.conductResearch(formData.value)
    research.value = result
    message.success('研究报告生成完成')
  } catch (e) {
    message.error(`研究失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

async function quickCheck() {
  formData.value.keywords = keywordsText.value
    .split(/[,，\s]+/)
    .filter(k => k.trim())

  quickCheckLoading.value = true

  try {
    const result = await marketApi.quickCheck(formData.value)
    quickCheckResult.value = result
    message.success('快速预检完成')
  } catch (e) {
    message.error(`预检失败: ${e.message}`)
  } finally {
    quickCheckLoading.value = false
  }
}

// 格式化
function formatNumber(n) {
  if (!n) return '0'
  return n.toLocaleString('zh-CN')
}

function getScoreType(score) {
  if (score >= 70) return 'success'
  if (score >= 50) return 'warning'
  return 'error'
}

function getRiskType(risk) {
  const map = { low: 'success', medium: 'warning', high: 'error' }
  return map[risk] || 'default'
}

function getRiskLabel(risk) {
  const map = { low: '低', medium: '中', high: '高' }
  return map[risk] || risk
}

function getTrendType(trend) {
  const map = { rising: 'success', stable: 'default', declining: 'error' }
  return map[trend] || 'default'
}

function getTrendLabel(trend) {
  const map = { rising: '上升', stable: '平稳', declining: '下降' }
  return map[trend] || trend
}

function getRecType(type) {
  const map = {
    recommend: 'success',
    avoid: 'error',
    caution: 'warning',
    info: 'info',
  }
  return map[type] || 'default'
}

function getRecLabel(type) {
  const map = {
    recommend: '推荐',
    avoid: '避免',
    caution: '注意',
    info: '信息',
  }
  return map[type] || type
}

function getSuccessRateType(rate) {
  if (rate >= 0.3) return 'success'
  if (rate >= 0.15) return 'warning'
  return 'error'
}

function getTimingStatus(score) {
  if (score >= 70) return 'success'
  if (score >= 50) return 'warning'
  return 'error'
}
</script>

<style scoped>
.novel-research {
  min-height: calc(100vh - 60px);
  background: var(--app-page-bg);
}

.research-content {
  width: min(1240px, calc(100% - 48px));
  margin: 0 auto;
  padding: 26px 0 52px;
}

.research-workspace {
  display: grid;
  grid-template-columns: minmax(260px, 0.78fr) minmax(0, 1.7fr);
  gap: 18px;
  align-items: stretch;
}

.research-brief {
  display: flex;
  flex-direction: column;
  padding: clamp(24px, 3vw, 34px);
  border-radius: 20px;
  background:
    radial-gradient(circle at 100% 0, rgba(99, 102, 241, 0.34), transparent 38%),
    #111827;
  color: #fff;
}

.brief-index {
  color: #a5b4fc;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.research-brief h2 {
  margin: 18px 0 10px;
  color: #fff;
  font-family: var(--font-serif);
  font-size: clamp(23px, 2.7vw, 34px);
  line-height: 1.25;
}

.research-brief > p {
  margin: 0;
  color: #cbd5e1;
  font-size: 12px;
  line-height: 1.75;
}

.brief-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: auto;
  padding-top: 36px;
}

.brief-steps div {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 2px 10px;
}

.brief-steps span {
  grid-row: 1 / 3;
  color: #818cf8;
  font-family: var(--font-mono);
  font-size: 10px;
}

.brief-steps strong {
  font-size: 12px;
}

.brief-steps small {
  color: #94a3b8;
  font-size: 10px;
}

.research-form-card,
.result-card {
  border: 1px solid var(--app-border);
  border-radius: 20px;
  background: var(--app-surface);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.045);
}

.research-form-card :deep(.n-card-header) {
  padding: 26px 28px 8px;
}

.research-form-card :deep(.n-card__content) {
  padding: 18px 28px 28px;
}

.research-form-card :deep(.n-card-header__main),
.result-card :deep(.n-card-header__main) {
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 19px;
}

.result-card {
  margin-top: 18px;
}

.research-report {
  padding: 4px;
}

.section {
  margin-top: 14px;
  border: 1px solid var(--app-border);
  border-radius: 14px;
}

@media (max-width: 860px) {
  .research-workspace {
    grid-template-columns: 1fr;
  }

  .brief-steps {
    margin-top: 8px;
    padding-top: 24px;
  }
}

@media (max-width: 620px) {
  .research-content {
    width: min(100% - 28px, 1240px);
    padding: 18px 0 36px;
  }

  .research-form-card :deep(.n-card-header),
  .research-form-card :deep(.n-card__content) {
    padding-left: 18px;
    padding-right: 18px;
  }
}
</style>
