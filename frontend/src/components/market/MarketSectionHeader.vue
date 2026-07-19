<template>
  <header class="market-section-header">
    <div class="market-section-shell">
      <button class="market-back" type="button" @click="router.push(backTo)">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M19 12H5m6-6-6 6 6 6" />
        </svg>
        <span>{{ backLabel }}</span>
      </button>

      <div class="page-header">
        <div class="page-heading">
          <span class="page-eyebrow">{{ eyebrow }}</span>
          <h1 class="page-title">{{ title }}</h1>
          <p class="page-subtitle">{{ subtitle }}</p>
        </div>
        <div v-if="$slots.actions" class="market-heading-actions">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

withDefaults(defineProps<{
  eyebrow?: string
  title: string
  subtitle: string
  backTo?: string
  backLabel?: string
}>(), {
  eyebrow: 'Market intelligence',
  backTo: '/market',
  backLabel: '返回市场洞察',
})

const router = useRouter()
</script>

<style scoped>
.market-section-header {
  border-bottom: 1px solid var(--app-border);
  background:
    radial-gradient(circle at 8% 0%, var(--color-brand-light), transparent 28%),
    var(--app-page-bg);
}

.market-section-shell {
  width: min(1240px, calc(100% - 48px));
  margin: 0 auto;
  padding-top: 14px;
}

.market-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--app-text-muted);
  font: inherit;
  font-size: 12px;
  cursor: pointer;
  transition: color 160ms ease;
}

.market-back:hover {
  color: var(--color-brand);
}

.market-back svg {
  width: 14px;
  height: 14px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

/* 与 Library / Studio 一致的 page-header 风格 */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 20px;
}

.page-heading {
  max-width: 680px;
  min-width: 0;
}

.page-eyebrow {
  display: block;
  margin-bottom: 7px;
  color: var(--color-brand);
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.page-title {
  margin: 0 0 7px;
  color: var(--app-text-primary);
  font-family: var(--font-serif);
  font-size: clamp(28px, 3vw, 36px);
  font-weight: 680;
  letter-spacing: -0.035em;
  line-height: 1.15;
}

.page-subtitle {
  max-width: 580px;
  margin: 0;
  color: var(--app-text-secondary);
  font-size: 13px;
  line-height: 1.65;
}

.market-heading-actions {
  flex: 0 0 auto;
}

@media (max-width: 760px) {
  .market-section-shell {
    width: min(100% - 28px, 1240px);
    padding-top: 12px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 16px;
  }

  .market-heading-actions {
    width: 100%;
  }
}
</style>
