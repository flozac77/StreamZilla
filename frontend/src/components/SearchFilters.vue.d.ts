import { Component } from 'vue'
import { Store } from 'pinia'

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
}

declare const SearchFilters: Component<SearchFiltersProps, SearchFiltersData>
export default SearchFilters 