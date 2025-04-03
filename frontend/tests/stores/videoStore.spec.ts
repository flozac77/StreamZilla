import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useVideoStore } from '../../src/stores/videoStore'
import axios from 'axios'

describe('Video Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initialise avec les valeurs par défaut', () => {
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

  it('met à jour les filtres', () => {
    const store = useVideoStore()
    store.updateFilters({ date: 'this_week' })
    expect(store.filters.date).toBe('this_week')
  })

  it('met à jour le tri', () => {
    const store = useVideoStore()
    store.updateSort('views')
    expect(store.sortBy).toBe('views')
  })

  it('réinitialise le store', () => {
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

    it('filtre par date', () => {
      store.updateFilters({ date: 'today' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('1')

      store.updateFilters({ date: 'this_week' })
      expect(store.filteredVideos.length).toBe(2)
      expect(store.filteredVideos.map(v => v.id)).toContain('1')
      expect(store.filteredVideos.map(v => v.id)).toContain('2')

      store.updateFilters({ date: 'this_month' })
      expect(store.filteredVideos.length).toBe(3)
    })

    it('filtre par durée', () => {
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

    it('filtre par vues', () => {
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

    it('filtre par langue', () => {
      store.updateFilters({ language: 'fr' })
      expect(store.filteredVideos.length).toBe(2)
      expect(store.filteredVideos.map(v => v.id)).toContain('1')
      expect(store.filteredVideos.map(v => v.id)).toContain('3')

      store.updateFilters({ language: 'en' })
      expect(store.filteredVideos.length).toBe(1)
      expect(store.filteredVideos[0].id).toBe('2')
    })

    it('trie par date', () => {
      store.updateSort('date')
      expect(store.filteredVideos[0].id).toBe('1')
      expect(store.filteredVideos[1].id).toBe('2')
      expect(store.filteredVideos[2].id).toBe('3')
    })

    it('trie par vues', () => {
      store.updateSort('views')
      expect(store.filteredVideos[0].id).toBe('2')
      expect(store.filteredVideos[1].id).toBe('1')
      expect(store.filteredVideos[2].id).toBe('3')
    })
  })

  describe('searchVideosByGame', () => {
    it('recherche des vidéos par jeu', async () => {
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
              duration: '1h30m',
              view_count: 500,
              language: 'fr'
            }
          ]
        }
      }

      vi.spyOn(axios, 'get').mockResolvedValueOnce(mockResponse)

      await store.searchVideosByGame('Minecraft')
      
      expect(store.videos.length).toBe(1)
      expect(store.allVideos.length).toBe(1)
      expect(store.videos[0].title).toBe('Test Video')
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.currentGame).toBe('Minecraft')
      expect(store.currentSearch).toBe('Minecraft')
      expect(store.hasMore).toBe(false)
    })

    it('gère les erreurs de recherche', async () => {
      const store = useVideoStore()
      
      vi.spyOn(axios, 'get').mockRejectedValueOnce(new Error('Network Error'))

      await store.searchVideosByGame('Minecraft')
      
      expect(store.videos).toEqual([])
      expect(store.allVideos).toEqual([])
      expect(store.visibleVideos).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBe('Une erreur est survenue lors de la recherche des vidéos')
    })
  })
}) 