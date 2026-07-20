<script setup lang="ts">
import { ref, computed } from 'vue'
import { NTabPane, NTabs, NProgress, NTag, NButton, NBadge, NSpace, NTooltip } from 'naive-ui'
import {
  SparklesOutline,
  WarningOutline,
  CheckmarkOutline,
  PeopleOutline,
  BookOutline,
  LocationOutline,
  FlashOutline,
  TrendingUpOutline,
  TrendingDownOutline,
  RemoveOutline,
  ChevronForwardOutline,
  RefreshOutline,
} from '@vicons/ionicons5'

const activeTab = ref('overview')

const consistencyScores = ref([
  { label: '剧情一致性', score: 92, icon: BookOutline, color: '#22c55e' },
  { label: '人物一致性', score: 85, icon: PeopleOutline, color: '#3b82f6' },
  { label: '世界观一致性', score: 96, icon: LocationOutline, color: '#8b5cf6' },
  { label: '节奏合理性', score: 78, icon: FlashOutline, color: '#f59e0b' },
])

const overallScore = computed(() => {
  const sum = consistencyScores.value.reduce((acc, s) => acc + s.score, 0)
  return Math.round(sum / consistencyScores.value.length)
})

const foreshadowStats = ref({
  total: 12,
  resolved: 9,
  pending: 3,
})

const foreshadowRate = computed(() =>
  Math.round((foreshadowStats.value.resolved / foreshadowStats.value.total) * 100)
)

const risks = ref([
  { type: 'warning', text: '人物李牧已 17 章未出场', detail: '建议安排回归场景' },
  { type: 'danger', text: '第12章设定与第20章冲突', detail: '地点「北城」位置描述不一致' },
  { type: 'info', text: '当前章节张力偏低', detail: '建议增加冲突或转折' },
])

const suggestions = ref([
  { icon: FlashOutline, text: '提升冲突强度', color: '#f59e0b' },
  { icon: PeopleOutline, text: '增加角色对白', color: '#3b82f6' },
  { icon: BookOutline, text: '回收伏笔', color: '#8b5cf6' },
])

const characterActivity = ref([
  { name: '李牧', chapters: 0, status: 'inactive' },
  { name: '林雨', chapters: 5, status: 'active' },
  { name: '王强', chapters: 2, status: 'normal' },
])

function getScoreColor(score: number) {
  if (score >= 90) return '#22c55e'
  if (score >= 80) return '#3b82f6'
  if (score >= 70) return '#f59e0b'
  return '#ef4444'
}

function getScoreLabel(score: number) {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '一般'
  return '需改进'
}
</script>

<template>
  <div class="ai-inspector">
    <div class="inspector-header">
      <div class="inspector-title">
        <SparklesOutline class="title-icon" :size="18" />
        <span>AI Inspector</span>
      </div>
      <n-tooltip trigger="hover" content="刷新分析">
        <button class="refresh-btn">
          <RefreshOutline :size="14" />
        </button>
      </n-tooltip>
    </div>

    <n-tabs v-model:value="activeTab" type="line" size="small" animated class="inspector-tabs">
      <!-- 总览 -->
      <n-tab-pane name="overview" tab="总览">
        <div class="tab-content">
          <!-- 综合健康度 -->
          <div class="health-score-card">
            <div class="health-ring">
              <svg class="ring-svg" viewBox="0 0 100 100">
                <circle class="ring-bg" cx="50" cy="50" r="42" />
                <circle
                  class="ring-progress"
                  cx="50"
                  cy="50"
                  r="42"
                  :stroke-dasharray="`${overallScore * 2.64} 264`"
                  :style="{ stroke: getScoreColor(overallScore) }"
                />
              </svg>
              <div class="ring-center">
                <span class="ring-value" :style="{ color: getScoreColor(overallScore) }">
                  {{ overallScore }}
                </span>
                <span class="ring-label">{{ getScoreLabel(overallScore) }}</span>
              </div>
            </div>
            <div class="health-title">作品健康度</div>
          </div>

          <!-- 四维评分 -->
          <div class="score-list">
            <div v-for="item in consistencyScores" :key="item.label" class="score-item">
              <div class="score-left">
                <div class="score-icon" :style="{ background: item.color + '15', color: item.color }">
                  <component :is="item.icon" :size="14" />
                </div>
                <span class="score-label">{{ item.label }}</span>
              </div>
              <div class="score-right">
                <span class="score-value" :style="{ color: item.color }">{{ item.score }}</span>
              </div>
            </div>
          </div>

          <!-- 伏笔统计 -->
          <div class="stat-block">
            <div class="stat-block-header">
              <span class="stat-block-title">伏笔状态</span>
              <n-tag size="small" type="info" round :bordered="false">
                {{ foreshadowStats.pending }} 待回收
              </n-tag>
            </div>
            <div class="foreshadow-progress">
              <n-progress
                type="line"
                :percentage="foreshadowRate"
                :show-indicator="false"
                :height="6"
                color="#8b5cf6"
                rail-color="rgba(139, 92, 246, 0.1)"
              />
              <div class="foreshadow-meta">
                <span>{{ foreshadowStats.resolved }} / {{ foreshadowStats.total }} 已回收</span>
                <span class="rate-text">{{ foreshadowRate }}%</span>
              </div>
            </div>
          </div>
        </div>
      </n-tab-pane>

      <!-- 风险 -->
      <n-tab-pane name="risks">
        <template #tab>
          <div class="tab-header-badge">
            风险
            <n-badge :value="risks.length" type="warning" size="small">
              <span class="badge-placeholder">!</span>
            </n-badge>
          </div>
        </template>
        <div class="tab-content">
          <div class="risk-list">
            <div
              v-for="(risk, idx) in risks"
              :key="idx"
              class="risk-item"
              :class="risk.type"
            >
              <div class="risk-icon">
                <WarningOutline v-if="risk.type === 'warning'" :size="16" />
                <WarningOutline v-else-if="risk.type === 'danger'" :size="16" />
                <RemoveOutline v-else :size="16" />
              </div>
              <div class="risk-content">
                <div class="risk-text">{{ risk.text }}</div>
                <div class="risk-detail">{{ risk.detail }}</div>
              </div>
              <ChevronForwardOutline class="risk-arrow" :size="14" />
            </div>
          </div>
        </div>
      </n-tab-pane>

      <!-- 建议 -->
      <n-tab-pane name="suggestions" tab="建议">
        <div class="tab-content">
          <div class="suggestion-list">
            <button
              v-for="(item, idx) in suggestions"
              :key="idx"
              class="suggestion-btn"
              :style="{ '--sug-color': item.color }"
            >
              <component :is="item.icon" class="sug-icon" :size="16" />
              <span class="sug-text">{{ item.text }}</span>
              <ChevronForwardOutline class="sug-arrow" :size="14" />
            </button>
          </div>
        </div>
      </n-tab-pane>

      <!-- 人物 -->
      <n-tab-pane name="characters" tab="人物">
        <div class="tab-content">
          <div class="char-list">
            <div v-for="char in characterActivity" :key="char.name" class="char-item">
              <div class="char-avatar" :class="char.status">
                {{ char.name[0] }}
              </div>
              <div class="char-info">
                <div class="char-name">{{ char.name }}</div>
                <div class="char-meta">
                  <span v-if="char.status === 'inactive'" class="inactive-text">
                    已 {{ char.chapters }} 章未出场
                  </span>
                  <span v-else-if="char.status === 'active'" class="active-text">
                    活跃中
                  </span>
                  <span v-else>
                    最近 {{ char.chapters }} 章出场
                  </span>
                </div>
              </div>
              <div class="char-status-dot" :class="char.status" />
            </div>
          </div>
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<style scoped>
.ai-inspector {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-surface);
}

.inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--app-divider);
}

.inspector-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.title-icon {
  color: #8b5cf6;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: var(--app-surface-subtle);
  border-radius: 6px;
  cursor: pointer;
  color: var(--app-text-muted);
  transition: all 0.18s ease;
}

.refresh-btn:hover {
  background: var(--color-brand-light);
  color: var(--color-brand);
}

.inspector-tabs {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.inspector-tabs :deep(.n-tabs-nav) {
  padding: 0 14px;
  flex-shrink: 0;
}

.inspector-tabs :deep(.n-tabs-panels) {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.inspector-tabs :deep(.n-tabs-tab) {
  padding: 10px 10px;
  font-size: 12px;
}

.tab-header-badge {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-content {
  padding: 14px;
}

/* Health Score */
.health-score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0 20px;
}

.health-ring {
  position: relative;
  width: 100px;
  height: 100px;
  margin-bottom: 12px;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: var(--app-divider);
  stroke-width: 8;
}

.ring-progress {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dasharray 0.6s ease;
}

.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.ring-label {
  font-size: 11px;
  color: var(--app-text-muted);
  margin-top: 4px;
}

.health-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--app-text-secondary);
}

/* Score List */
.score-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--app-divider);
}

.score-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.score-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-label {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.score-right .score-value {
  font-size: 14px;
  font-weight: 600;
}

/* Stat Block */
.stat-block {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--app-divider);
}

.stat-block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.stat-block-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.foreshadow-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.foreshadow-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--app-text-muted);
}

.rate-text {
  font-weight: 600;
  color: #8b5cf6;
}

/* Risk List */
.risk-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.18s ease;
}

.risk-item:hover {
  background: var(--app-surface-subtle);
}

.risk-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.risk-item.warning .risk-icon {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.risk-item.danger .risk-icon {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.risk-item.info .risk-icon {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.risk-content {
  flex: 1;
  min-width: 0;
}

.risk-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--app-text-primary);
  line-height: 1.4;
}

.risk-detail {
  font-size: 11px;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.risk-arrow {
  color: var(--app-text-muted);
  flex-shrink: 0;
  margin-top: 4px;
}

/* Suggestions */
.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
}

.suggestion-btn:hover {
  border-color: var(--sug-color);
  background: color-mix(in srgb, var(--sug-color) 5%, transparent);
}

.sug-icon {
  color: var(--sug-color);
  flex-shrink: 0;
}

.sug-text {
  flex: 1;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.sug-arrow {
  color: var(--app-text-muted);
  flex-shrink: 0;
}

/* Character List */
.char-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.char-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
}

.char-item:hover {
  background: var(--app-surface-subtle);
}

.char-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  background: var(--color-brand-light);
  color: var(--color-brand);
  flex-shrink: 0;
}

.char-avatar.inactive {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.char-avatar.active {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.char-info {
  flex: 1;
  min-width: 0;
}

.char-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.char-meta {
  font-size: 11px;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.inactive-text {
  color: var(--color-warning);
}

.active-text {
  color: var(--color-success);
}

.char-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.char-status-dot.active {
  background: var(--color-success);
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.char-status-dot.normal {
  background: var(--color-info);
}

.char-status-dot.inactive {
  background: var(--color-warning);
}

.badge-placeholder {
  display: none;
}
</style>
