import { defineStore } from 'pinia'
import { searchVideosByGame as searchApi } from '@/api/video'
import type { Video, VideoState, VideoStoreActions, VideoStoreGetters, SearchParams } from '@/types/video'
import type { SortOption, FilterChangeEvent } from '@/types/filters'
import { DEFAULT_FILTERS, DEFAULT_SORT } from '@/types/filters'
import { parseDuration } from '@/utils/duration'
import { retry } from '@/utils/retry'

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
    page: 1,
    hasMore: true,
    filters: DEFAULT_FILTERS,
    sortBy: DEFAULT_SORT,
    retryCount: 0
  }),

  getters: {
    filteredVideos(): Video[] {
      console.log('Starting filtering, total videos:', this.allVideos.length)
      let filtered = [...this.allVideos]

      // Language filter
      if (this.filters.language !== 'all') {
        console.log('Filtering by language:', this.filters.language)
        filtered = filtered.filter(video => {
          const matches = video.language === this.filters.language
          console.log(`Video ${video.id || 'unknown'}: language=${video.language}, match=${matches}`)
          return matches
        })
        console.log('Videos after language filter:', filtered.length)
      }

      // Date filter
      if (this.filters.date !== 'all') {
        console.log('Filtering by date:', this.filters.date)
        const now = new Date()
        filtered = filtered.filter(video => {
          const videoDate = new Date(video.created_at)
          let matches = false
          switch (this.filters.date) {
            case 'today':
              matches = videoDate.toDateString() === now.toDateString()
              break
            case 'this_week':
              const weekAgo = new Date(now.getTime())
              weekAgo.setDate(weekAgo.getDate() - 7)
              matches = videoDate >= weekAgo
              break
            case 'this_month':
              const monthAgo = new Date(now.getTime())
              monthAgo.setMonth(monthAgo.getMonth() - 1)
              matches = videoDate >= monthAgo
              break
            default:
              matches = true
          }
          console.log(`Video ${video.id || 'unknown'}: date=${video.created_at}, match=${matches}`)
          return matches
        })
        console.log('Videos after date filter:', filtered.length)
      }

      // Duration filter
      if (this.filters.duration !== 'all') {
        console.log('Filtering by duration:', this.filters.duration)
        filtered = filtered.filter(video => {
          const duration = parseDuration(video.duration)
          let matches = false
          switch (this.filters.duration) {
            case 'short':
              matches = duration <= 900
              break
            case 'medium':
              matches = duration > 900 && duration <= 3600
              break
            case 'long':
              matches = duration > 3600
              break
            default:
              matches = true
          }
          console.log(`Video ${video.id || 'unknown'}: duration=${video.duration}, match=${matches}`)
          return matches
        })
        console.log('Videos after duration filter:', filtered.length)
      }

      // Views filter
      if (this.filters.views !== 'all') {
        console.log('Filtering by views:', this.filters.views)
        filtered = filtered.filter(video => {
          let matches = false
          switch (this.filters.views) {
            case 'less_100':
              matches = video.view_count < 100
              break
            case '100_1000':
              matches = video.view_count >= 100 && video.view_count < 1000
              break
            case 'more_1000':
              matches = video.view_count >= 1000
              break
            default:
              matches = true
          }
          console.log(`Video ${video.id || 'unknown'}: views=${video.view_count}, match=${matches}`)
          return matches
        })
        console.log('Videos after views filter:', filtered.length)
      }

      // Sort
      console.log('Applying sort:', this.sortBy)
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

      console.log('Final filtered videos count:', filtered.length)
      return filtered
    }
  },

  actions: {
    updateFilters(event: FilterChangeEvent): void {
      console.log('updateFilters called with:', event)
      this.filters = {
        ...this.filters,
        [event.type]: event.value
      }
      console.log('New filters:', this.filters)
      this.applyFilters()
    },

    updateSort(sortBy: SortOption): void {
      console.log('updateSort called with:', sortBy)
      this.sortBy = sortBy
      this.applyFilters()
    },

    applyFilters(): void {
      console.log('applyFilters called')
      console.log('Current filters:', this.filters)
      console.log('Videos count before filtering:', this.allVideos.length)
      this.visibleVideos = this.filteredVideos
      console.log('Videos count after filtering:', this.visibleVideos.length)
    },

    async searchVideosByGame(game_name: string): Promise<void> {
      return this.searchVideos({ game_name, reset: true })
    },

    async searchVideos({ game_name, limit = 10, page = 1, reset = false }: SearchParams): Promise<void> {
      if (reset) {
        this.videos = []
        this.allVideos = []
        this.visibleVideos = []
        this.page = 1
        this.hasMore = true
        this.retryCount = 0
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await retry(
          () => searchApi(game_name),
          3, // maxRetries
          1000 // delay en ms
        )
        
        const newVideos = response.data.videos
        if (!newVideos) {
          throw new Error('No videos in response')
        }
        
        this.videos = reset ? newVideos : [...this.videos, ...newVideos]
        this.allVideos = reset ? newVideos : [...this.allVideos, ...newVideos]
        this.currentGame = game_name
        this.currentSearch = game_name
        this.hasMore = newVideos.length === limit
        this.applyFilters()
      } catch (error) {
        console.error('Error during search:', error)
        this.error = 'An error occurred while searching for videos'
        this.allVideos = []
        this.visibleVideos = []
      } finally {
        this.loading = false
      }
    },

    async loadMore(): Promise<void> {
      if (!this.loading && !this.loadingMore && this.hasMore) {
        this.loadingMore = true
        this.page++
        await this.searchVideos({
          game_name: this.currentSearch,
          page: this.page
        })
        this.loadingMore = false
      }
    },

    resetSearch(): void {
      this.videos = []
      this.allVideos = []
      this.visibleVideos = []
      this.page = 1
      this.hasMore = true
      this.currentSearch = ''
      this.currentGame = ''
      this.error = null
      this.filters = DEFAULT_FILTERS
      this.sortBy = DEFAULT_SORT
      this.loading = false
      this.loadingMore = false
    }
  }
}) 