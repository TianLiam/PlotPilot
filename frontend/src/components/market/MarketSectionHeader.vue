<template>
  <header class="market-section-header">
    <div class="market-section-shell">
      <button class="market-back" type="button" @click="router.push(backTo)">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M19 12H5m6-6-6 6 6 6" />
        </svg>
        <span>{{ backLabel }}</span>
      </button>

      <div class="market-heading-row">
        <div class="market-heading-copy">
          <span class="market-eyebrow">{{ eyebrow }}</span>
          <h1>{{ title }}</h1>
          <p>{{ subtitle }}</p>
        </div>
        <div v-if="$slots.actions" class="market-heading-actions">
          <slot name="actions" />
        </div>
      </div>

      <nav class="market-section-nav" aria-label="市场洞察子功能">
        <router-link
          v-for="(item, index) in navItems"
          :key="item.path"
          :to="item.path"
          class="market-section-link"
          :class="{ 'is-active': isCurrent(item) }"
        >
          <span class="market-section-index">0{{ index + 1 }}</span>
          <span>{{ item.label }}</span>
          <span v-if="item.hint" class="market-section-hint">{{ item.hint }}</span>
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

type SectionItem = {
  path: string
  label: string
  hint?: string
}

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

const route = useRoute()
const router = useRouter()

const navItems: SectionItem[] = [
  { path: '/market/trends', label: '趋势大盘' },
  { path: '/market', label: '题材发现', hint: 'HOT' },
  { path: '/market/research', label: '题材研究' },
  { path: '/market/deconstruction', label: '作品拆解' },
]

function isCurrent(item: SectionItem): boolean {
  if (item.path === '/market') return route.path === '/market'
  return route.path === item.path || route.path.startsWith(`${item.path}/`)
}
</script>

<style scoped>
.market-section-header {
  border-bottom: 1px solid var(--app-border);
  background:
    radial-gradient(circle at 78% -40%, rgba(79, 70, 229, 0.12), transparent 35%),
    var(--app-surface);
}

.market-section-shell {
  width: min(1240px, calc(100% - 48px));
  margin: 0 auto;
  padding-top: 18px;
}

.market-back {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--app-text-muted);
  font: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: color 160ms ease;
}

.market-back:hover {
  color: #4f46e5;
}

.market-back svg {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.market-heading-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  padding: 22px 0 24px;
}

.market-heading-copy {
  min-width: 0;
}

.market-eyebrow {
  display: block;
  margin-bottom: 8px;
  color: #4f46e5;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.market-heading-copy h1 {
  margin: 0;
  color: var(--app-text-primary);
  font-family: "Noto Serif SC", "Source Han Serif SC", Georgia, serif;
  font-size: clamp(28px, 3vw, 40px);
  font-weight: 800;
  letter-spacing: -0.045em;
  line-height: 1.12;
}

.market-heading-copy p {
  max-width: 680px;
  margin: 10px 0 0;
  color: var(--app-text-muted);
  font-size: 14px;
  line-height: 1.7;
}

.market-heading-actions {
  flex: 0 0 auto;
}

.market-section-nav {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  padding-bottom: 14px;
}

.market-section-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 42px;
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: 11px;
  color: var(--app-text-secondary);
  font-size: 13px;
  font-weight: 650;
  text-decoration: none;
  transition: border-color 160ms ease, background 160ms ease, color 160ms ease;
}

.market-section-link:hover {
  border-color: var(--app-border);
  background: rgba(255, 255, 255, 0.7);
  color: var(--app-text-primary);
}

.market-section-link.is-active {
  border-color: rgba(79, 70, 229, 0.18);
  background: rgba(79, 70, 229, 0.08);
  color: #4338ca;
}

.market-section-index {
  color: var(--app-text-muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.is-active .market-section-index {
  color: #6366f1;
}

.market-section-hint {
  margin-left: auto;
  padding: 2px 6px;
  border-radius: 99px;
  background: #f97316;
  color: #fff;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

@media (max-width: 760px) {
  .market-section-shell {
    width: min(100% - 28px, 1240px);
    padding-top: 14px;
  }

  .market-heading-row {
    align-items: flex-start;
    flex-direction: column;
    gap: 16px;
    padding: 18px 0 20px;
  }

  .market-heading-actions {
    width: 100%;
  }

  .market-section-nav {
    display: flex;
    margin: 0 -2px;
    padding-bottom: 12px;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .market-section-nav::-webkit-scrollbar {
    display: none;
  }

  .market-section-link {
    flex: 0 0 auto;
    min-height: 38px;
  }
}
</style>
