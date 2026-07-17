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
                <n-button size="small" type="primary" @click="goDetail(d.deconstruction_id)">
                  查看详情 →
                </n-button>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
    </n-card>
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
    deconstructions.value.forEach(d => {
      if (d.deconstruction_id === id) {
        Object.assign(d, res)
      }
    })
  } catch (e) {
    message.error('获取详情失败')
  }
}

function goDetail(id) {
  router.push(`/market/deconstruction/${id}`)
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
