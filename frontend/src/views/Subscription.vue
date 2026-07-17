<template>
  <div class="subscription-page">
    <div class="subscription-header">
      <div class="header-inner">
        <div class="header-left">
          <h1 class="page-title">会员订阅</h1>
          <p class="page-subtitle">解锁更多 AI 创作能力，成为爆款作家</p>
        </div>
        <div class="header-right">
          <n-button @click="goBack">
            <template #icon><n-icon><IconArrowLeft /></n-icon></template>
            返回
          </n-button>
        </div>
      </div>
    </div>

    <div class="subscription-content">
      <div class="pricing-switch">
        <n-radio-group v-model:value="billingCycle" size="medium">
          <n-radio-button value="monthly">按月付费</n-radio-button>
          <n-radio-button value="yearly">按年付费 <n-tag type="success" size="small">省20%</n-tag></n-radio-button>
        </n-radio-group>
      </div>

      <n-grid :cols="3" :x-gap="20" :y-gap="20" responsive="screen" class="pricing-grid">
        <n-gi>
          <div class="pricing-card" :class="{ 'is-popular': false }">
            <div class="pricing-badge">免费版</div>
            <h3 class="pricing-title">新手作家</h3>
            <div class="pricing-price">
              <span class="price-value">¥0</span>
              <span class="price-period">/永久</span>
            </div>
            <p class="pricing-desc">适合个人创作者，体验 AI 写作基础功能</p>

            <ul class="pricing-features">
              <li v-for="feature in freeFeatures" :key="feature">
                <n-icon :component="IconCheck" :size="14" class="feature-icon" />
                <span>{{ feature }}</span>
              </li>
            </ul>

            <div class="pricing-actions">
              <n-button size="large" @click="selectPlan('free')">
                免费使用
              </n-button>
            </div>
          </div>
        </n-gi>

        <n-gi>
          <div class="pricing-card is-popular">
            <div class="pricing-badge popular-badge">推荐</div>
            <h3 class="pricing-title">专业版</h3>
            <div class="pricing-price">
              <span class="price-value">¥{{ billingCycle === 'monthly' ? '29' : '278' }}</span>
              <span class="price-period">/{{ billingCycle === 'monthly' ? '月' : '年' }}</span>
            </div>
            <p class="pricing-desc">解锁完整 AI 创作能力，快速打造爆款</p>

            <ul class="pricing-features">
              <li v-for="feature in proFeatures" :key="feature">
                <n-icon :component="IconCheck" :size="14" class="feature-icon" />
                <span>{{ feature }}</span>
              </li>
            </ul>

            <div class="pricing-actions">
              <n-button type="primary" size="large" @click="selectPlan('pro')">
                <template #icon><n-icon><IconSparkles /></n-icon></template>
                立即升级
              </n-button>
            </div>
          </div>
        </n-gi>

        <n-gi>
          <div class="pricing-card" :class="{ 'is-popular': false }">
            <div class="pricing-badge">企业版</div>
            <h3 class="pricing-title">团队版</h3>
            <div class="pricing-price">
              <span class="price-value">¥{{ billingCycle === 'monthly' ? '99' : '950' }}</span>
              <span class="price-period">/{{ billingCycle === 'monthly' ? '月' : '年' }}</span>
            </div>
            <p class="pricing-desc">团队协作创作，共享模板库与数据</p>

            <ul class="pricing-features">
              <li v-for="feature in teamFeatures" :key="feature">
                <n-icon :component="IconCheck" :size="14" class="feature-icon" />
                <span>{{ feature }}</span>
              </li>
            </ul>

            <div class="pricing-actions">
              <n-button type="info" size="large" @click="selectPlan('team')">
                <template #icon><n-icon><IconUsers /></n-icon></template>
                联系销售
              </n-button>
            </div>
          </div>
        </n-gi>
      </n-grid>

      <n-card :bordered="false" class="faq-card">
        <template #header>
          <div class="faq-header">
            <span class="faq-title">🤔 常见问题</span>
          </div>
        </template>
        <n-space vertical size="medium">
          <n-collapse default-expanded-names="1">
            <n-collapse-item name="1" title="支付方式有哪些？">
              <p>支持微信支付、支付宝、银行卡等主流支付方式。企业用户可申请对公转账。</p>
            </n-collapse-item>
            <n-collapse-item name="2" title="订阅后可以退款吗？">
              <p>按月订阅支持 7 天无理由退款，按年订阅支持 30 天无理由退款。退款将在 3-5 个工作日内到账。</p>
            </n-collapse-item>
            <n-collapse-item name="3" title="团队版最多支持多少人？">
              <p>团队版默认支持 5 人协作，如需更多席位可联系销售团队定制方案。</p>
            </n-collapse-item>
            <n-collapse-item name="4" title="如何升级或降级订阅？">
              <p>在设置页面的订阅管理中，可随时升级或降级订阅方案。升级立即生效，降级将在下一计费周期生效。</p>
            </n-collapse-item>
            <n-collapse-item name="5" title="API 调用次数是每月重置吗？">
              <p>是的，每月 1 号自动重置 API 调用次数。未使用的次数不累计到下月。</p>
            </n-collapse-item>
          </n-collapse>
        </n-space>
      </n-card>
    </div>

    <n-modal v-model:show="showPaymentModal" preset="card" title="确认支付" :style="{ width: '520px' }">
      <div class="payment-modal">
        <div class="payment-summary">
          <div class="summary-row">
            <span>订阅方案</span>
            <span>{{ selectedPlan?.title }}</span>
          </div>
          <div class="summary-row">
            <span>计费周期</span>
            <span>{{ billingCycle === 'monthly' ? '按月付费' : '按年付费' }}</span>
          </div>
          <div class="summary-row total">
            <span>应付金额</span>
            <span>¥{{ selectedPlan?.price }}</span>
          </div>
        </div>

        <n-space vertical size="medium" style="margin-top: 20px">
          <n-radio-group v-model:value="paymentMethod">
            <n-radio value="wechat">
              <template #default>
                <div class="payment-option">
                  <span class="payment-icon">💳</span>
                  <span>微信支付</span>
                </div>
              </template>
            </n-radio>
            <n-radio value="alipay">
              <template #default>
                <div class="payment-option">
                  <span class="payment-icon">🐴</span>
                  <span>支付宝</span>
                </div>
              </template>
            </n-radio>
            <n-radio value="card">
              <template #default>
                <div class="payment-option">
                  <span class="payment-icon">🏦</span>
                  <span>银行卡</span>
                </div>
              </template>
            </n-radio>
          </n-radio-group>
        </n-space>

        <div class="modal-actions">
          <n-button @click="showPaymentModal = false">取消</n-button>
          <n-button type="primary" @click="confirmPayment">确认支付</n-button>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, h } from 'vue'
import { NIcon, useMessage } from 'naive-ui'

const message = useMessage()

const IconArrowLeft = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z' }))

const IconCheck = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' }))

const IconSparkles = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z' }))

const IconUsers = () =>
  h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', width: '1em', height: '1em' },
    h('path', { fill: 'currentColor', d: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' }))

const billingCycle = ref('monthly')
const paymentMethod = ref('wechat')
const showPaymentModal = ref(false)
const selectedPlan = ref<{ title: string; price: string } | null>(null)

const freeFeatures = [
  '每月 100 次 AI 写作调用',
  '基础小说管理功能',
  '1 个小说项目',
  '基础章节编辑器',
  '社区模板库',
  '邮件技术支持',
]

const proFeatures = [
  '每月 5000 次 AI 写作调用',
  '完整小说管理功能',
  '无限小说项目',
  'AI 智能续写',
  '市场洞察与趋势分析',
  '爆款拆书与模板提取',
  '多 Agent 自动创作流水线',
  'Novel Research 创作前研究',
  '高级质量检测工具',
  '专属模板库',
  '优先技术支持',
]

const teamFeatures = [
  '每月 20000 次 AI 写作调用',
  '所有专业版功能',
  '5 人团队协作',
  '共享模板库与数据',
  '团队权限管理',
  '定制化 API 接入',
  '私有部署支持',
  '专属客户成功经理',
  '7×24 小时技术支持',
  '定制化培训服务',
]

function goBack() {
  window.history.back()
}

function selectPlan(plan: string) {
  if (plan === 'free') {
    message.info('当前已是免费版')
    return
  }

  const planInfo = {
    pro: { title: '专业版', price: billingCycle.value === 'monthly' ? '29' : '278' },
    team: { title: '团队版', price: billingCycle.value === 'monthly' ? '99' : '950' },
  }

  selectedPlan.value = planInfo[plan as keyof typeof planInfo]
  showPaymentModal.value = true
}

function confirmPayment() {
  showPaymentModal.value = false
  message.success('支付成功！会员权益已生效')
}
</script>

<style scoped>
.subscription-page {
  min-height: calc(100vh - 60px);
  background: var(--app-page-bg);
}

.subscription-header {
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  padding: 0 24px;
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0 16px;
}

.page-title {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  color: var(--app-text-primary);
  letter-spacing: -0.02em;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--app-text-muted);
}

.subscription-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.pricing-switch {
  text-align: center;
  margin-bottom: 32px;
}

.pricing-grid {
  margin-bottom: 40px;
}

.pricing-card {
  background: var(--app-surface);
  border-radius: 16px;
  border: 2px solid var(--app-border);
  padding: 32px 24px;
  position: relative;
  transition: all 0.3s ease;
}

.pricing-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--app-shadow-lg);
}

.pricing-card.is-popular {
  border-color: var(--color-brand);
  box-shadow: 0 0 0 4px var(--color-brand-light);
}

.pricing-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  background: var(--app-surface-subtle);
  color: var(--app-text-secondary);
  margin-bottom: 16px;
}

.popular-badge {
  background: linear-gradient(135deg, var(--color-brand), var(--color-brand-hover));
  color: #fff;
}

.pricing-title {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text-primary);
}

.pricing-price {
  margin-bottom: 12px;
}

.price-value {
  font-size: 42px;
  font-weight: 700;
  color: var(--app-text-primary);
  letter-spacing: -0.02em;
}

.price-period {
  font-size: 14px;
  color: var(--app-text-muted);
  margin-left: 4px;
}

.pricing-desc {
  margin: 0 0 24px;
  font-size: 13px;
  color: var(--app-text-muted);
  line-height: 1.5;
}

.pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pricing-features li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: var(--app-text-secondary);
  line-height: 1.5;
}

.feature-icon {
  color: var(--color-success);
  flex-shrink: 0;
  margin-top: 2px;
}

.pricing-actions {
  display: flex;
}

.pricing-actions .n-button {
  width: 100%;
}

.faq-card {
  border-radius: 14px;
  box-shadow: var(--app-shadow-md);
}

.faq-header {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text-primary);
}

.payment-modal {
  padding: 8px 0;
}

.payment-summary {
  background: var(--app-surface-subtle);
  border-radius: 10px;
  padding: 16px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.summary-row.total {
  padding-top: 12px;
  border-top: 1px dashed var(--app-border);
  font-weight: 600;
  color: var(--app-text-primary);
}

.summary-row.total span:last-child {
  font-size: 18px;
  font-weight: 700;
}

.payment-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  transition: background 0.2s ease;
}

.payment-option:hover {
  background: var(--app-surface-subtle);
}

.payment-icon {
  font-size: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--app-border);
}

@media (max-width: 900px) {
  .subscription-content {
    padding: 24px 16px;
  }

  .pricing-grid :deep(.n-grid) {
    grid-template-columns: 1fr;
  }

  .pricing-card {
    padding: 24px 20px;
  }

  .price-value {
    font-size: 36px;
  }
}
</style>
