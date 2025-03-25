import { defineStore } from 'pinia'
import axios from 'axios'

export const useVideoStore = defineStore('video', {
  state: () => ({
    videos: [],
    loading: false,
    error: null,
    currentSearch: '',
    page: 1,
    hasMore: true
  }),

  actions: {
    async searchVideos(query, reset = true) {
      if (reset) {
        this.videos = []
        this.page = 1
        this.hasMore = true
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/api/twitch/search`, {
          params: {
            game_name: query,
            limit: 10,
            page: this.page
          }
        })
        
        const newVideos = response.data.videos || []
        this.videos = reset ? newVideos : [...this.videos, ...newVideos]
        this.hasMore = newVideos.length === 10
        this.currentSearch = query
        
      } catch (error) {
        this.error = error.response?.data?.detail || 'Une erreur est survenue'
      } finally {
        this.loading = false
      }
    },

    async loadMore() {
      if (!this.loading && this.hasMore) {
        this.page++
        await this.searchVideos(this.currentSearch, false)
      }
    },

    resetSearch() {
      this.videos = []
      this.page = 1
      this.hasMore = true
      this.currentSearch = ''
      this.error = null
    }
  }
}) 