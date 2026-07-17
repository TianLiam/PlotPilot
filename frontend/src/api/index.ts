// New RESTful API exports (v1)
export * from './config'
export * from './llmControl'
export * from './novel'
export { chapterApi } from './chapter'
export type {
  UpdateChapterRequest,
  ChapterReviewDTO,
  ChapterStructureDTO,
  ChapterReviewAiResponse,
} from './chapter'
export * from './bible'
export * from './workflow'
export * from './chronicles'
export * from './narrativeEngine'

export * from './stats'
export { marketApi } from './market'
export type { Template, GenreRecommendation, MarketAnalysis } from './market'
