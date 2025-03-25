import { defineStore } from 'pinia'
import api from '../config/api'

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

interface Game {
  id: string
  name: string
  box_art_url: string
}

interface SearchResponse {
  game_name: string
  game: Game
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
        console.log(`Recherche des vidéos pour le jeu: ${game}`)
        const response = await api.get<SearchResponse>(`/api/search`, {
          params: {
            game_name: game,
            limit: 10,
            use_cache: true
          }
        })
        console.log('Réponse reçue:', response.data)
        this.videos = response.data.videos
        this.currentGame = game
        return response.data
      } catch (error) {
        console.error('Erreur lors de la recherche:', error)
        this.error = "Erreur lors de la recherche des vidéos"
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 