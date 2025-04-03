import axios from 'axios'
import type { SearchResponse } from '@/types/video'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
})

export async function searchVideosByGame(game_name: string) {
  console.log('Recherche de vidéos pour le jeu:', game_name)
  
  try {
    // Encode le nom du jeu pour éviter les problèmes avec les caractères spéciaux
    const encodedGameName = encodeURIComponent(game_name)
    console.log('Nom du jeu encodé:', encodedGameName)

    const response = await api.get<SearchResponse>('/api/search/', {
      params: {
        game: encodedGameName,
        limit: 24,
        page: 1,
        use_cache: true
      }
    })

    console.log('Réponse de l\'API:', response.data)
    return response
  } catch (error) {
    console.error('Erreur lors de la recherche de vidéos:', error)
    if (axios.isAxiosError(error) && error.response) {
      console.error('Détails de l\'erreur:', error.response.data)
    }
    throw error
  }
} 