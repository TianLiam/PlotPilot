import { createRouter, createWebHistory } from 'vue-router'

const AppLayout = () => import('../layouts/AppLayout.vue')

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
      ],
    },
    {
      path: '/home',
      name: 'Home',
      component: Home,
    },
    { path: '/book/:slug/workbench', name: 'Workbench', component: Workbench },
    { path: '/book/:slug/cast', name: 'Cast', component: Cast },
    { path: '/book/:slug/chapter/:id', name: 'Chapter', component: Chapter },
    { path: '/book/:slug/characters', name: 'CharacterGraph', component: CharacterGraph },
    { path: '/book/:slug/location-graph', name: 'LocationGraph', component: LocationGraph },
    {
      path: '/debug/scheduler',
      name: 'CharacterSchedulerSimulator',
      component: CharacterSchedulerSimulator,
    },
  ],
})

export default router
