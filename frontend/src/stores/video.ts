import { defineStore } from 'pinia'
import { searchVideosByGame as searchApi } from '@/api/video'
import type { Video, VideoState, VideoStoreActions, VideoStoreGetters, SearchParams } from '@/types/video'
import type { SortOption, FilterChangeEvent } from '@/types/filters'
import { DEFAULT_FILTERS, DEFAULT_SORT } from '@/types/filters'
import { parseDuration } from '@/utils/duration'
import { retry } from '@/utils/retry'
import { useToast } from 'vue-toastification'

// Cache constants
const CACHE_TTL_MS = 900000 // 15 minutes
interface CachedVideoSearch {
  data: {
    videos: Video[]
    pagination: { cursor: string | null }
    game?: any // Optional: if you store game details from TwitchSearchResult
  }
  expiry: number
}

// Stratégies de fallback pour la recherche
const FALLBACK_STRATEGIES = [
  (game: string) => game.toLowerCase(),
  (game: string) => game.split(/[\s-]+/)[0], // Premier mot
  (game: string) => game.replace(/[^a-zA-Z0-9]/g, ''), // Alphanumérique uniquement
  (game: string) => game.split(/[\s-]+/).slice(0, 2).join(' '), // Deux premiers mots
]

const VIDEOS_PER_PAGE = 20
const MAX_VIDEOS = 100

export const useVideoStore = defineStore<string, VideoState, VideoStoreGetters, VideoStoreActions>('video', {
  state: () => ({
    videos: [] as Video[],
    allVideos: [] as Video[],
    visibleVideos: [] as Video[],
    loading: false,
    loadingMore: false,
    error: null as string | null,
    currentSearch: '',
    currentGame: '',
    currentPage: 1,
    hasMore: true,
    filters: DEFAULT_FILTERS,
    sortBy: DEFAULT_SORT,
    retryCount: 0,
    lastError: null as Error | null,
    currentStrategy: -1,
    nextCursor: null as string | null
  }),

  getters: {
    filteredVideos(): Video[] {
      let filtered = [...this.allVideos]

      // Appliquer les filtres
      if (this.filters.language !== 'all') {
        filtered = filtered.filter(video => video.language === this.filters.language)
      }

      if (this.filters.date !== 'all') {
        const now = new Date()
        filtered = filtered.filter(video => {
          const videoDate = new Date(video.created_at)
          switch (this.filters.date) {
            case 'today': {
              return videoDate.toDateString() === now.toDateString()
            }
            case 'this_week': {
              const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
              return videoDate >= weekAgo
            }
            case 'this_month': {
              const monthAgo = new Date(now.getTime())
              monthAgo.setMonth(monthAgo.getMonth() - 1)
              return videoDate >= monthAgo
            }
            default:
              return true
          }
        })
      }

      if (this.filters.duration !== 'all') {
        filtered = filtered.filter(video => {
          const duration = parseDuration(video.duration)
          switch (this.filters.duration) {
            case 'short': {
              return duration <= 900
            }
            case 'medium': {
              return duration > 900 && duration <= 3600
            }
            case 'long': {
              return duration > 3600
            }
            default:
              return true
          }
        })
      }

      if (this.filters.views !== 'all') {
        filtered = filtered.filter(video => {
          switch (this.filters.views) {
            case 'less_100': {
              return video.view_count < 100
            }
            case '100_1000': {
              return video.view_count >= 100 && video.view_count < 1000
            }
            case 'more_1000': {
              return video.view_count >= 1000
            }
            default:
              return true
          }
        })
      }

      // Appliquer le tri
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'date':
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          case 'views':
            return b.view_count - a.view_count
          case 'duration':
            return parseDuration(b.duration) - parseDuration(a.duration)
          default:
            return 0
        }
      })

      return filtered
    },

    paginatedVideos(): Video[] {
      const filtered = this.filteredVideos
      const start = 0
      const end = this.currentPage * VIDEOS_PER_PAGE
      return filtered.slice(start, Math.min(end, filtered.length))
    },

    totalFilteredCount(): number {
      return this.filteredVideos.length
    }
  },

  actions: {
    updateFilters(event: FilterChangeEvent): void {
      this.filters = {
        ...this.filters,
        [event.type]: event.value
      }
      this.currentPage = 1
      this.updateVisibleVideos()
    },

    updateSort(sortBy: SortOption): void {
      this.sortBy = sortBy
      this.currentPage = 1
      this.updateVisibleVideos()
    },

    updateVisibleVideos(): void {
      const filtered = this.filteredVideos
      const start = 0
      const end = this.currentPage * VIDEOS_PER_PAGE
      
      // Mettre à jour les vidéos visibles
      this.visibleVideos = filtered.slice(start, end)
      
      console.log({
        totalVideos: this.allVideos.length,
        filteredCount: filtered.length,
        visibleCount: this.visibleVideos.length,
        currentPage: this.currentPage,
        hasMore: this.hasMore,
        nextCursor: this.nextCursor
      })
    },

    async searchVideosByGame(raw_game_name: string): Promise<void> {
      const game_name = raw_game_name.trim()
      if (!game_name) {
        this.resetState()
        // Optionally, show a toast or set an error message if a blank search is attempted
        const toast = useToast()
        toast.info("Search query was empty. Displaying default state.")
        return
      }
      return this.searchVideos({ game_name, reset: true })
    },

    async searchVideos({ game_name, reset = false }: SearchParams): Promise<void> {
      // game_name here is assumed to be already trimmed if called from searchVideosByGame
      // If searchVideos can be called directly from elsewhere with a raw query,
      // trimming might be needed here too, or ensure all call sites trim.
      // For now, assuming searchVideosByGame is the main entry point for new game searches.
      const toast = useToast()
      
      if (reset) {
        // Try to load from cache first when it's a new search
        const cacheKey = `videoSearchCache_${game_name}`
        try {
          const cached = localStorage.getItem(cacheKey)
          if (cached) {
            const parsedCache: CachedVideoSearch = JSON.parse(cached)
            if (Date.now() < parsedCache.expiry) {
              console.log(`Cache hit for ${game_name}. Displaying cached results.`)
              this.allVideos = parsedCache.data.videos
              this.currentGame = game_name 
              this.currentSearch = game_name
              this.nextCursor = parsedCache.data.pagination.cursor
              this.hasMore = !!this.nextCursor
              this.currentPage = 1 // Reset page for cached results display
              this.updateVisibleVideos()
              this.loading = false
              toast.info(`Displaying cached results for "${game_name}".`)
              return
            } else {
              console.log(`Cache expired for ${game_name}. Fetching fresh data.`)
              localStorage.removeItem(cacheKey) // Remove expired cache
            }
          }
        } catch (e) {
          console.error('Error accessing localStorage for cache retrieval:', e)
        }
        // If cache miss or expired, proceed to reset state (without clearing this specific cache again) and fetch
        this.resetState(false) 
      }
      
      this.loading = reset
      this.loadingMore = !reset
      this.error = null
      
      try {
        console.log('Searching videos for game:', game_name, 'with cursor:', this.nextCursor)
        const response = await retry(
          () => searchApi(game_name, { 
            limit: MAX_VIDEOS,
            cursor: reset ? null : this.nextCursor,
            use_cache: reset // This use_cache is for backend API cache, not client-side
          }),
          3,
          1000,
          (error, attempt) => {
            this.retryCount = attempt
            this.lastError = error
            toast.info(`Tentative ${attempt}/3 de récupération des vidéos...`)
          }
        )
        
        const newVideos = response.data.videos
        if (!newVideos || newVideos.length === 0) {
          this.handleNoVideosFound(game_name, reset, toast)
          return
        }
        
        console.log(`Received ${newVideos.length} videos from API`)
        
        // Mettre à jour le curseur pour la pagination
        this.nextCursor = response.data.pagination?.cursor || null
        this.hasMore = !!this.nextCursor
        
        if (reset) {
          this.allVideos = newVideos
        } else {
          // Vérifier les doublons avant d'ajouter
          const existingIds = new Set(this.allVideos.map(v => v.id))
          const uniqueNewVideos = newVideos.filter(v => !existingIds.has(v.id))
          this.allVideos = [...this.allVideos, ...uniqueNewVideos]
        }
        
        this.currentGame = game_name
        this.currentSearch = game_name
        this.updateVisibleVideos()
        
        if (reset) {
          toast.success(`${newVideos.length} vidéos trouvées pour "${game_name}"`)
          // Save to client-side cache if it was a fresh search (reset = true) and videos were found
          if (newVideos.length > 0) {
            const cacheKey = `videoSearchCache_${game_name}`
            const cacheItem: CachedVideoSearch = {
              data: {
                videos: this.allVideos, // allVideos is now newVideos
                pagination: { cursor: this.nextCursor },
                game: response.data.game 
              },
              expiry: Date.now() + CACHE_TTL_MS
            }
            try {
              localStorage.setItem(cacheKey, JSON.stringify(cacheItem))
              console.log(`Saved search results for ${game_name} to client cache.`)
            } catch (e) {
              console.error('Error saving to localStorage:', e)
            }
          }
        } else if (!reset && this.currentGame) { // Update cache on loadMore success
            const cacheKey = `videoSearchCache_${this.currentGame}`
            const cacheItem: CachedVideoSearch = {
              data: {
                videos: this.allVideos, // Updated allVideos
                pagination: { cursor: this.nextCursor },
                // game data might not be available on subsequent loads, or use existing from store if needed
              },
              expiry: Date.now() + CACHE_TTL_MS 
            }
            try {
              localStorage.setItem(cacheKey, JSON.stringify(cacheItem))
              console.log(`Updated client cache for ${this.currentGame} after loadMore.`)
            } catch (e) {
              console.error('Error updating localStorage after loadMore:', e)
            }
        }
      } catch (error) {
        this.handleSearchError(error, game_name, toast)
      } finally {
        this.loading = false
        this.loadingMore = false
      }
    },

    async tryNextStrategy(originalGame: string): Promise<boolean> {
      this.currentStrategy++
      if (this.currentStrategy >= FALLBACK_STRATEGIES.length) {
        return false
      }

      const strategy = FALLBACK_STRATEGIES[this.currentStrategy]
      const modifiedGame = strategy(originalGame)
      
      if (modifiedGame === originalGame) {
        return this.tryNextStrategy(originalGame)
      }

      const toast = useToast()
      toast.info(`Tentative avec une recherche modifiée : "${modifiedGame}"`)
      
      try {
        const response = await retry(
          () => searchApi(modifiedGame, { 
            limit: MAX_VIDEOS,
            use_cache: false 
          }),
          2,
          1000
        )
        
        if (response.data.videos && response.data.videos.length > 0) {
          console.log(`Fallback strategy found ${response.data.videos.length} videos`)
          this.allVideos = response.data.videos
          this.currentGame = modifiedGame
          this.currentSearch = modifiedGame
          this.currentPage = 1
          this.updateVisibleVideos()
          toast.success(`${response.data.videos.length} vidéos trouvées pour "${modifiedGame}"`)
          return true
        }
      } catch (error) {
        console.error('Fallback strategy failed:', error)
      }
      
      return this.tryNextStrategy(originalGame)
    },

    async loadMore(): Promise<void> {
      if (this.loading || this.loadingMore || !this.hasMore) {
        return
      }

      console.log('Loading more videos...')
      await this.searchVideos({
        game_name: this.currentGame,
        reset: false
      })
    },

    resetState(clearAssociatedCache = true): void {
      if (clearAssociatedCache && this.currentGame) {
        const cacheKey = `videoSearchCache_${this.currentGame}`
        try {
          localStorage.removeItem(cacheKey)
          console.log(`Cache cleared for game: ${this.currentGame} due to resetState.`)
        } catch (e) {
          console.error('Error removing item from localStorage during resetState:', e)
        }
      }
      this.videos = []
      this.allVideos = []
      this.visibleVideos = []
      this.currentPage = 1
      this.hasMore = true
      this.currentSearch = ''
      this.currentGame = ''
      this.error = null
      this.filters = DEFAULT_FILTERS
      this.sortBy = DEFAULT_SORT
      this.loading = false
      this.loadingMore = false
      this.retryCount = 0
      this.lastError = null
      this.currentStrategy = -1
      this.nextCursor = null
    },

    handleNoVideosFound(game_name: string, reset: boolean, toast: any): void {
      if (reset) {
        toast.warning(`Aucune vidéo trouvée pour "${game_name}". Tentative avec des termes alternatifs...`)
        this.tryNextStrategy(game_name).then(found => {
          if (!found) {
            toast.error(`Aucune vidéo trouvée pour "${game_name}" même après plusieurs tentatives`)
            this.hasMore = false
            this.nextCursor = null
          }
        })
      } else {
        this.hasMore = false
        this.nextCursor = null
        toast.info('Plus de vidéos disponibles')
      }
    },

    handleSearchError(error: unknown, game_name: string, toast: any): void {
      console.error('Error in searchVideos:', error)
      this.error = error instanceof Error ? error.message : 'Une erreur est survenue'
      this.lastError = error instanceof Error ? error : new Error('Une erreur est survenue')
      this.hasMore = false
      this.nextCursor = null
      
      toast.error(`Erreur lors de la recherche des vidéos${this.retryCount > 0 ? ` (après ${this.retryCount} tentatives)` : ''}: ${this.error}`)
      
      if (this.visibleVideos.length === 0) {
        this.tryNextStrategy(game_name).then(found => {
          if (!found) {
            this.visibleVideos = []
            toast.error('Impossible de charger les vidéos malgré plusieurs tentatives. Veuillez réessayer plus tard.')
          }
        })
      }
    }
  }
}) 