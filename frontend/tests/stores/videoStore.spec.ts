import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useVideoStore } from '../../src/stores/videoStore'
import axios from 'axios'

describe('Video Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useVideoStore()
    expect(store.videos).toEqual([])
    expect(store.allVideos).toEqual([])
    expect(store.visibleVideos).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.loadingMore).toBe(false)
    expect(store.error).toBeNull()
    expect(store.currentSearch).toBe('')
    expect(store.currentGame).toBe('')
    expect(store.page).toBe(1)
    expect(store.hasMore).toBe(true)
    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
    expect(store.sortBy).toBe('date')
  })

  it('updates filters', () => {
    const store = useVideoStore()
    store.updateFilters({ date: 'this_week' })
    expect(store.filters.date).toBe('this_week')
  })

  it('updates sorting', () => {
    const store = useVideoStore()
    store.updateSort('views')
    expect(store.sortBy).toBe('views')
  })

  it('resets the store', () => {
    const store = useVideoStore()
    store.videos = [{ id: '1', title: 'Test' }] as any
    store.filters.date = 'this_week'
    store.sortBy = 'views'
    store.currentSearch = 'test'
    store.currentGame = 'test'
    store.page = 2
    store.hasMore = false
    
    store.reset()
    
    expect(store.videos).toEqual([])
    expect(store.allVideos).toEqual([])
    expect(store.visibleVideos).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.loadingMore).toBe(false)
    expect(store.error).toBeNull()
    expect(store.currentSearch).toBe('')
    expect(store.currentGame).toBe('')
    expect(store.page).toBe(1)
    expect(store.hasMore).toBe(true)
    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
    expect(store.sortBy).toBe('date')
  })

  describe('filteredVideos', () => {
    let store: ReturnType<typeof useVideoStore>
    const today = new Date()
    const lastWeek = new Date(today)
    lastWeek.setDate(today.getDate() - 7)
    const lastMonth = new Date(today)
    lastMonth.setMonth(today.getMonth() - 1)

    const mockVideos = [
      {
        id: '1',
        title: 'Video 1',
        url: 'http://test.com/1',
        user_name: 'User 1',
        created_at: today.toISOString(),
        duration: '10m',
        view_count: 500,
        language: 'fr'
      },
      {
        id: '2', 
        title: 'Video 2',
        url: 'http://test.com/2',
        user_name: 'User 2',
        created_at: lastWeek.toISOString(),
        duration: '2h',
        view_count: 2000,
        language: 'en'
      },
      {
        id: '3',
        title: 'Video 3',
        url: 'http://test.com/3',
        user_name: 'User 3',
        created_at: lastMonth.toISOString(),
        duration: '45m',
        view_count: 50,
        language: 'fr'
      }
    ]

    beforeEach(() => {
      store = useVideoStore()
      store.videos = mockVideos
    })

    // it('filters by date', () => {
    //   store.updateFilters({ date: 'today' })
    //   expect(store.filteredVideos.length).toBe(1)
    //   expect(store.filteredVideos[0].id).toBe('1')

    //   store.updateFilters({ date: 'this_week' })
    //   expect(store.filteredVideos.length).toBe(2)
    //   expect(store.filteredVideos.map(v => v.id)).toContain('1')
    //   expect(store.filteredVideos.map(v => v.id)).toContain('2')

    //   store.updateFilters({ date: 'this_month' })
    //   expect(store.filteredVideos.length).toBe(3)
    // })

    it('filters by duration', () => {
      store.updateFilters({ duration: 'short' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('1')

      store.updateFilters({ duration: 'medium' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('3')

      store.updateFilters({ duration: 'long' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('2')
    })

    it('filters by views', () => {
      store.updateFilters({ views: 'less_100' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('3')

      store.updateFilters({ views: '100_1000' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('1')

      store.updateFilters({ views: 'more_1000' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('2')
    })

    it('filters by language', () => {
      store.updateFilters({ language: 'fr' })
      expect(store.filteredVideos.length).toBe(2)
      expect(store.filteredVideos.map(v => v.id)).toContain('1')
      expect(store.filteredVideos.map(v => v.id)).toContain('3')

      store.updateFilters({ language: 'en' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('2')
    })

    it('sorts by date', () => {
      store.updateSort('date')
      expect(store.filteredVideos[0].id).toBe('1')
      expect(store.filteredVideos[1].id).toBe('2')
      expect(store.filteredVideos[2].id).toBe('3')
    })

    it('sorts by views', () => {
      store.updateSort('views')
      expect(store.filteredVideos[0].id).toBe('2')
      expect(store.filteredVideos[1].id).toBe('1')
      expect(store.filteredVideos[2].id).toBe('3')
    })
  })

  describe('searchVideosByGame', () => {
    it('searches videos by game', async () => {
      const store = useVideoStore()
      const mockResponse = {
        data: {
          videos: [
            {
              id: '1',
              title: 'Test Video',
              url: 'http://test.com/1',
              user_name: 'User 1',
              created_at: '2024-03-20T10:00:00Z',
              duration: '10m',
              view_count: 500,
              language: 'fr'
            }
          ]
        }
      }

      vi.spyOn(axios, 'get').mockResolvedValue(mockResponse)

      await store.searchVideosByGame('Minecraft')

      expect(store.videos.length).toBe(1)
      expect(store.videos[0].id).toBe('1')
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })
}) 