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
}