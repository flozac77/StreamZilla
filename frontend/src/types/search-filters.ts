import type { Store } from 'pinia'

export interface SearchFiltersProps {
  store: Store
}

export interface SearchFiltersData {
  selectedFilters: {
    date: string
    duration: string
    views: string
    language: string
  }
  sortBy: string
  store: Store
} 