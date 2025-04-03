export interface VideoFilters {
  date: 'all' | 'today' | 'this_week' | 'this_month'
  duration: 'all' | 'short' | 'medium' | 'long'
  views: 'all' | 'less_100' | '100_1000' | 'more_1000'
  language: 'all' | 'fr' | 'en'
}

export type SortOption = 'date' | 'views' | 'duration'

export type FilterChangeEvent = {
  type: 'date'
  value: VideoFilters['date']
} | {
  type: 'duration'
  value: VideoFilters['duration']
} | {
  type: 'views'
  value: VideoFilters['views']
} | {
  type: 'language'
  value: VideoFilters['language']
}

export const DEFAULT_FILTERS: VideoFilters = {
  date: 'all',
  duration: 'all',
  views: 'all',
  language: 'all'
}

export const DEFAULT_SORT: SortOption = 'date' 