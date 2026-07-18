export const BRAND = {
  productName: 'Narra',
  chineseName: '叙界',
  displayName: 'Narra · 叙界',
  tagline: '让每一个故事，都拥有自己的世界。',
  descriptor: 'AI 小说创作平台',
  team: 'Narra（叙界）团队',
  credit: '由 Narra（叙界）团队倾力开发',
} as const

export const BRAND_COPY = {
  short: BRAND.displayName,
  compact: `${BRAND.chineseName} · ${BRAND.tagline}`,
  full: `${BRAND.displayName}｜${BRAND.credit}`,
} as const
