<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NEmpty } from 'naive-ui'
import { HammerOutline, ConstructOutline } from '@vicons/ionicons5'

const props = defineProps<{
  title: string
  description?: string
}>()

const desc = computed(() => props.description || '该功能正在开发中，敬请期待...')
</script>

<template>
  <div class="placeholder-page">
    <n-card class="placeholder-card">
      <div class="placeholder-content">
        <div class="placeholder-icon">
          <HammerOutline />
        </div>
        <h2 class="placeholder-title">{{ title }}</h2>
        <p class="placeholder-desc">{{ desc }}</p>
      </div>
    </n-card>
  </div>
</template>

<style scoped>
.placeholder-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.placeholder-card {
  border-radius: var(--app-radius-lg);
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: var(--color-brand-light);
  color: var(--color-brand);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-bottom: 20px;
}

.placeholder-icon svg {
  width: 32px;
  height: 32px;
}

.placeholder-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin: 0 0 8px 0;
}

.placeholder-desc {
  font-size: 14px;
  color: var(--app-text-muted);
  margin: 0;
  max-width: 400px;
}
</style>
