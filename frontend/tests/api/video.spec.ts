import { describe, it, expect, beforeEach } from 'vitest'
import { videoApi } from '@/api/config'
import { mockAxios } from '../setup'

describe('Video API', () => {
  beforeEach(() => {
    mockAxios.reset()
  })

  describe('GET /api/search', () => {
    const mockResponse = {
      videos: [
        {
          id: '1',
          title: 'Test Video 1',
          thumbnail_url: 'http://example.com/thumb1.jpg',
          duration: '1h30m',
          view_count: 1000,
          language: 'fr',
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          title: 'Test Video 2',
          thumbnail_url: 'http://example.com/thumb2.jpg',
          duration: '45m',
          view_count: 500,
          language: 'en',
          created_at: new Date().toISOString()
        }
      ]
    }

    it('returns videos successfully', async () => {
      mockAxios.onGet('/api/search').reply(200, mockResponse)

      const response = await videoApi.get('/api/search', {
        params: {
          game: 'Minecraft',
          limit: 10,
          page: 1
        }
      })

      expect(response.status).toBe(200)
      expect(response.data).toEqual(mockResponse)
    })

    it('handles search parameters correctly', async () => {
      mockAxios.onGet('/api/search').reply((config) => {
        expect(config.params).toEqual({
          game: 'Minecraft',
          limit: 10,
          page: 1,
          use_cache: true
        })
        return [200, mockResponse]
      })

      await videoApi.get('/api/search', {
        params: {
          game: 'Minecraft',
          limit: 10,
          page: 1,
          use_cache: true
        }
      })
    })

    it('handles errors correctly', async () => {
      mockAxios.onGet('/api/search').reply(500, {
        detail: 'Internal server error'
      })

      try {
        await videoApi.get('/api/search', {
          params: {
            game: 'Minecraft'
          }
        })
        // Si on arrive ici, le test doit échouer
        expect(true).toBe(false)
      } catch (error) {
        expect(error.response.status).toBe(500)
        expect(error.response.data.detail).toBe('Internal server error')
      }
    })

    it('handles network errors', async () => {
      mockAxios.onGet('/api/search').networkError()

      try {
        await videoApi.get('/api/search')
        // Si on arrive ici, le test doit échouer
        expect(true).toBe(false)
      } catch (error) {
        expect(error.message).toContain('Network Error')
      }
    })

    it('handles timeout', async () => {
      mockAxios.onGet('/api/search').timeout()

      try {
        await videoApi.get('/api/search')
        // Si on arrive ici, le test doit échouer
        expect(true).toBe(false)
      } catch (error) {
        expect(error.message).toContain('timeout')
      }
    })
  })
}) 