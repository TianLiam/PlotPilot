<template>
  <div class="novel-research">
    <n-card title="📚 创作前研究" class="research-header">
      <template #header-extra>
        <n-tag :type="researchStatusType" round>
          {{ researchStatusText }}
        </n-tag>
      </template>
      
      <n-space vertical>
        <n-text>
          想知道你构思的题材+金手指组合能不能火？AI 会基于历史爆款数据生成完整的研究报告。
        </n-text>
        <n-text depth="3">
          💡 例如：「末日+系统+种田」近一年成功率19%，建议采用仓库流开局，避免重生流。
        </n-text>
      </n-space>
    </n-card>

    <!-- 输入面板 -->
    <n-card title="第一步：输入你的创意" style="margin-top: 16px">
      <n-form :model="formData" label-placement="top">
        <n-grid :cols="2" :x-gap="16">
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
            🚀 开始研究
          </n-button>
          <n-button
            size="large"
            :loading="quickCheckLoading"
            @click="quickCheck"
          >
            ⚡ 快速预检
          </n-button>
        </n-space>
      </n-form>
    </n-card>

    <!-- 快速预检结果 -->
    <n-card
      v-if="quickCheckResult"
      title="快速预检结果"
      style="margin-top: 16px"
    >
      <n-alert v-if="quickCheckResult.saturation" type="info" style="margin-bottom: 16px">
        市场饱和度：{{ quickCheckResult.saturation.message }}
        （评分：{{ (quickCheckResult.saturation.score * 100).toFixed(0) }}%）
      </n-alert>

      <n-grid v-if="quickCheckResult.conflict_check?.conflicts?.length" :cols="1">
        <n-gi>
          <n-text strong>⚠️ 金手指冲突检测：</n-text>
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
      :title="`研究报告 - ${research.research_id}`"
      style="margin-top: 16px"
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
      <n-card v-if="research.ai_summary" type="inner" title="📝 AI 综合评估" class="section">
        <p style="white-space: pre-wrap">{{ research.ai_summary }}</p>
      </n-card>

      <!-- 时机分析 -->
      <n-card
        v-if="research.timing_advice"
        type="inner"
        title="⏰ 时机分析"
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
        title="📊 题材数据统计"
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
        title="🎯 成功开局模式"
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
        title="💡 建议清单"
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
        title="⚠️ 风险警告"
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
        title="🏆 竞品分析"
        class="section"
      >
        <p style="white-space: pre-wrap">{{ research.ai_suggestions }}</p>
      </n-card>
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { marketApi } from '@/api/market'

const message = useMessage()

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
  const map = { rising: '📈 上升', stable: '➡️ 平稳', declining: '📉 下降' }
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
  padding: 16px;
}

.research-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.research-header :deep(.n-card-header__main) {
  color: white;
}

.section {
  margin-top: 12px;
}
</style>