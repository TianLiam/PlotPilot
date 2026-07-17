<template>
  <section class="template-panel">
    <div class="template-panel-head">
      <div>
        <div class="template-title-row">
          <h2>{{ title }}</h2>
          <span class="template-count">{{ templates.length }} 个可用模板</span>
        </div>
        <p>{{ description }}</p>
      </div>

      <div class="template-controls">
        <n-select
          :value="modelValue"
          :options="genreOptions"
          aria-label="按题材筛选"
          class="genre-select"
          @update:value="updateGenre"
        />
        <n-button secondary :loading="loading" @click="emit('reload')">刷新列表</n-button>
      </div>
    </div>

    <n-spin :show="loading">
      <div v-if="templates.length" class="template-grid">
        <article v-for="item in templates" :key="item.id" class="template-item">
          <div class="template-item-head">
            <div class="template-source" :class="`is-${item.source || 'built_in'}`">
              {{ item.source === 'crawler' ? '榜单提炼' : '内置基线' }}
            </div>
            <n-tag size="small" :bordered="false">{{ item.genre || '通用' }}</n-tag>
          </div>

          <h3>{{ item.name }}</h3>
          <p class="template-description">{{ item.description || '该模板暂无摘要，可进入详情查看完整结构。' }}</p>

          <div v-if="item.tags?.length" class="template-tags">
            <span v-for="tag in item.tags.slice(0, 3)" :key="tag">{{ tag }}</span>
          </div>

          <div class="template-item-foot">
            <div class="template-metrics">
              <template v-if="item.source === 'crawler'">
                <span>置信度 {{ Math.round((item.confidence_score || 0) * 100) }}%</span>
                <span>命中 {{ item.occurrence_count || 1 }} 本</span>
              </template>
              <template v-else>
                <span>基线热度 {{ item.popularity }}</span>
                <span>{{ item.usage_count }} 次使用</span>
              </template>
            </div>
            <n-button type="primary" size="small" @click="emit('use', item)">查看并使用</n-button>
          </div>
        </article>
      </div>

      <div v-else class="template-empty">
        <span class="template-empty-index">00</span>
        <div>
          <h3>当前筛选下还没有模板</h3>
          <p>可以先查看全部题材，或从最新热门榜单启动一次自动提炼。</p>
        </div>
        <n-button type="primary" secondary @click="emit('discover')">从榜单自动提炼</n-button>
      </div>
    </n-spin>
  </section>
</template>

<script setup lang="ts">
import type { SelectOption } from 'naive-ui'
import type { Template } from '@/api/market'

defineProps<{
  title: string
  description: string
  templates: Template[]
  modelValue: string
  genreOptions: SelectOption[]
  loading: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  reload: []
  use: [template: Template]
  discover: []
}>()

function updateGenre(value: string | number | null): void {
  emit('update:modelValue', value == null ? '' : String(value))
}
</script>

<style scoped>
.template-panel {
  padding: clamp(20px, 3vw, 32px);
  border: 1px solid var(--app-border);
  border-radius: 20px;
  background: var(--app-surface);
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.045);
}

.template-panel-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.template-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.template-title-row h2 {
  margin: 0;
  color: var(--app-text-primary);
  font-family: "Noto Serif SC", "Source Han Serif SC", Georgia, serif;
  font-size: 21px;
}

.template-count {
  color: #6366f1;
  font-size: 11px;
  font-weight: 700;
}

.template-panel-head p {
  margin: 7px 0 0;
  color: var(--app-text-muted);
  font-size: 13px;
  line-height: 1.6;
}

.template-controls {
  display: flex;
  gap: 8px;
  flex: 0 0 auto;
}

.genre-select {
  width: 170px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.template-item {
  display: flex;
  min-height: 230px;
  flex-direction: column;
  padding: 20px;
  border: 1px solid var(--app-border);
  border-radius: 15px;
  background: linear-gradient(145deg, #fff, var(--app-surface-subtle));
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.template-item:hover {
  transform: translateY(-2px);
  border-color: rgba(79, 70, 229, 0.24);
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.07);
}

.template-item-head,
.template-item-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.template-source {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--app-text-muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.template-source::before {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #94a3b8;
  content: "";
}

.template-source.is-crawler {
  color: #047857;
}

.template-source.is-crawler::before {
  background: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.template-item h3 {
  margin: 18px 0 8px;
  color: var(--app-text-primary);
  font-size: 17px;
  line-height: 1.35;
}

.template-description {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--app-text-secondary);
  font-size: 13px;
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 14px;
}

.template-tags span {
  padding: 3px 8px;
  border-radius: 99px;
  background: rgba(79, 70, 229, 0.07);
  color: #4f46e5;
  font-size: 10px;
}

.template-item-foot {
  align-items: flex-end;
  margin-top: auto;
  padding-top: 18px;
}

.template-metrics {
  display: flex;
  flex-direction: column;
  gap: 3px;
  color: var(--app-text-muted);
  font-size: 11px;
}

.template-empty {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 20px;
  min-height: 190px;
  padding: 28px;
  border: 1px dashed rgba(100, 116, 139, 0.35);
  border-radius: 15px;
  background: var(--app-surface-subtle);
}

.template-empty-index {
  color: #cbd5e1;
  font-family: Georgia, serif;
  font-size: 42px;
  font-weight: 800;
}

.template-empty h3 {
  margin: 0;
  color: var(--app-text-primary);
  font-size: 15px;
}

.template-empty p {
  margin: 6px 0 0;
  color: var(--app-text-muted);
  font-size: 12px;
}

@media (max-width: 760px) {
  .template-panel-head,
  .template-controls,
  .template-item-foot {
    align-items: stretch;
    flex-direction: column;
  }

  .genre-select {
    width: 100%;
  }

  .template-grid {
    grid-template-columns: 1fr;
  }

  .template-empty {
    grid-template-columns: 1fr;
  }
}
</style>
