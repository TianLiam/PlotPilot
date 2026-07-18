import { apiClient } from './config'

export interface Template {
  id: string
  name: string
  type: string
  genre: string
  description: string
  popularity: number
  usage_count: number
  content?: string
  source?: 'built_in' | 'crawler'
  confidence_score?: number
  occurrence_count?: number
  trend?: string
  tags?: string[]
  source_novels?: Array<{
    platform: string
    novel_name: string
    rank: number
  }>
}

export interface DiscoveredTemplate {
  id: string
  name: string
  description: string
  pattern_type: string
  genre: string
  content: string
  occurrence_count: number
  avg_rank: number
  trend: string
  trend_value: number
  confidence_score: number
  tags: string[]
  source_novels: Array<{
    platform: string
    novel_name: string
    rank: number
  }>
  status: string
  usage_count: number
  created_at: string
  updated_at: string
}

export interface GenreRecommendation {
  genre: string
  score: number
  trend: 'up' | 'down' | 'stable'
  hot_topics: string[]
  recommended_templates: Template[]
}

export interface MarketAnalysis {
  id: string
  platform: string
  category: string
  total_rankings: number
  avg_popularity: number
  avg_score: number
  trending_tags: string[]
  analysis_date: string
}

export interface TrendHistoryPoint {
  date: string
  score: number
  top_rank?: number
  novel_count: number
}

export interface TrendDashboardRow {
  genre: string
  platform: string
  current_score: number
  current_top_rank: number
  change_value: number
  history_points: number
  history: TrendHistoryPoint[]
}

export interface TrendDashboard {
  days: number
  data_state: 'empty' | 'single_snapshot' | 'historical'
  snapshot_count: number
  series_count: number
  rising: TrendDashboardRow[]
  declining: TrendDashboardRow[]
  hot: TrendDashboardRow[]
  line_series: Array<{
    platform: string
    genre: string
    data_points: TrendHistoryPoint[]
  }>
  heatmap: Array<{ platform: string; genre: string; score: number }>
  hot_tags: Array<{ name: string; value: number }>
}

export const marketApi = {
  getGoldenFingers(genre?: string, limit?: number) {
    const params: Record<string, string | number> = {}
    if (genre) params.genre = genre
    if (limit) params.limit = limit
    return apiClient.get<Template[]>('/market/templates/golden-fingers', { params })
  },

  getCharacters(genre?: string, limit?: number) {
    const params: Record<string, string | number> = {}
    if (genre) params.genre = genre
    if (limit) params.limit = limit
    return apiClient.get<Template[]>('/market/templates/characters', { params })
  },

  getWorldviews(genre?: string, limit?: number) {
    const params: Record<string, string | number> = {}
    if (genre) params.genre = genre
    if (limit) params.limit = limit
    return apiClient.get<Template[]>('/market/templates/worldviews', { params })
  },

  getCoolPoints(genre?: string, limit?: number) {
    const params: Record<string, string | number> = {}
    if (genre) params.genre = genre
    if (limit) params.limit = limit
    return apiClient.get<Template[]>('/market/templates/cool-points', { params })
  },

  getTemplateDetail(id: string) {
    return apiClient.get<Template>(`/market/templates/${id}`)
  },

  searchTemplates(keyword: string) {
    return apiClient.get<Template[]>('/market/templates/search', { params: { keyword } })
  },

  useTemplate(id: string) {
    return apiClient.post(`/market/templates/${id}/use`)
  },

  getGenreRecommendations(limit?: number) {
    const params: Record<string, number> = {}
    if (limit) params.limit = limit
    return apiClient.get<GenreRecommendation[]>('/market/recommender/genres', { params })
  },

  getGenreRecommendation(genre: string) {
    return apiClient.get<GenreRecommendation>(`/market/recommender/genres/${genre}`)
  },

  getMarketAnalysis() {
    return apiClient.get<MarketAnalysis[]>('/market/analyzer/trend-analysis')
  },

  getTrendDashboard(days = 30) {
    return apiClient.get<TrendDashboard>('/market/trend/dashboard', { params: { days } })
  },

  crawlRankings(platform?: string) {
    const params: Record<string, string> = {}
    if (platform) params.platform = platform
    return apiClient.post('/market/crawler/rankings/all', {}, { params })
  },

  crawlHotTopics(source?: string) {
    const params: Record<string, string> = {}
    if (source) params.source = source
    return apiClient.post('/market/crawler/hot-topics/all', {}, { params })
  },

  generateAnalysis(days?: number) {
    const params: Record<string, number> = {}
    if (days) params.days = days
    return apiClient.post('/market/analyzer/full-analysis', {}, { params })
  },

  getDiscoveredTemplates(patternType?: string, genre?: string, limit = 50) {
    const params: Record<string, string | number> = { limit }
    if (patternType) params.pattern_type = patternType
    if (genre) params.genre = genre
    return apiClient.get<DiscoveredTemplate[]>('/market/discovery/templates', { params })
  },

  runTemplateDiscovery(data: {
    platform?: string
    category?: string
    top_n?: number
    max_chapters?: number
  }) {
    return apiClient.post<{ message: string }>('/market/discovery/run', data)
  },

  runDailyTemplateDiscovery(data: {
    platforms: string[]
    categories: string[]
    top_n?: number
  }) {
    return apiClient.post<{ message: string }>('/market/discovery/daily', data)
  },

  markDiscoveredTemplateUsed(id: string) {
    return apiClient.post(`/market/discovery/templates/${id}/use`)
  },

  // ── 创作前研究 ──

  conductResearch(data: ResearchRequest) {
    return apiClient.post<NovelResearch>('/market/research/conduct', data)
  },

  quickCheck(data: ResearchRequest) {
    return apiClient.post<QuickCheckResult>('/market/research/quick-check', data)
  },

  analyzeGenres(genres: string[]) {
    return apiClient.post<GenreAnalysisResult>('/market/research/analyze-genres', { genres })
  },

  getOpeningPatterns(genre: string, topN = 5) {
    return apiClient.get<OpeningPatternsResult>('/market/research/opening-patterns', {
      params: { genre, top_n: topN },
    })
  },

  checkGoldenFingerConflicts(golden_fingers: string[], platform?: string) {
    return apiClient.post<ConflictCheckResult>(
      '/market/research/check-conflicts',
      golden_fingers,
      { params: platform ? { platform } : {} },
    )
  },

  getGenreOptions() {
    return apiClient.get<{ genres: GenreOption[] }>('/market/research/options/genres')
  },

  getGoldenFingerOptions() {
    return apiClient.get<{ golden_fingers: GoldenFingerOption[] }>(
      '/market/research/options/golden-fingers',
    )
  },

  deconstructNovel(data: { platform: string; book_id: string; max_chapters?: number }) {
    return apiClient.post<any>('/market/deconstruction/run', data)
  },

  getDeconstruction(id: string) {
    return apiClient.get<any>(`/market/deconstruction/${id}`)
  },

  listDeconstructions(platform?: string, category?: string, limit = 20) {
    return apiClient.get<any[]>('/market/deconstruction', {
      params: { platform, category, limit },
    })
  },

  getDNALibrary(limit = 50) {
    return apiClient.get<any[]>('/market/deconstruction/dna/library', {
      params: { limit },
    })
  },

  getSingleDNA(deconstructionId: string) {
    return apiClient.get<any>(`/market/deconstruction/dna/${deconstructionId}`)
  },
}

// ── 类型定义 ──

export interface ResearchRequest {
  genres: string[]
  golden_fingers: string[]
  keywords: string[]
  target_word_count: number
  target_chapter_count: number
  additional_notes: string
  platform?: string | null
}

export interface NovelResearch {
  research_id: string
  status: string
  sample_count: number
  overall_score: number
  risk_level: string
  risk_factors: string[]
  timing_score: number
  timing_advice: string
  ai_summary: string
  ai_suggestions: string
  ai_warnings: string
  genre_stats: GenreStat[]
  opening_patterns: OpeningPattern[]
  recommendations: Recommendation[]
}

export interface GenreStat {
  genre: string
  total_novels: number
  successful_novels: number
  success_rate: number
  avg_word_count: number
  median_word_count: number
  avg_chapter_count: number
  avg_chapter_words: number
  optimal_chapter_words: number
  avg_peak_rank: number
  avg_popularity: number
  trend: string
  trend_change: number
}

export interface OpeningPattern {
  name: string
  description: string
  success_count: number
  total_count: number
  success_rate: number
  avg_popularity: number
  sample_novels: string[]
  chapter_range: string
  key_points: string[]
}

export interface Recommendation {
  type: string
  title: string
  description: string
  confidence: number
  reason: string
  references?: string[]
}

export interface QuickCheckResult {
  user_request: ResearchRequest
  genre_stats: GenreStat[]
  conflict_check: {
    conflicts: any[]
    recommendations: any[]
  }
  saturation: {
    level: string
    score: number
    message: string
  }
}

export interface GenreAnalysisResult {
  genres: string[]
  stats: GenreStat[]
}

export interface OpeningPatternsResult {
  genre: string
  patterns: OpeningPattern[]
}

export interface ConflictCheckResult {
  user_golden_fingers: string[]
  current_hot_golden_fingers: string[]
  conflicts: any[]
  saturation: any
  recommendations: any[]
}

export interface GenreOption {
  value: string
  label: string
  description: string
}

export interface GoldenFingerOption {
  value: string
  label: string
  category: string
}
