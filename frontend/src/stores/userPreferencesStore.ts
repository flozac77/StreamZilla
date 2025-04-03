import { defineStore } from 'pinia'

interface UserPreferencesState {
  autoRefreshEnabled: boolean
  autoRefreshInterval: number
  infiniteScrollEnabled: boolean
}

export const useUserPreferencesStore = defineStore('userPreferences', {
  state: (): UserPreferencesState => ({
    autoRefreshEnabled: true,
    autoRefreshInterval: 60000, // 1 minute
    infiniteScrollEnabled: true
  }),

  actions: {
    toggleAutoRefresh() {
      this.autoRefreshEnabled = !this.autoRefreshEnabled
    },

    setAutoRefreshInterval(interval: number) {
      this.autoRefreshInterval = interval
    },

    toggleInfiniteScroll() {
      this.infiniteScrollEnabled = !this.infiniteScrollEnabled
    }
  }
}) 