import { defineStore } from 'pinia'
import axios from 'axios'

interface Video {
  id: string
  user_id: string
  user_name: string
  title: string
  description: string
  created_at: string
  published_at: string
  url: string
  thumbnail_url: string
  viewable: string
  view_count: number
  language: string
  type: string
  duration: string
}

interface SearchResponse {
  game_name: string
  game: {
    id: string
    name: string
    box_art_url: string
  }
  videos: Video[]
  last_updated: string
}

export const useVideoStore = defineStore('video', {
  state: () => ({
    videos: [] as Video[],
    currentGame: null as string | null,
    loading: false,
    error: null as string | null
  }),

  actions: {
    async searchVideosByGame(game: string): Promise<SearchResponse> {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get<SearchResponse>(`${import.meta.env.VITE_API_URL}/api/videos/${game}`)
        this.videos = response.data.videos
        this.currentGame = game
        return response.data
      } catch (error) {
        this.error = "Erreur lors de la recherche des vidéos"
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 