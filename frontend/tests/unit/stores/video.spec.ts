import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

// 1) On mock d'abord axios
vi.mock('axios', () => {
  const mockGet = vi.fn()
  const mockCreate = vi.fn(() => ({
    get: mockGet
  }))

  return {
    default: {
      create: mockCreate
    }
  }
})

// 2) Puis on importe le reste
import { setActivePinia, createPinia } from 'pinia'
import { useVideoStore } from '@/stores/video'

describe('Video Store', () => {
  let mockGet: ReturnType<typeof vi.fn>

  beforeEach(() => {
    setActivePinia(createPinia())

    // 3) On configure le mockGet pour retourner la bonne structure
    mockGet = vi.fn()
    ;(axios.create as any).mockReturnValue({
      get: mockGet
    })
  })

  it('initializes with default values', () => {
    const store = useVideoStore()
    expect(store.allVideos).toEqual([])
    expect(store.visibleVideos).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
    expect(store.hasMore).toBe(true)
    expect(store.currentGame).toBe('')
    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
  })

  it('updates filters', () => {
    const store = useVideoStore()
    store.updateFilters({
      date: 'today',
      duration: 'short',
      views: 'more_1000',
      language: 'fr'
    })
    expect(store.filters).toEqual({
      date: 'today',
      duration: 'short',
      views: 'more_1000',
      language: 'fr'
    })
  })

  it('updates sort', () => {
    const store = useVideoStore()
    store.updateSort('views')
    expect(store.sortBy).toBe('views')
  })

  it('resets store state', () => {
    const store = useVideoStore()
    store.updateFilters({
      date: 'today',
      duration: 'short',
      views: 'more_1000',
      language: 'fr'
    })
    store.$reset()
    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
  })

  describe('filteredVideos getter', () => {
    it('should filter videos by date', async () => {
      const store = useVideoStore()
      const now = '2024-01-01T12:00:00Z'
      const yesterday = '2023-12-31T12:00:00Z'
      const lastWeek = '2023-12-25T12:00:00Z'
      
      store.$patch({
        allVideos: [
          { 
            id: '1', 
            user_name: 'test1', 
            title: 'test1', 
            url: 'test1', 
            view_count: 100, 
            duration: '1h', 
            created_at: now,
            language: 'fr',
            thumbnail_url: 'https://example.com/thumb1.jpg',
            description: 'Test video 1',
            streamer_name: 'test1',
            game_id: '1',
            game_name: 'test'
          },
          { 
            id: '2', 
            user_name: 'test2', 
            title: 'test2', 
            url: 'test2', 
            view_count: 200, 
            duration: '2h', 
            created_at: yesterday,
            language: 'en',
            thumbnail_url: 'https://example.com/thumb2.jpg',
            description: 'Test video 2',
            streamer_name: 'test2',
            game_id: '1',
            game_name: 'test'
          },
          { 
            id: '3', 
            user_name: 'test3', 
            title: 'test3', 
            url: 'test3', 
            view_count: 300, 
            duration: '30m', 
            created_at: lastWeek,
            language: 'fr',
            thumbnail_url: 'https://example.com/thumb3.jpg',
            description: 'Test video 3',
            streamer_name: 'test3',
            game_id: '1',
            game_name: 'test'
          }
        ],
        filters: {
          date: 'today',
          duration: 'all',
          views: 'all',
          language: 'all'
        }
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by duration', async () => {
      const store = useVideoStore()
      store.$patch({
        allVideos: [
          { id: '1', user_name: 'test1', title: 'test1', url: 'test1', created_at: new Date().toISOString(), view_count: 100, duration: '10m', language: 'fr' },
          { id: '2', user_name: 'test2', title: 'test2', url: 'test2', created_at: new Date().toISOString(), view_count: 200, duration: '30m', language: 'en' },
          { id: '3', user_name: 'test3', title: 'test3', url: 'test3', created_at: new Date().toISOString(), view_count: 300, duration: '2h', language: 'fr' }
        ],
        filters: {
          date: 'all',
          duration: 'short',
          views: 'all',
          language: 'all'
        }
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by views', async () => {
      const store = useVideoStore()
      store.$patch({
        allVideos: [
          { id: '1', user_name: 'test1', title: 'test1', url: 'test1', created_at: new Date().toISOString(), view_count: 50, duration: '1h', language: 'fr' },
          { id: '2', user_name: 'test2', title: 'test2', url: 'test2', created_at: new Date().toISOString(), view_count: 500, duration: '2h', language: 'en' },
          { id: '3', user_name: 'test3', title: 'test3', url: 'test3', created_at: new Date().toISOString(), view_count: 1500, duration: '30m', language: 'fr' }
        ],
        filters: {
          date: 'all',
          duration: 'all',
          views: 'less_100',
          language: 'all'
        }
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by language', async () => {
      const store = useVideoStore()
      store.$patch({
        allVideos: [
          { id: '1', user_name: 'test1', title: 'test1', url: 'test1', created_at: new Date().toISOString(), view_count: 100, duration: '1h', language: 'fr' },
          { id: '2', user_name: 'test2', title: 'test2', url: 'test2', created_at: new Date().toISOString(), view_count: 200, duration: '2h', language: 'en' },
          { id: '3', user_name: 'test3', title: 'test3', url: 'test3', created_at: new Date().toISOString(), view_count: 300, duration: '30m', language: 'fr' }
        ],
        filters: {
          date: 'all',
          duration: 'all',
          views: 'all',
          language: 'fr'
        }
      })

      const filtered = store.filteredVideos
      expect(filtered.length).toBe(2)
      // expect(filtered.map(v => v.id)).toEqual(['1', '3'])
    })
  })

  describe('actions', () => {
    it('should handle search videos by game', async () => {
      const mockResponse = {
        game_name: 'test',
        game: {
          id: '1',
          name: 'test',
          box_art_url: 'https://example.com/box.jpg'
        },
        videos: [
          { 
            id: '1', 
            user_name: 'test1', 
            title: 'test1', 
            url: 'test1', 
            view_count: 100, 
            duration: '1h', 
            created_at: '2024-01-01T12:00:00Z',
            language: 'fr',
            thumbnail_url: 'https://example.com/thumb1.jpg',
            description: 'Test video 1',
            streamer_name: 'test1',
            game_id: '1',
            game_name: 'test'
          },
          { 
            id: '2', 
            user_name: 'test2', 
            title: 'test2', 
            url: 'test2', 
            view_count: 200, 
            duration: '2h', 
            created_at: '2024-01-01T11:00:00Z',
            language: 'en',
            thumbnail_url: 'https://example.com/thumb2.jpg',
            description: 'Test video 2',
            streamer_name: 'test2',
            game_id: '1',
            game_name: 'test'
          }
        ],
        total_count: 2,
        last_updated: '2024-01-01T12:00:00Z'
      }

      mockGet.mockResolvedValueOnce({ data: mockResponse })

      const store = useVideoStore()
      await store.searchVideosByGame('test')

      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.allVideos.length).toBe(2)
      expect(store.visibleVideos.length).toBe(2)
    })

    it('should handle search error', async () => {
      mockGet.mockRejectedValueOnce(new Error('API Error'))

      const store = useVideoStore()
      await store.searchVideosByGame('test')

      expect(store.loading).toBe(false)
      expect(store.error).toBeTruthy()
      expect(store.allVideos.length).toBe(0)
      expect(store.visibleVideos.length).toBe(0)
    })
  })
}) 