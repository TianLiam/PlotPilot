<template>
  <div class="character-graph-page">
    <div class="graph-toolbar">
      <n-space>
        <n-button @click="handleRefresh" :loading="loading">
          <template #icon>
            <n-icon><RefreshOutline /></n-icon>
          </template>
          刷新
        </n-button>
      </n-space>
    </div>

    <div class="graph-container">
      <CharacterRelationGraph
        v-if="novelId"
        :slug="novelId"
        @loading="loading = $event"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NSpace, NIcon } from 'naive-ui'
import { RefreshOutline } from '@vicons/ionicons5'
import CharacterRelationGraph from '../components/graphs/CharacterRelationGraph.vue'

const route = useRoute()
const loading = ref(false)

const novelId = computed(() => route.params.novelId as string)

const handleRefresh = () => {
  window.location.reload()
}
</script>

<style scoped>
.character-graph-page {
  height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
  background: var(--app-page-bg);
}

.graph-toolbar {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px 0;
}

.graph-container {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}
</style>
