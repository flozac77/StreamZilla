import { useVideoStore } from '../../../src/stores/video'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Video } from '../../../src/types/video'
import { createTestingPinia } from '@pinia/testing'

describe('Video Store', () => {
  let store
  // let pinia // Removed unused variable

  beforeEach(() => {
    createTestingPinia({ // Call createTestingPinia for its side effects (e.g., setting up active pinia)
      createSpy: vi.fn,
      stubActions: false
    })
    store = useVideoStore()
  })

  it('initializes with default values', () => {
    expect(store.videos).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
    expect(store.sortBy).toBe('date')
  })

  it('updates filters', () => {
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
    store.updateSort('views')
    expect(store.sortBy).toBe('views')
  })

  it('resets store state', () => {
    store.resetSearch()
    expect(store.videos).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
    expect(store.sortBy).toBe('date')
  })

  describe('filteredVideos getter', () => {
    let store: ReturnType<typeof useVideoStore>
    const mockVideos: Video[] = [
      {
        id: '1',
        title: 'Video 1',
        created_at: new Date().toISOString(),
        duration: '30m',
        view_count: 500,
        language: 'fr',
        user_name: 'user1',
        url: 'url1',
        thumbnail_url: 'thumb1',
        description: 'desc1',
        streamer_name: 'streamer1',
        game_id: 'game1',
        game_name: 'Game 1'
      },
      {
        id: '2',
        title: 'Video 2',
        created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days ago
        duration: '2h',
        view_count: 1500,
        language: 'en',
        user_name: 'user2',
        url: 'url2',
        thumbnail_url: 'thumb2',
        description: 'desc2',
        streamer_name: 'streamer2',
        game_id: 'game2',
        game_name: 'Game 2'
      }
    ]

    beforeEach(() => {
      store = useVideoStore()
      store.videos = mockVideos
    })

    it('should filter videos by date', () => {
      store.updateFilters({ date: 'today' })
      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by duration', () => {
      store.updateFilters({ duration: 'short' })
      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter videos by views', () => {
      store.updateFilters({ views: 'more_1000' })
      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('2')
    })

    it('should filter videos by language', () => {
      store.updateFilters({ language: 'fr' })
      const filtered = store.filteredVideos
      expect(filtered.length).toBe(1)
      expect(filtered[0].id).toBe('1')
    })
  })

  describe('actions', () => {
    let store: ReturnType<typeof useVideoStore>
    const mockApiResponse = {
      data: {
        game_name: 'Minecraft',
        game: {
          id: 'game1',
          name: 'Minecraft',
          box_art_url: 'url'
        },
        videos: [
          {
            id: '1',
            title: 'Video 1',
            created_at: new Date().toISOString(),
            duration: '30m',
            view_count: 500,
            language: 'fr',
            user_name: 'user1',
            url: 'url1',
            thumbnail_url: 'thumb1',
            description: 'desc1',
            streamer_name: 'streamer1',
            game_id: 'game1',
            game_name: 'Game 1'
          },
          {
            id: '2',
            title: 'Video 2',
            created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
            duration: '2h',
            view_count: 1500,
            language: 'en',
            user_name: 'user2',
            url: 'url2',
            thumbnail_url: 'thumb2',
            description: 'desc2',
            streamer_name: 'streamer2',
            game_id: 'game2',
            game_name: 'Game 2'
          }
        ],
        total_count: 2,
        last_updated: new Date().toISOString()
      }
    }

    beforeEach(() => {
      vi.mock('@/api/video', () => ({
        searchVideosByGame: vi.fn().mockResolvedValue(mockApiResponse)
      }))
      store = useVideoStore()
    })

    it('should handle search videos by game', async () => {
      await store.searchVideosByGame('Minecraft')
      expect(store.loading).toBe(false)
      expect(store.error).toBe("An error has occurred")
      expect(store.videos.length).toBe(2)
      expect(store.currentGame).toBe('Minecraft')
    })

    it('should handle search error', async () => {
      vi.mock('@/api/video', () => ({
        searchVideosByGame: vi.fn().mockRejectedValue(new Error('Test error'))
      }))
      
      await store.searchVideosByGame('Minecraft')
      expect(store.loading).toBe(false)
      expect(store.error).toBe('Une erreur est survenue')
      expect(store.videos).toEqual([])
    })
  })
}) 