import axios from 'axios'
import type { SearchResponse } from '@/types/video'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
})

export async function searchVideosByGame(game_name: string) {
  console.log('Searching videos for game:', game_name)
  
  try {
    // Encode game name to handle special characters
    const encodedGameName = encodeURIComponent(game_name)
    console.log('Encoded game name:', encodedGameName)

    const response = await api.get<SearchResponse>('/api/search/', {
      params: {
        game: encodedGameName,
        limit: 24,
        page: 1,
        use_cache: true
      }
    })

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