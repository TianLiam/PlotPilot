<template>
  <div class="deconstruction-detail-page">
    <div class="detail-header">
      <div class="header-inner">
        <div class="header-left">
          <n-button @click="goBack">
            <template #icon><n-icon><IconArrowLeft /></n-icon></template>
            返回列表
          </n-button>
          <div class="header-title">
            <h1>{{ detail.novel_name }}</h1>
            <p>{{ detail.author }} · {{ detail.platform }} · {{ detail.category }}</p>
          </div>
        </div>
        <div class="header-right">
          <n-space>
            <n-tag>{{ detail.analyzed_chapters }} 章</n-tag>
            <n-tag>{{ (detail.total_word_count / 10000).toFixed(1) }}万字</n-tag>
            <n-button type="primary" @click="saveAsTemplate">
              <template #icon><n-icon><IconSave /></n-icon></template>
              保存为模板
            </n-button>
          </n-space>
        </div>
      </div>
    </div>

    <div class="detail-content">
      <aside class="detail-sidebar">
        <div class="sidebar-section">
          <div class="sidebar-title">导航</div>
          <div class="nav-tree">
            <div
              v-for="item in navItems"
              :key="item.key"
              class="nav-item"
              :class="{ 'is-active': activeTab === item.key }"
              @click="activeTab = item.key"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span class="nav-label">{{ item.label }}</span>
            </div>
          </div>
        </div>

        <div v-if="detail.chapter_beats?.length" class="sidebar-section">
          <div class="sidebar-title">章节拆解</div>
          <div class="chapter-tree">
            <div
              v-for="(beat, idx) in displayChapters"
              :key="beat.chapter_number"
              class="chapter-item"
              :class="{ 'is-active': selectedChapter === beat.chapter_number }"
              @click="selectChapter(beat.chapter_number)"
            >
              <span class="chapter-num">{{ beat.chapter_number }}</span>
              <span class="chapter-title">{{ beat.title }}</span>
              <span class="chapter-pace" :class="`pace-${beat.pacing}`">{{ beat.pacing }}</span>
            </div>
            <div v-if="detail.chapter_beats.length > 20" class="chapter-more">
              <n-button text size="small" @click="showAllChapters = !showAllChapters">
                {{ showAllChapters ? '收起' : `展开全部 ${detail.chapter_beats.length} 章` }}
              </n-button>
            </div>
          </div>
        </div>

        <div v-if="detail.dna" class="sidebar-section">
          <div class="sidebar-title">爆款DNA概览</div>
          <div class="dna-summary">
            <div class="dna-item">
              <span class="dna-label">核心卖点</span>
              <span class="dna-value">{{ detail.dna.core_selling_point }}</span>
            </div>
            <div class="dna-item">
              <span class="dna-label">目标读者</span>
              <span class="dna-value">{{ detail.dna.target_audience }}</span>
            </div>
            <div class="dna-item">
              <span class="dna-label">复制难度</span>
              <n-tag :type="getDifficultyType(detail.dna.difficulty_level)">
                {{ detail.dna.difficulty_level }}
              </n-tag>
            </div>
          </div>
        </div>
      </aside>

      <main class="detail-main">
        <transition name="fade" mode="out-in">
          <div v-if="activeTab === 'summary'" key="summary" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>📝 AI 综合评价</template>
              <p>{{ detail.ai_summary }}</p>
            </n-card>

            <n-card :bordered="false" class="tab-card">
              <template #header>🔥 为什么火</template>
              <p style="white-space: pre-wrap">{{ detail.ai_strengths }}</p>
            </n-card>

            <n-card :bordered="false" class="tab-card">
              <template #header>✅ 可复用元素</template>
              <p style="white-space: pre-wrap">{{ detail.ai_replicable_elements }}</p>
            </n-card>

            <n-card :bordered="false" class="tab-card" type="warning">
              <template #header>⚠️ 不足之处</template>
              <p style="white-space: pre-wrap">{{ detail.ai_weaknesses }}</p>
            </n-card>
          </div>

          <div v-else-if="activeTab === 'dna'" key="dna" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>🧬 爆款 DNA</template>
              <n-descriptions :column="2" bordered size="small">
                <n-descriptions-item label="核心卖点">
                  {{ detail.dna.core_selling_point }}
                </n-descriptions-item>
                <n-descriptions-item label="目标读者">
                  {{ detail.dna.target_audience }}
                </n-descriptions-item>
                <n-descriptions-item label="情感共鸣">
                  {{ detail.dna.emotional_resonance }}
                </n-descriptions-item>
                <n-descriptions-item label="可复制性">
                  <n-progress type="line" :percentage="detail.dna.replication_score" />
                </n-descriptions-item>
                <n-descriptions-item label="难度">
                  <n-tag :type="getDifficultyType(detail.dna.difficulty_level)">
                    {{ detail.dna.difficulty_level }}
                  </n-tag>
                </n-descriptions-item>
              </n-descriptions>

              <n-divider />

              <n-space vertical size="medium">
                <div class="formula-card">
                  <div class="formula-label">开局模板</div>
                  <div class="formula-content">{{ detail.dna.opening_template }}</div>
                </div>
                <div class="formula-card">
                  <div class="formula-label">节奏公式</div>
                  <div class="formula-content">{{ detail.dna.pacing_formula }}</div>
                </div>
                <div class="formula-card">
                  <div class="formula-label">爽点公式</div>
                  <div class="formula-content">{{ detail.dna.cool_point_formula }}</div>
                </div>
                <div class="formula-card">
                  <div class="formula-label">冲突公式</div>
                  <div class="formula-content">{{ detail.dna.conflict_formula }}</div>
                </div>
                <div class="formula-card">
                  <div class="formula-label">人物公式</div>
                  <div class="formula-content">{{ detail.dna.character_formula }}</div>
                </div>
              </n-space>
            </n-card>
          </div>

          <div v-else-if="activeTab === 'chapters'" key="chapters" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>
                <div class="card-header">
                  <span>📊 章节节奏分析</span>
                  <span v-if="selectedChapter" class="selected-info">
                    选中：第 {{ selectedChapter }} 章
                  </span>
                </div>
              </template>
              <n-data-table
                :columns="chapterColumns"
                :data="detail.chapter_beats"
                :pagination="{ pageSize: 10 }"
                size="small"
                :row-class-name="(row) => ({
                  'row-selected': row.chapter_number === selectedChapter,
                })"
                @row-click="(row) => selectChapter(row.chapter_number)"
              />
            </n-card>

            <n-card v-if="selectedChapterDetail" :bordered="false" class="tab-card">
              <template #header>第 {{ selectedChapter }} 章 · {{ selectedChapterDetail.title }}</template>
              <n-descriptions :column="2" bordered size="small">
                <n-descriptions-item label="节奏">
                  <n-tag :type="getPaceType(selectedChapterDetail.pacing)">
                    {{ selectedChapterDetail.pacing }}
                  </n-tag>
                  <span class="score">{{ selectedChapterDetail.pacing_score }}分</span>
                </n-descriptions-item>
                <n-descriptions-item label="情绪">
                  <n-tag>{{ selectedChapterDetail.emotion }}</n-tag>
                </n-descriptions-item>
                <n-descriptions-item label="爽点类型">{{ selectedChapterDetail.cool_point_type }}</n-descriptions-item>
                <n-descriptions-item label="爽点强度">{{ selectedChapterDetail.cool_point_intensity }}</n-descriptions-item>
                <n-descriptions-item label="冲突类型">{{ selectedChapterDetail.conflict_type }}</n-descriptions-item>
                <n-descriptions-item label="钩子类型">{{ selectedChapterDetail.hook_type }}</n-descriptions-item>
              </n-descriptions>
              <n-divider />
              <n-text strong>章节分析：</n-text>
              <p style="white-space: pre-wrap">{{ selectedChapterDetail.analysis }}</p>
            </n-card>
          </div>

          <div v-else-if="activeTab === 'characters'" key="characters" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>👥 人物模型</template>
              <n-grid :cols="2" :x-gap="12">
                <n-gi v-for="ch in detail.characters" :key="ch.name">
                  <div class="character-card">
                    <div class="character-header">
                      <span class="character-name">{{ ch.name }}</span>
                      <n-tag size="small">{{ ch.role }}</n-tag>
                      <n-tag v-if="ch.archetype" size="small" type="info">{{ ch.archetype }}</n-tag>
                    </div>
                    <n-descriptions :column="2" size="small">
                      <n-descriptions-item label="性格">{{ ch.personality_traits?.join(', ') }}</n-descriptions-item>
                      <n-descriptions-item label="动机">{{ ch.motivation }}</n-descriptions-item>
                      <n-descriptions-item label="目标">{{ ch.goal }}</n-descriptions-item>
                      <n-descriptions-item label="缺陷">{{ ch.flaw }}</n-descriptions-item>
                      <n-descriptions-item label="成长">{{ ch.growth_arc }}</n-descriptions-item>
                      <n-descriptions-item label="首次登场">第{{ ch.first_appearance_chapter }}章</n-descriptions-item>
                    </n-descriptions>
                  </div>
                </n-gi>
              </n-grid>
            </n-card>
          </div>

          <div v-else-if="activeTab === 'plot'" key="plot" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>📖 剧情结构</template>
              <n-timeline mode="left">
                <n-timeline-item
                  v-for="ps in detail.plot_structure"
                  :key="ps.act"
                  :type="getActType(ps.act)"
                  :title="ps.act"
                  :time="`第${ps.start_chapter}-${ps.end_chapter}章`"
                >
                  <p>{{ ps.description }}</p>
                  <n-tag v-for="event in ps.key_events" :key="event" size="small">
                    {{ event }}
                  </n-tag>
                </n-timeline-item>
              </n-timeline>
            </n-card>
          </div>

          <div v-else-if="activeTab === 'golden'" key="golden" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>⚡ 金手指分析</template>
              <n-list>
                <n-list-item v-for="gf in detail.golden_fingers" :key="gf.name">
                  <n-thing :title="gf.name" :description="gf.type">
                    <n-descriptions :column="2" size="small">
                      <n-descriptions-item label="觉醒章节">第{{ gf.awakening_chapter }}章</n-descriptions-item>
                      <n-descriptions-item label="初始能力">{{ gf.initial_power }}</n-descriptions-item>
                      <n-descriptions-item label="成长路径">{{ gf.growth_path }}</n-descriptions-item>
                      <n-descriptions-item label="使用频率">{{ gf.usage_frequency }}</n-descriptions-item>
                      <n-descriptions-item label="剧情驱动">
                        <n-tag :type="gf.plot_driver ? 'success' : 'default'">
                          {{ gf.plot_driver ? '是' : '否' }}
                        </n-tag>
                      </n-descriptions-item>
                      <n-descriptions-item label="爽点制造">
                        <n-tag :type="gf.cool_point_enabler ? 'success' : 'default'">
                          {{ gf.cool_point_enabler ? '是' : '否' }}
                        </n-tag>
                      </n-descriptions-item>
                    </n-descriptions>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-card>
          </div>

          <div v-else-if="activeTab === 'coolpoints'" key="coolpoints" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>🎉 爽点分布</template>
              <n-grid :cols="2" :x-gap="12">
                <n-gi v-for="cp in detail.cool_points" :key="cp.cool_point_type">
                  <div class="coolpoint-card">
                    <div class="coolpoint-header">
                      <span class="coolpoint-name">{{ cp.cool_point_type }}</span>
                      <n-tag type="success">出现 {{ cp.total_count }} 次</n-tag>
                    </div>
                    <n-space>
                      <n-tag>频率: {{ cp.frequency }}</n-tag>
                      <n-tag>强度: {{ cp.avg_intensity }}</n-tag>
                    </n-space>
                    <p style="margin-top: 8px">{{ cp.description }}</p>
                  </div>
                </n-gi>
              </n-grid>
            </n-card>
          </div>

          <div v-else-if="activeTab === 'conflicts'" key="conflicts" class="tab-content">
            <n-card :bordered="false" class="tab-card">
              <template #header>⚔️ 冲突设计</template>
              <n-list>
                <n-list-item v-for="cf in detail.conflicts" :key="cf.conflict_type">
                  <n-thing :title="cf.conflict_type">
                    <p>{{ cf.description }}</p>
                    <n-descriptions :column="2" size="small">
                      <n-descriptions-item label="升级模式">{{ cf.escalation_pattern }}</n-descriptions-item>
                      <n-descriptions-item label="解决方式">{{ cf.resolution_style }}</n-descriptions-item>
                    </n-descriptions>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-card>
          </div>
        </transition>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon, useMessage } from 'naive-ui'
import { marketApi } from '@/api/market'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const IconArrowLeft = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z' }))

const IconSave = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z' }))

const detail = ref<any>(null)
const activeTab = ref('summary')
const selectedChapter = ref<number | null>(null)
const showAllChapters = ref(false)

const navItems = [
  { key: 'summary', label: '综合评价', icon: '📝' },
  { key: 'dna', label: '爆款DNA', icon: '🧬' },
  { key: 'chapters', label: '章节节奏', icon: '📊' },
  { key: 'characters', label: '人物模型', icon: '👥' },
  { key: 'plot', label: '剧情结构', icon: '📖' },
  { key: 'golden', label: '金手指', icon: '⚡' },
  { key: 'coolpoints', label: '爽点分布', icon: '🎉' },
  { key: 'conflicts', label: '冲突设计', icon: '⚔️' },
]

const displayChapters = computed(() => {
  if (showAllChapters.value) return detail.value?.chapter_beats || []
  return (detail.value?.chapter_beats || []).slice(0, 20)
})

const selectedChapterDetail = computed(() => {
  if (!selectedChapter.value) return null
  return detail.value?.chapter_beats?.find(
    (b: any) => b.chapter_number === selectedChapter.value
  )
})

const chapterColumns = [
  { title: '章', key: 'chapter_number', width: 50 },
  { title: '标题', key: 'title', width: 150 },
  { title: '节奏', key: 'pacing', width: 80 },
  { title: '节奏分', key: 'pacing_score', width: 70 },
  { title: '情绪', key: 'emotion', width: 80 },
  { title: '爽点', key: 'cool_point_type', width: 100 },
  { title: '强度', key: 'cool_point_intensity', width: 60 },
  { title: '冲突', key: 'conflict_type', width: 80 },
  { title: '钩子', key: 'hook_type', width: 80 },
]

onMounted(async () => {
  const id = route.params.id
  if (id) {
    await loadDetail(id as string)
  }
})

async function loadDetail(id: string) {
  try {
    detail.value = await marketApi.getDeconstruction(id)
  } catch (e) {
    message.error('加载失败')
    router.push('/market/deconstruction')
  }
}

function selectChapter(num: number) {
  selectedChapter.value = num
  activeTab.value = 'chapters'
}

function goBack() {
  router.push('/market/deconstruction')
}

async function saveAsTemplate() {
  try {
    await marketApi.useTemplate(detail.value.deconstruction_id)
    message.success('已保存到模板库')
  } catch {
    message.error('保存失败')
  }
}

function getActType(act: string) {
  const map: Record<string, string> = { Act1: 'info', Act2a: 'warning', Act2b: 'success', Act3: 'error' }
  return map[act] || 'default'
}

function getDifficultyType(level: string) {
  const map: Record<string, string> = { '简单': 'success', '中等': 'warning', '困难': 'error' }
  return map[level] || 'default'
}

function getPaceType(pace: string) {
  const map: Record<string, string> = { '快': 'success', '中': 'default', '慢': 'warning' }
  return map[pace] || 'default'
}
</script>

<style scoped>
.deconstruction-detail-page {
  min-height: calc(100vh - 60px);
  background: var(--app-page-bg);
}

.detail-header {
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  padding: 0 24px;
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1600px;
  margin: 0 auto;
  padding: 16px 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title h1 {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text-primary);
}

.header-title p {
  margin: 0;
  font-size: 13px;
  color: var(--app-text-muted);
}

.detail-content {
  display: flex;
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
  gap: 20px;
}

.detail-sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-section {
  background: var(--app-surface);
  border-radius: 12px;
  border: 1px solid var(--app-border);
  padding: 14px;
}

.sidebar-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.nav-tree {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--app-text-secondary);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: var(--app-surface-subtle);
}

.nav-item.is-active {
  background: var(--color-brand-light);
  color: var(--color-brand);
  font-weight: 600;
}

.nav-icon {
  font-size: 14px;
}

.chapter-tree {
  max-height: 300px;
  overflow-y: auto;
}

.chapter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.chapter-item:hover {
  background: var(--app-surface-subtle);
}

.chapter-item.is-active {
  background: var(--color-brand-light);
}

.chapter-num {
  width: 24px;
  text-align: center;
  font-weight: 600;
  color: var(--app-text-secondary);
}

.chapter-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--app-text-primary);
}

.chapter-pace {
  font-size: 10px;
  padding: 2px 5px;
  border-radius: 4px;
}

.pace-快 { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.pace-中 { background: rgba(148, 163, 184, 0.15); color: #64748b; }
.pace-慢 { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }

.chapter-more {
  padding: 8px 0;
  text-align: center;
}

.dna-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dna-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dna-label {
  font-size: 11px;
  color: var(--app-text-muted);
}

.dna-value {
  font-size: 13px;
  color: var(--app-text-primary);
  font-weight: 500;
}

.detail-main {
  flex: 1;
  min-width: 0;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tab-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.tab-card :deep(.n-card-header) {
  font-size: 15px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-info {
  font-size: 12px;
  color: var(--color-brand);
}

.row-selected {
  background: var(--color-brand-light) !important;
}

.formula-card {
  background: var(--app-surface-subtle);
  border-radius: 8px;
  padding: 12px;
}

.formula-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text-secondary);
  margin-bottom: 6px;
}

.formula-content {
  font-size: 13px;
  color: var(--app-text-primary);
  white-space: pre-wrap;
}

.character-card {
  background: var(--app-surface-subtle);
  border-radius: 10px;
  padding: 14px;
}

.character-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.character-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.coolpoint-card {
  background: var(--app-surface-subtle);
  border-radius: 10px;
  padding: 14px;
}

.coolpoint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.coolpoint-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.score {
  margin-left: 8px;
  font-size: 12px;
  color: var(--app-text-muted);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 900px) {
  .detail-content {
    flex-direction: column;
  }

  .detail-sidebar {
    width: 100%;
  }
}
</style>
