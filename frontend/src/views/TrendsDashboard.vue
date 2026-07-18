<template>
  <div class="trends-page">
    <MarketSectionHeader
      title="趋势大盘"
      subtitle="把榜单波动拆成上涨、退潮与持续热门三类信号，先看变化，再决定是否跟进。"
      :back-to="backTarget"
      :back-label="backLabel"
    >
      <template #actions>
        <div class="range-control">
          <span>观察窗口</span>
          <n-radio-group v-model:value="timeRange" size="medium">
            <n-radio-button value="7">7天</n-radio-button>
            <n-radio-button value="30">30天</n-radio-button>
            <n-radio-button value="90">90天</n-radio-button>
          </n-radio-group>
        </div>
      </template>
    </MarketSectionHeader>

    <div class="trends-content">
      <section class="data-note">
        <span class="data-note-mark">DATA</span>
        <div>
          <strong>趋势仅使用真实榜单快照</strong>
          <p>{{ dataNotice }}</p>
        </div>
        <div class="data-note-tags">
          <n-tag v-if="focusGenre" :bordered="false" type="success">聚焦：{{ focusGenre }}</n-tag>
          <n-tag :bordered="false" type="info">{{ timeRange }} 天窗口</n-tag>
          <n-tag :bordered="false" :type="dashboard.data_state === 'historical' ? 'success' : 'warning'">
            {{ dataStateLabel }}
          </n-tag>
        </div>
      </section>

      <n-alert v-if="loadError" type="error" :show-icon="true" class="dashboard-alert">
        {{ loadError }}
      </n-alert>
      <n-empty
        v-else-if="!loading && dashboard.data_state === 'empty'"
        description="尚无真实榜单快照，请先在市场洞察页刷新榜单"
        class="dashboard-empty"
      />

      <n-grid :cols="3" :x-gap="16" :y-gap="16" responsive="screen" class="alert-section">
        <n-gi>
          <div class="alert-card alert-up">
            <div class="alert-icon">UP</div>
            <div class="alert-info">
              <div class="alert-value">{{ risingGenres.length }}</div>
              <div class="alert-label">暴涨题材</div>
            </div>
          </div>
        </n-gi>
        <n-gi>
          <div class="alert-card alert-down">
            <div class="alert-icon">DN</div>
            <div class="alert-info">
              <div class="alert-value">{{ fallingGenres.length }}</div>
              <div class="alert-label">下跌题材</div>
            </div>
          </div>
        </n-gi>
        <n-gi>
          <div class="alert-card alert-hot">
            <div class="alert-icon">HOT</div>
            <div class="alert-info">
              <div class="alert-value">{{ hotGenres.length }}</div>
              <div class="alert-label">持续热门</div>
            </div>
          </div>
        </n-gi>
      </n-grid>

      <n-grid :cols="2" :x-gap="20" :y-gap="20" responsive="screen" class="charts-section">
        <n-gi :span="2">
          <n-card
            class="chart-card"
            :bordered="false"
            :title="focusGenre ? `${focusGenre} · 题材热度走势` : '题材热度走势'"
          >
            <ChartWrapper
              :option="trendLineOption"
              height="360px"
              aria-label="题材热度近30天走势折线图"
            />
          </n-card>
        </n-gi>

        <n-gi :span="1">
          <n-card class="chart-card" :bordered="false" title="平台 × 题材 热度矩阵">
            <ChartWrapper
              :option="heatmapOption"
              height="320px"
              aria-label="平台题材热度热力图"
            />
          </n-card>
        </n-gi>

        <n-gi :span="1">
          <n-card class="chart-card" :bordered="false" title="榜单热门标签分布">
            <ChartWrapper
              :option="goldenFingerOption"
              height="320px"
              aria-label="榜单热门标签饼图"
            />
          </n-card>
        </n-gi>
      </n-grid>

      <n-grid :cols="2" :x-gap="20" :y-gap="20" responsive="screen">
        <n-gi>
          <n-card class="panel-card" :bordered="false">
            <template #header>
              <div class="panel-header">
                <span class="panel-title">涨幅榜 TOP 5</span>
              </div>
            </template>
            <div class="rank-list">
              <div
                v-for="(item, idx) in risingGenres"
                :key="item.name"
                class="rank-item"
                :class="{ 'is-focus': matchesFocus(item.name) }"
              >
                <div class="rank-num" :class="`rank-${idx + 1}`">{{ idx + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ item.name }}</div>
                  <div class="rank-meta">{{ item.platform }}</div>
                </div>
                <div class="rank-change up">+{{ item.change }}%</div>
              </div>
            </div>
          </n-card>
        </n-gi>

        <n-gi>
          <n-card class="panel-card" :bordered="false">
            <template #header>
              <div class="panel-header">
                <span class="panel-title">跌幅榜 TOP 5</span>
              </div>
            </template>
            <div class="rank-list">
              <div
                v-for="(item, idx) in fallingGenres"
                :key="item.name"
                class="rank-item"
                :class="{ 'is-focus': matchesFocus(item.name) }"
              >
                <div class="rank-num">{{ idx + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ item.name }}</div>
                  <div class="rank-meta">{{ item.platform }}</div>
                </div>
                <div class="rank-change down">{{ item.change }}%</div>
              </div>
            </div>
          </n-card>
        </n-gi>
      </n-grid>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import ChartWrapper from '@/components/charts/ChartWrapper.vue'
import MarketSectionHeader from '@/components/market/MarketSectionHeader.vue'
import { marketApi, type TrendDashboard } from '@/api/market'
import { getApiErrorDetail } from '@/utils/apiError'
import type { EChartsOption } from 'echarts'

const timeRange = ref('30')
const loading = ref(false)
const loadError = ref('')
const route = useRoute()
const focusGenre = computed(() => typeof route.query.genre === 'string' ? route.query.genre : '')
const focusGenreRoot = computed(() => focusGenre.value.split(/[\/·]/)[0]?.trim() || '')
const fromDashboard = computed(() => route.query.from === 'dashboard')
const backTarget = computed(() => fromDashboard.value ? '/dashboard' : '/market')
const backLabel = computed(() => fromDashboard.value ? '返回创作总览' : '返回市场洞察')

const emptyDashboard = (): TrendDashboard => ({
  days: Number(timeRange.value),
  data_state: 'empty',
  snapshot_count: 0,
  series_count: 0,
  rising: [],
  declining: [],
  hot: [],
  line_series: [],
  heatmap: [],
  hot_tags: [],
})

const dashboard = ref<TrendDashboard>(emptyDashboard())

const platformLabels: Record<string, string> = {
  qidian: '起点中文网',
  fanqie: '番茄小说',
  qimao: '七猫小说',
}

function platformLabel(platform: string): string {
  return platformLabels[platform] || platform
}

function matchesFocus(name: string): boolean {
  const root = focusGenreRoot.value
  return Boolean(root && (name.includes(root) || root.includes(name)))
}

const risingGenres = computed(() => dashboard.value.rising.map(item => ({
  name: item.genre,
  platform: platformLabel(item.platform),
  change: Math.round(item.change_value * 100) / 100,
})))

const fallingGenres = computed(() => dashboard.value.declining.map(item => ({
  name: item.genre,
  platform: platformLabel(item.platform),
  change: Math.round(item.change_value * 100) / 100,
})))

const hotGenres = computed(() => dashboard.value.hot)

const dataStateLabel = computed(() => ({
  empty: '无快照',
  single_snapshot: '单日样本',
  historical: '历史趋势',
}[dashboard.value.data_state]))

const dataNotice = computed(() => {
  if (dashboard.value.data_state === 'empty') {
    return '当前没有可用快照，不展示估算或随机趋势。'
  }
  if (dashboard.value.data_state === 'single_snapshot') {
    return `已读取 ${dashboard.value.snapshot_count} 个真实快照，但只有单日样本；热度可用，涨跌保持为 0。`
  }
  return `已读取 ${dashboard.value.snapshot_count} 个真实快照、${dashboard.value.series_count} 条平台题材序列。`
})

const selectedLineSeries = computed(() => {
  if (!focusGenreRoot.value) return dashboard.value.line_series
  return dashboard.value.line_series.filter(item => matchesFocus(item.genre))
})

const trendLineOption = computed<EChartsOption>(() => {
  const dates = Array.from(new Set(
    selectedLineSeries.value.flatMap(item => item.data_points.map(point => point.date)),
  )).sort()
  const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
  const names = selectedLineSeries.value.map(item => `${platformLabel(item.platform)} · ${item.genre}`)

  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: names, bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8 },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates.map(date => date.slice(5).replace('-', '/')),
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#64748b', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: '热度指数',
      nameTextStyle: { color: '#64748b', fontSize: 11 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLabel: { color: '#64748b', fontSize: 11 },
    },
    series: selectedLineSeries.value.map((item, i) => {
      const scoreByDate = new Map(item.data_points.map(point => [point.date, point.score]))
      return {
      name: names[i],
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2 },
      itemStyle: { color: colors[i % colors.length] },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: colors[i % colors.length] + '33' },
            { offset: 1, color: colors[i % colors.length] + '05' },
          ],
        },
      },
      data: dates.map(date => scoreByDate.get(date) ?? null),
    }}),
  }
})

const heatmapOption = computed<EChartsOption>(() => {
  const platformKeys = Array.from(new Set(dashboard.value.heatmap.map(item => item.platform)))
  const genres = Array.from(new Set(dashboard.value.heatmap.map(item => item.genre)))
  const platforms = platformKeys.map(platformLabel)
  const data: [number, number, number][] = dashboard.value.heatmap.map(item => [
    platformKeys.indexOf(item.platform),
    genres.indexOf(item.genre),
    item.score,
  ])
  const maxScore = Math.max(100, ...dashboard.value.heatmap.map(item => item.score))

  return {
    tooltip: {
      position: 'top',
      formatter: (p: any) => {
        return `${platforms[p.value[0]]} · ${genres[p.value[1]]}<br/>热度: ${p.value[2]}`
      },
    },
    grid: { left: '12%', right: '8%', top: '5%', bottom: '15%' },
    xAxis: {
      type: 'category',
      data: platforms,
      splitArea: { show: true },
      axisLabel: { color: '#64748b', fontSize: 11, rotate: 15 },
    },
    yAxis: {
      type: 'category',
      data: genres,
      splitArea: { show: true },
      axisLabel: { color: '#64748b', fontSize: 11 },
    },
    visualMap: {
      min: 0,
      max: maxScore,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: {
        color: ['#f0f9ff', '#bae6fd', '#7dd3fc', '#38bdf8', '#0ea5e9', '#0284c7'],
      },
      textStyle: { color: '#64748b', fontSize: 11 },
    },
    series: [{
      type: 'heatmap',
      data,
      label: { show: false },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 1,
        borderRadius: 4,
      },
      emphasis: {
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.1)' },
      },
    }],
  }
})

const goldenFingerOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    textStyle: { color: '#64748b', fontSize: 12 },
    itemWidth: 10,
    itemHeight: 10,
  },
  series: [{
    type: 'pie',
    radius: ['45%', '75%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: false,
    itemStyle: {
      borderRadius: 6,
      borderColor: '#fff',
      borderWidth: 2,
    },
    label: { show: false },
    emphasis: {
      label: {
        show: true,
        fontSize: 14,
        fontWeight: 'bold',
      },
    },
    data: dashboard.value.hot_tags,
  }],
}))

async function loadDashboard() {
  loading.value = true
  loadError.value = ''
  try {
    dashboard.value = await marketApi.getTrendDashboard(Number(timeRange.value))
  } catch (error) {
    dashboard.value = emptyDashboard()
    loadError.value = getApiErrorDetail(error) || '趋势大盘加载失败'
  } finally {
    loading.value = false
  }
}

watch(timeRange, loadDashboard, { immediate: true })
</script>

<style scoped>
.trends-page {
  min-height: calc(100vh - 60px);
  background: var(--app-page-bg);
}

.trends-header {
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

.trends-content {
  width: min(1240px, calc(100% - 48px));
  max-width: none;
  margin: 0 auto;
  padding: 26px 0 48px;
}

.range-control {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--app-text-muted);
  font-size: 11px;
}

.data-note {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
  padding: 16px 18px;
  border: 1px solid rgba(14, 165, 233, 0.14);
  border-radius: 14px;
  background: rgba(14, 165, 233, 0.055);
}

.data-note-mark {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 11px;
  background: #0f172a;
  color: #fff;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.08em;
}

.data-note strong {
  color: var(--app-text-primary);
  font-size: 13px;
}

.data-note p {
  margin: 3px 0 0;
  color: var(--app-text-muted);
  font-size: 11px;
}

.data-note-tags {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 7px;
  flex-wrap: wrap;
}

.alert-section {
  margin-bottom: 20px;
}

.alert-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-radius: 16px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  transition: all 0.2s ease;
}

.alert-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
}

.alert-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
  border-radius: 12px;
  flex-shrink: 0;
}

.alert-up .alert-icon { background: rgba(16, 185, 129, 0.1); }
.alert-down .alert-icon { background: rgba(239, 68, 68, 0.1); }
.alert-hot .alert-icon { background: rgba(245, 158, 11, 0.1); }

.alert-info {
  flex: 1;
}

.alert-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--app-text-primary);
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.alert-label {
  font-size: 13px;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-card {
  border: 1px solid var(--app-border);
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.chart-card :deep(.n-card-header) {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
  padding-bottom: 12px;
}

.panel-card {
  border: 1px solid var(--app-border);
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.panel-header {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.rank-item:hover {
  background: var(--app-surface-subtle);
}

.rank-item.is-focus {
  background: rgba(79, 70, 229, 0.08);
  box-shadow: inset 3px 0 0 #6366f1;
}

.rank-num {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  border-radius: 6px;
  background: var(--app-surface-subtle);
  color: var(--app-text-muted);
  flex-shrink: 0;
}

.rank-num.rank-1 { background: linear-gradient(135deg, #ef4444, #f97316); color: #fff; }
.rank-num.rank-2 { background: linear-gradient(135deg, #f97316, #f59e0b); color: #fff; }
.rank-num.rank-3 { background: linear-gradient(135deg, #f59e0b, #eab308); color: #fff; }

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--app-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-meta {
  font-size: 11px;
  color: var(--app-text-muted);
  margin-top: 1px;
}

.rank-change {
  font-size: 13px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  flex-shrink: 0;
}

.rank-change.up {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.rank-change.down {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

@media (max-width: 768px) {
  .trends-content {
    width: min(100% - 28px, 1240px);
    padding: 18px 0 36px;
  }

  .data-note {
    grid-template-columns: auto 1fr;
  }

  .data-note-tags {
    grid-column: 1 / -1;
    justify-self: start;
  }

  .header-inner {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
