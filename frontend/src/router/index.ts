import { createRouter, createWebHistory } from 'vue-router'

const AppLayout = () => import('../layouts/AppLayout.vue')
const BookLayout = () => import('../layouts/BookLayout.vue')

const Dashboard = () => import('../views/Dashboard.vue')
const Home = () => import('../views/Home.vue')
const Workbench = () => import('../views/Workbench.vue')
const Chapter = () => import('../views/Chapter.vue')
const Cast = () => import('../views/Cast.vue')
const CharacterGraph = () => import('../views/CharacterGraph.vue')
const LocationGraph = () => import('../views/LocationGraph.vue')

const Market = () => import('../views/Market.vue')
const TrendsDashboard = () => import('../views/TrendsDashboard.vue')
const NovelResearch = () => import('../views/NovelResearch.vue')
const Deconstruction = () => import('../views/Deconstruction.vue')
const DeconstructionDetail = () => import('../views/DeconstructionDetail.vue')
const PipelineMonitor = () => import('../views/PipelineMonitor.vue')
const Library = () => import('../views/Library.vue')
const Studio = () => import('../views/Studio.vue')

const BookOverview = () => import('../views/book/BookOverview.vue')
const PagePlaceholder = () => import('../components/common/PagePlaceholder.vue')

const CharacterSchedulerSimulator = () =>
  import('../components/debug/CharacterSchedulerSimulator.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard,
          meta: { title: '驾驶舱' },
        },
        {
          path: 'market',
          name: 'Market',
          component: Market,
          meta: { title: '市场洞察 · 爆款发现' },
        },
        {
          path: 'market/trends',
          name: 'MarketTrends',
          component: TrendsDashboard,
          meta: { title: '市场洞察 · 趋势大盘' },
        },
        {
          path: 'market/research',
          name: 'NovelResearch',
          component: NovelResearch,
          meta: { title: '市场洞察 · 题材研究' },
        },
        {
          path: 'market/deconstruction',
          name: 'Deconstruction',
          component: Deconstruction,
          meta: { title: '市场洞察 · 爆款拆书' },
        },
        {
          path: 'market/deconstruction/:id',
          name: 'DeconstructionDetail',
          component: DeconstructionDetail,
          meta: { title: '市场洞察 · 拆书详情' },
        },
        {
          path: 'pipeline',
          name: 'Pipeline',
          component: PipelineMonitor,
          meta: { title: '多 Agent 流水线' },
        },
        {
          path: 'studio',
          name: 'Studio',
          component: Studio,
          meta: { title: '创作工坊' },
        },
        {
          path: 'library',
          name: 'Library',
          component: Library,
          meta: { title: '我的书架' },
        },
        {
          path: 'subscription',
          redirect: '/dashboard',
          meta: { hidden: true },
        },
        {
          path: 'book/:novelId',
          component: BookLayout,
          redirect: (to) => `/book/${to.params.novelId}/overview`,
          children: [
            {
              path: 'overview',
              name: 'BookOverview',
              component: BookOverview,
              meta: { title: '作品概览' },
            },
            {
              path: 'workbench',
              name: 'Workbench',
              component: Workbench,
              meta: { title: '工作台' },
            },
            {
              path: 'outline',
              name: 'BookOutline',
              component: PagePlaceholder,
              props: { title: '大纲管理', description: '可视化故事线、剧情分支与汇合点管理功能即将上线...' },
              meta: { title: '大纲' },
            },
            {
              path: 'characters',
              name: 'BookCharacters',
              component: Cast,
              meta: { title: '人物' },
            },
            {
              path: 'character-graph',
              name: 'BookCharacterGraph',
              component: CharacterGraph,
              meta: { title: '人物图谱' },
            },
            {
              path: 'world',
              name: 'BookWorld',
              component: PagePlaceholder,
              props: { title: '世界观', description: '世界设定、地点图谱、势力格局等世界观管理功能即将上线...' },
              meta: { title: '世界观' },
            },
            {
              path: 'location-graph',
              name: 'BookLocationGraph',
              component: LocationGraph,
              meta: { title: '地点图谱' },
            },
            {
              path: 'timeline',
              name: 'BookTimeline',
              component: PagePlaceholder,
              props: { title: '时间线', description: '故事时间轴、事件序列、因果链追溯功能即将上线...' },
              meta: { title: '时间线' },
            },
            {
              path: 'analytics',
              name: 'BookAnalytics',
              component: PagePlaceholder,
              props: { title: '数据分析', description: '张力曲线、文风分析、人物活跃度、节奏统计等数据分析功能即将上线...' },
              meta: { title: '数据分析' },
            },
            {
              path: 'settings',
              name: 'BookSettings',
              component: PagePlaceholder,
              props: { title: '作品设置', description: '小说基础信息、生成配置、高级设置等功能即将上线...' },
              meta: { title: '作品设置' },
            },
            {
              path: 'chapter/:id',
              name: 'Chapter',
              component: Chapter,
              meta: { title: '章节详情' },
            },
          ],
        },
      ],
    },
    {
      path: '/home',
      name: 'Home',
      component: Home,
    },
    {
      path: '/debug/scheduler',
      name: 'CharacterSchedulerSimulator',
      component: CharacterSchedulerSimulator,
    },
  ],
})

export default router
