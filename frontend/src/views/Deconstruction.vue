<template>
  <div class="deconstruction-page">
    <n-page-header title="📖 爆款拆书" subtitle="AI 逐章拆解爆款小说，提取可复用的创作模板">
      <template #header-extra>
        <n-button @click="goMarket">返回市场</n-button>
      </template>
    </n-page-header>

    <n-card style="margin-top: 16px" title="拆解新小说">
      <n-space>
        <n-input-group>
          <n-input-group-label>平台</n-input-group-label>
          <n-select v-model:value="platform" :options="platformOptions" style="width: 120px" />
        </n-input-group>
        <n-input v-model:value="bookId" placeholder="输入小说ID" style="width: 240px" />
        <n-button type="primary" :loading="loading" @click="runDeconstruction">
          开始拆解
        </n-button>
      </n-space>
    </n-card>

    <!-- 拆书列表 -->
    <n-card style="margin-top: 16px" title="已拆解的小说">
      <n-empty v-if="!deconstructions.length" description="暂无拆书记录" />
      <n-list v-else>
        <n-list-item v-for="d in deconstructions" :key="d.deconstruction_id">
          <n-thing
            :title="d.novel_name"
            :description="`${d.author} · ${d.platform} · ${d.category}`"
          >
            <template #header-extra>
              <n-space>
                <n-tag>分析 {{ d.analyzed_chapters }} 章</n-tag>
                <n-tag>{{ (d.total_word_count / 10000).toFixed(1) }}万字</n-tag>
                <n-button size="small" @click="viewDetail(d.deconstruction_id)">
                  查看详情
                </n-button>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
    </n-card>

    <!-- 拆书详情抽屉 -->
    <n-drawer v-model:show="showDetail" :width="900" placement="right">
      <n-drawer-content v-if="currentDetail" :title="currentDetail.novel_name" closable>
        <!-- AI 总结 -->
        <n-card v-if="currentDetail.ai_summary" type="info" title="📝 AI 综合评价" class="section">
          <p>{{ currentDetail.ai_summary }}</p>
        </n-card>

        <!-- 为什么火 -->
        <n-card v-if="currentDetail.ai_strengths" type="success" title="🔥 为什么火" class="section">
          <p style="white-space: pre-wrap">{{ currentDetail.ai_strengths }}</p>
        </n-card>

        <!-- 爆款DNA -->
        <n-card v-if="currentDetail.dna" title="🧬 爆款 DNA" class="section">
          <n-descriptions :column="1" bordered>
            <n-descriptions-item label="核心卖点">
              {{ currentDetail.dna.core_selling_point }}
            </n-descriptions-item>
            <n-descriptions-item label="目标读者">
              {{ currentDetail.dna.target_audience }}
            </n-descriptions-item>
            <n-descriptions-item label="情感共鸣">
              {{ currentDetail.dna.emotional_resonance }}
            </n-descriptions-item>
            <n-descriptions-item label="可复制性">
              <n-progress type="line" :percentage="currentDetail.dna.replication_score" />
            </n-descriptions-item>
            <n-descriptions-item label="难度">
              <n-tag :type="getDifficultyType(currentDetail.dna.difficulty_level)">
                {{ currentDetail.dna.difficulty_level }}
              </n-tag>
            </n-descriptions-item>
          </n-descriptions>

          <n-divider />

          <n-space vertical>
            <n-text strong>开局模板：</n-text>
            <n-card embedded>{{ currentDetail.dna.opening_template }}</n-card>

            <n-text strong>节奏公式：</n-text>
            <n-card embedded>{{ currentDetail.dna.pacing_formula }}</n-card>

            <n-text strong>爽点公式：</n-text>
            <n-card embedded>{{ currentDetail.dna.cool_point_formula }}</n-card>

            <n-text strong>冲突公式：</n-text>
            <n-card embedded>{{ currentDetail.dna.conflict_formula }}</n-card>

            <n-text strong>人物公式：</n-text>
            <n-card embedded>{{ currentDetail.dna.character_formula }}</n-card>
          </n-space>
        </n-card>

        <!-- 章节节奏表 -->
        <n-card v-if="currentDetail.chapter_beats?.length" title="📊 章节节奏分析" class="section">
          <n-data-table
            :columns="chapterColumns"
            :data="currentDetail.chapter_beats"
            :pagination="{ pageSize: 10 }"
            size="small"
          />
        </n-card>

        <!-- 人物模型 -->
        <n-card v-if="currentDetail.characters?.length" title="👥 人物模型" class="section">
          <n-grid :cols="2" :x-gap="12">
            <n-gi v-for="ch in currentDetail.characters" :key="ch.name">
              <n-card embedded>
                <template #header>
                  <n-space>
                    <n-text strong>{{ ch.name }}</n-text>
                    <n-tag size="small">{{ ch.role }}</n-tag>
                    <n-tag v-if="ch.archetype" size="small" type="info">{{ ch.archetype }}</n-tag>
                  </n-space>
                </template>
                <n-descriptions :column="1" size="small">
                  <n-descriptions-item label="性格">{{ ch.personality_traits?.join(', ') }}</n-descriptions-item>
                  <n-descriptions-item label="动机">{{ ch.motivation }}</n-descriptions-item>
                  <n-descriptions-item label="目标">{{ ch.goal }}</n-descriptions-item>
                  <n-descriptions-item label="缺陷">{{ ch.flaw }}</n-descriptions-item>
                  <n-descriptions-item label="成长">{{ ch.growth_arc }}</n-descriptions-item>
                  <n-descriptions-item label="首次登场">第{{ ch.first_appearance_chapter }}章</n-descriptions-item>
                </n-descriptions>
              </n-card>
            </n-gi>
          </n-grid>
        </n-card>

        <!-- 剧情结构 -->
        <n-card v-if="currentDetail.plot_structure?.length" title="📖 剧情结构" class="section">
          <n-timeline>
            <n-timeline-item
              v-for="ps in currentDetail.plot_structure"
              :key="ps.act"
              :type="getActType(ps.act)"
              :title="ps.act"
              :content="`${ps.description}\n关键事件: ${ps.key_events?.join(', ')}`"
              :time="`第${ps.start_chapter}-${ps.end_chapter}章`"
            />
          </n-timeline>
        </n-card>

        <!-- 金手指 -->
        <n-card v-if="currentDetail.golden_fingers?.length" title="⚡ 金手指分析" class="section">
          <n-list>
            <n-list-item v-for="gf in currentDetail.golden_fingers" :key="gf.name">
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

        <!-- 爽点分布 -->
        <n-card v-if="currentDetail.cool_points?.length" title="🎉 爽点分布" class="section">
          <n-list>
            <n-list-item v-for="cp in currentDetail.cool_points" :key="cp.cool_point_type">
              <n-thing :title="cp.cool_point_type">
                <n-space>
                  <n-tag>出现 {{ cp.total_count }} 次</n-tag>
                  <n-tag>频率: {{ cp.frequency }}</n-tag>
                  <n-tag>平均强度: {{ cp.avg_intensity }}</n-tag>
                </n-space>
                <n-text depth="3" style="margin-top: 8px">{{ cp.description }}</n-text>
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>

        <!-- 冲突设计 -->
        <n-card v-if="currentDetail.conflicts?.length" title="⚔️ 冲突设计" class="section">
          <n-list>
            <n-list-item v-for="cf in currentDetail.conflicts" :key="cf.conflict_type">
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

        <!-- 可复用元素 -->
        <n-card v-if="currentDetail.ai_replicable_elements" title="✅ 可复用元素" class="section">
          <p style="white-space: pre-wrap">{{ currentDetail.ai_replicable_elements }}</p>
        </n-card>

        <!-- 不足 -->
        <n-card v-if="currentDetail.ai_weaknesses" type="warning" title="⚠️ 不足之处" class="section">
          <p style="white-space: pre-wrap">{{ currentDetail.ai_weaknesses }}</p>
        </n-card>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { marketApi } from '@/api/market'

const router = useRouter()
const message = useMessage()

const platform = ref('fanqie')
const bookId = ref('')
const loading = ref(false)
const deconstructions = ref([])
const showDetail = ref(false)
const currentDetail = ref(null)

const platformOptions = [
  { label: '番茄小说', value: 'fanqie' },
  { label: '起点中文网', value: 'qidian' },
  { label: '七猫小说', value: 'qimao' },
]

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

onMounted(() => {
  loadDeconstructions()
})

async function loadDeconstructions() {
  try {
    const res = await marketApi.listDeconstructions()
    deconstructions.value = res
  } catch (e) {
    console.error(e)
  }
}

async function runDeconstruction() {
  if (!bookId.value) {
    message.warning('请输入小说ID')
    return
  }
  loading.value = true
  try {
    const res = await marketApi.deconstructNovel({
      platform: platform.value,
      book_id: bookId.value,
    })
    message.success('拆解完成')
    deconstructions.value.unshift({
      deconstruction_id: res.deconstruction_id,
      novel_name: res.novel_name,
      author: res.author,
      platform: res.platform,
      category: res.category,
      analyzed_chapters: res.analyzed_chapters,
      total_word_count: res.total_word_count,
      created_at: new Date().toISOString(),
    })
    currentDetail.value = res
    showDetail.value = true
  } catch (e) {
    message.error(`拆解失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

async function viewDetail(id) {
  try {
    const res = await marketApi.getDeconstruction(id)
    currentDetail.value = res
    showDetail.value = true
  } catch (e) {
    message.error('获取详情失败')
  }
}

function goMarket() {
  router.push('/market')
}

function getActType(act) {
  const map = { 'Act1': 'info', 'Act2a': 'warning', 'Act2b': 'success', 'Act3': 'error' }
  return map[act] || 'default'
}

function getDifficultyType(level) {
  const map = { '简单': 'success', '中等': 'warning', '困难': 'error' }
  return map[level] || 'default'
}
</script>

<style scoped>
.deconstruction-page {
  padding: 16px;
}
.section {
  margin-bottom: 16px;
}
</style>
