export interface VideoFilters {
  date: 'all' | 'today' | 'this_week' | 'this_month'
  duration: 'all' | 'short' | 'medium' | 'long'
  views: 'all' | 'less_100' | '100_1000' | 'more_1000'
  language: 'all' | 'fr' | 'en' | 'es' | 'de' | 'it' | 'pt' | 'ru' | 'ja' | 'ko' | 'zh'
}

export type SortOption = 'date' | 'views' | 'duration'

export interface FilterChangeEvent {
  type: keyof VideoFilters
  value: string
}

export const DEFAULT_FILTERS: VideoFilters = {
  date: 'all',
  duration: 'all',
  views: 'all',
  language: 'all'
}

export const DEFAULT_SORT: SortOption = 'date' 