import type { VideoFilters, SortOption, FilterChangeEvent } from './filters'

export interface Game {
  id: string
  name: string
  box_art_url: string | null
}

export interface Video {
  id: string
  user_name: string
  title: string
  url: string
  view_count: number
  duration: string
  created_at: string
  language: string
  thumbnail_url?: string | null
  description?: string | null
  streamer_name?: string | null
  game_id?: string | null
  game_name?: string | null
}

export interface SearchResponse {
  game_name: string
  game: Game | null
  videos: Video[]
  total_count: number
  last_updated: string
  pagination: {
    cursor: string | null
  }
}

export interface VideoState {
  videos: Video[]
  allVideos: Video[]  // Pour stocker tous les vidéos non filtrées
  visibleVideos: Video[]  // Pour stocker les vidéos filtrées
  loading: boolean
  loadingMore: boolean
  error: string | null
  currentSearch: string
  currentGame: string
  currentPage: number
  hasMore: boolean
  filters: VideoFilters
  sortBy: SortOption
  retryCount: number
  lastError: Error | null
  currentStrategy: number
}

export interface SearchParams {
  game_name: string
  limit?: number
  cursor?: string | null
  reset?: boolean
}

export interface VideoStoreActions {
  searchVideosByGame(game_name: string): Promise<void>
  searchVideos(params: SearchParams): Promise<void>
  loadMore(): Promise<void>
  resetState(): void
  updateFilters(event: FilterChangeEvent): void
  updateSort(sortBy: SortOption): void
  updateVisibleVideos(): void
  tryNextStrategy(originalGame: string): Promise<boolean>
  handleNoVideosFound(game_name: string, reset: boolean, toast: any): void
  handleSearchError(error: unknown, game_name: string, toast: any): void
}

export interface VideoStoreGetters {
  [key: string]: any
  filteredVideos: (state: VideoState) => Video[]
} 