import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useVideoStore } from '@/stores/videoStore'
import { mockAxios } from '../setup'

describe('Video Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockAxios.reset()
  })

  it('initializes with default values', () => {
    const store = useVideoStore()
    expect(store.videos).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
  })

  it('updates filters', () => {
    const store = useVideoStore()
    store.updateFilters({
      type: 'date',
      value: 'today'
    })
    expect(store.filters).toEqual({
      date: 'today',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
  })

  it('updates sort', () => {
    const store = useVideoStore()
    store.updateSort('views')
    expect(store.sortBy).toBe('views')
  })

  it('resets store state', () => {
    const store = useVideoStore()
    store.videos = [{ id: '1', title: 'Test' }]
    store.loading = true
    store.error = 'Error'

    store.resetSearch()

    expect(store.videos).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
  })

  describe('filteredVideos getter', () => {
    const mockVideos = [
      {
        id: '1',
        title: 'Video 1',
        created_at: new Date().toISOString(),
        duration: '1h30m',
        view_count: 1000,
        language: 'fr'
      },
      {
        id: '2',
        title: 'Video 2',
        created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
        duration: '30m',
        view_count: 500,
        language: 'en'
      }
    ]

    beforeEach(() => {
      const store = useVideoStore()
      store.videos = mockVideos
    })

    it('should filter videos by date', () => {
      const store = useVideoStore()
      store.updateFilters({
        type: 'date',
        value: 'today'
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by duration', () => {
      const store = useVideoStore()
      store.updateFilters({
        type: 'duration',
        value: 'long'
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by views', () => {
      const store = useVideoStore()
      store.updateFilters({
        type: 'views',
        value: 'more_1000'
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by language', () => {
      const store = useVideoStore()
      store.updateFilters({
        type: 'language',
        value: 'fr'
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })
  })

  describe('actions', () => {
    const mockVideos = [
      { id: '1', title: 'Video 1' },
      { id: '2', title: 'Video 2' }
    ]

    it('should handle search videos by game', async () => {
      mockAxios.onGet('/api/search').reply(200, { videos: mockVideos })

      const store = useVideoStore()
      await store.searchVideosByGame('Minecraft')

      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.videos.length).toBe(2)
      expect(store.currentGame).toBe('Minecraft')
    })

    it('should handle search error', async () => {
      mockAxios.onGet('/api/search').reply(500)

      const store = useVideoStore()
      await store.searchVideosByGame('Minecraft')

      expect(store.loading).toBe(false)
      expect(store.error).toBe('Erreur lors de la recherche des vidéos')
      expect(store.videos).toEqual([])
    })
  })
}) 