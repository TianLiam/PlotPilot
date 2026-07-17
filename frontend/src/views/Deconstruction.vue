<template>
  <div class="deconstruction-page">
    <MarketSectionHeader
      title="作品拆解"
      subtitle="用真实作品样本拆出开局、节奏、爽点与钩子结构，结论进入模板库，而不是停在一份读后感里。"
    >
      <template #actions>
        <n-tag :bordered="false" type="info">{{ deconstructions.length }} 份拆解档案</n-tag>
      </template>
    </MarketSectionHeader>

    <main class="deconstruction-content">
      <section class="deconstruction-workspace">
        <div class="deconstruction-brief">
          <span class="brief-index">DECONSTRUCT / 01</span>
          <h2>先锁定样本，再提取可复用结构。</h2>
          <p>输入平台作品 ID 后，系统会抓取可访问章节并生成分章节节奏、冲突、爽点和钩子分析。</p>
          <div class="brief-note">
            <strong>建议</strong>
            <span>优先选择目标题材近 30 天的高排名作品，样本更接近当前市场。</span>
          </div>
        </div>

        <n-card :bordered="false" class="deconstruction-form">
          <span class="form-step">STEP 01</span>
          <h3>创建新的拆解任务</h3>
          <p>选择来源平台并填写作品 ID。拆解会调用正文抓取与模型分析，请确认模型配置可用。</p>

          <div class="deconstruction-fields">
            <n-select
              v-model:value="platform"
              :options="platformOptions"
              aria-label="作品平台"
              class="platform-select"
            />
            <n-input
              v-model:value="bookId"
              clearable
              placeholder="输入平台作品 ID"
              aria-label="作品 ID"
              @keyup.enter="runDeconstruction"
            />
            <n-button type="primary" :loading="loading" @click="runDeconstruction">
              开始拆解
            </n-button>
          </div>
        </n-card>
      </section>

      <section class="archive-section">
        <div class="archive-heading">
          <div>
            <span class="archive-eyebrow">DECONSTRUCTION ARCHIVE</span>
            <h2>拆解档案</h2>
          </div>
          <n-button quaternary :loading="archiveLoading" @click="loadDeconstructions">刷新档案</n-button>
        </div>

        <div v-if="deconstructions.length" class="archive-grid">
          <article v-for="item in deconstructions" :key="item.deconstruction_id" class="archive-card">
            <div class="archive-card-top">
              <span>{{ platformLabel(item.platform) }}</span>
              <n-tag size="small" :bordered="false">{{ item.category || '未分类' }}</n-tag>
            </div>
            <h3>{{ item.novel_name || '未命名作品' }}</h3>
            <p>{{ item.author || '作者未知' }}</p>
            <div class="archive-metrics">
              <div><strong>{{ item.analyzed_chapters || 0 }}</strong><span>分析章节</span></div>
              <div><strong>{{ formatWordCount(item.total_word_count) }}</strong><span>样本字数</span></div>
            </div>
            <n-button type="primary" secondary block @click="goDetail(item.deconstruction_id)">
              查看完整拆解
            </n-button>
          </article>
        </div>

        <div v-else class="archive-empty">
          <span class="empty-index">00</span>
          <div>
            <h3>还没有拆解档案</h3>
            <p>完成第一份拆解后，这里会保存作品结构、分章节节奏与可复用 DNA。</p>
          </div>
          <div class="empty-steps">
            <span>选择对标作品</span>
            <i>→</i>
            <span>抓取可用章节</span>
            <i>→</i>
            <span>沉淀创作模板</span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import MarketSectionHeader from '@/components/market/MarketSectionHeader.vue'
import { marketApi } from '@/api/market'

type DeconstructionRecord = {
  deconstruction_id: string
  novel_name: string
  author: string
  platform: string
  category: string
  analyzed_chapters: number
  total_word_count: number
  created_at?: string
}

const router = useRouter()
const message = useMessage()
const platform = ref('fanqie')
const bookId = ref('')
const loading = ref(false)
const archiveLoading = ref(false)
const deconstructions = ref<DeconstructionRecord[]>([])

const platformOptions = [
  { label: '番茄小说', value: 'fanqie' },
  { label: '起点中文网', value: 'qidian' },
  { label: '七猫小说', value: 'qimao' },
]

async function loadDeconstructions(): Promise<void> {
  archiveLoading.value = true
  try {
    deconstructions.value = await marketApi.listDeconstructions() as DeconstructionRecord[]
  } catch (error) {
    console.error('Failed to load deconstruction archive:', error)
    message.error('拆解档案加载失败')
  } finally {
    archiveLoading.value = false
  }
}

async function runDeconstruction(): Promise<void> {
  if (!bookId.value.trim()) {
    message.warning('请输入作品 ID')
    return
  }

  loading.value = true
  try {
    const result = await marketApi.deconstructNovel({
      platform: platform.value,
      book_id: bookId.value.trim(),
    })
    message.success('作品拆解完成')
    bookId.value = ''
    await loadDeconstructions()
    if (result?.deconstruction_id) goDetail(result.deconstruction_id)
  } catch (error) {
    const detail = error instanceof Error ? error.message : '未知错误'
    message.error(`拆解失败：${detail}`)
  } finally {
    loading.value = false
  }
}

function goDetail(id: string): void {
  router.push(`/market/deconstruction/${id}`)
}

function formatWordCount(value?: number): string {
  const count = Number(value || 0)
  return count >= 10000 ? `${(count / 10000).toFixed(1)} 万` : String(count)
}

function platformLabel(value: string): string {
  return platformOptions.find(item => item.value === value)?.label || value || '未知平台'
}

onMounted(loadDeconstructions)
</script>

<style scoped>
.deconstruction-page {
  min-height: calc(100vh - 60px);
  background: var(--app-page-bg);
}

.deconstruction-content {
  width: min(1240px, calc(100% - 48px));
  margin: 0 auto;
  padding: 26px 0 52px;
}

.deconstruction-workspace {
  display: grid;
  grid-template-columns: minmax(280px, 0.82fr) minmax(0, 1.55fr);
  gap: 18px;
}

.deconstruction-brief,
.deconstruction-form,
.archive-section {
  border: 1px solid var(--app-border);
  border-radius: 20px;
  background: var(--app-surface);
}

.deconstruction-brief {
  padding: clamp(24px, 3vw, 34px);
  background:
    radial-gradient(circle at 100% 0, rgba(249, 115, 22, 0.18), transparent 40%),
    var(--app-surface);
}

.brief-index,
.archive-eyebrow,
.form-step {
  color: #f97316;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.deconstruction-brief h2 {
  margin: 18px 0 10px;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: clamp(24px, 2.8vw, 34px);
  line-height: 1.25;
}

.deconstruction-brief > p,
.deconstruction-form > p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 12px;
  line-height: 1.75;
}

.brief-note {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 28px;
  padding-top: 18px;
  border-top: 1px solid var(--app-border);
  color: var(--app-text-muted);
  font-size: 11px;
}

.brief-note strong {
  color: var(--app-text-primary);
}

.deconstruction-form {
  padding: clamp(24px, 3vw, 34px);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.045);
}

.deconstruction-form h3 {
  margin: 12px 0 8px;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 22px;
}

.deconstruction-fields {
  display: grid;
  grid-template-columns: 150px minmax(180px, 1fr) auto;
  gap: 10px;
  margin-top: 30px;
}

.archive-section {
  margin-top: 18px;
  padding: clamp(22px, 3vw, 32px);
}

.archive-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
}

.archive-heading h2 {
  margin: 7px 0 0;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: 22px;
}

.archive-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.archive-card {
  padding: 20px;
  border: 1px solid var(--app-border);
  border-radius: 15px;
  background: var(--app-surface-subtle);
}

.archive-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: var(--app-text-muted);
  font-size: 10px;
}

.archive-card h3 {
  margin: 20px 0 4px;
  color: var(--app-text-primary);
  font-size: 16px;
}

.archive-card > p {
  margin: 0;
  color: var(--app-text-muted);
  font-size: 11px;
}

.archive-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin: 18px 0;
}

.archive-metrics div {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 10px;
  border-radius: 10px;
  background: var(--app-surface);
}

.archive-metrics strong {
  color: var(--app-text-primary);
  font-family: var(--font-mono);
  font-size: 15px;
}

.archive-metrics span {
  color: var(--app-text-muted);
  font-size: 9px;
}

.archive-empty {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 22px;
  min-height: 190px;
  padding: 28px;
  border: 1px dashed rgba(100, 116, 139, 0.35);
  border-radius: 15px;
  background: var(--app-surface-subtle);
}

.empty-index {
  color: #cbd5e1;
  font-family: Georgia, serif;
  font-size: 44px;
  font-weight: 800;
}

.archive-empty h3 {
  margin: 0;
  color: var(--app-text-primary);
}

.archive-empty p {
  max-width: 500px;
  margin: 7px 0 0;
  color: var(--app-text-muted);
  font-size: 11px;
}

.empty-steps {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--app-text-secondary);
  font-size: 10px;
}

.empty-steps i {
  color: #cbd5e1;
  font-style: normal;
}

@media (max-width: 900px) {
  .deconstruction-workspace,
  .archive-grid {
    grid-template-columns: 1fr;
  }

  .archive-empty {
    grid-template-columns: auto 1fr;
  }

  .empty-steps {
    grid-column: 1 / -1;
  }
}

@media (max-width: 620px) {
  .deconstruction-content {
    width: min(100% - 28px, 1240px);
    padding: 18px 0 36px;
  }

  .deconstruction-fields,
  .archive-empty {
    grid-template-columns: 1fr;
  }

  .empty-steps {
    align-items: flex-start;
    flex-direction: column;
  }

  .empty-steps i {
    display: none;
  }
}
</style>
