import axios from 'axios'
import type { SearchResponse } from '@/types/video'

interface SearchOptions {
  limit?: number
  use_cache?: boolean
  cursor?: string | null
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
})

export const searchVideosByGame = async (game_name: string, options: SearchOptions = {}): Promise<{ data: SearchResponse }> => {
  console.log('Searching videos for game:', game_name, 'with options:', options)
  
  try {
    const { limit = 100, use_cache = true, cursor = null } = options
    const encodedGameName = encodeURIComponent(game_name)
    
    const params: Record<string, any> = {
      game: encodedGameName,
      limit,
      use_cache
    }

    if (cursor) {
      params.after = cursor
    }
    
    const response = await api.get<SearchResponse>('/api/search/', { params })

    console.log('API Response:', response.data)
    return response
  } catch (error) {
    console.error('Error while searching videos:', error)
    if (axios.isAxiosError(error) && error.response) {
      console.error('Error details:', error.response.data)
    }
    throw error
  }
} 