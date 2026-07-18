<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NSpin } from 'naive-ui'
import BookSubNav from '../components/book/BookSubNav.vue'
import { novelApi, type NovelDTO } from '../api/novel'

const route = useRoute()
const novel = ref<NovelDTO | null>(null)
const loading = ref(true)

const novelId = computed(() => {
  return route.params.novelId as string
})

async function loadNovel() {
  if (!novelId.value) return
  loading.value = true
  try {
    const data = await novelApi.getNovel(novelId.value)
    novel.value = data
  } catch (e) {
    console.error('Failed to load novel:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadNovel()
})

watch(() => route.params.novelId, () => {
  loadNovel()
})
</script>

<template>
  <div class="book-layout">
    <BookSubNav
      v-if="novel"
      :novel-id="novelId"
      :novel-title="novel.title"
    >
      <template #right>
        <slot name="nav-right" />
      </template>
    </BookSubNav>

    <div v-if="loading" class="book-loading">
      <n-spin size="large" />
    </div>

    <main v-else class="book-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.book-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--app-page-bg);
}

.book-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 400px;
}

.book-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
