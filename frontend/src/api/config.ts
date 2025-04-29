import axios from 'axios'
import type { AxiosInstance } from 'axios'

// Configuration de base
const baseConfig = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
}

// Instance par défaut
const defaultApi = axios.create(baseConfig)

// Instance pour les vidéos
const videoApi = axios.create({
  ...baseConfig,
  // Configurations spécifiques aux vidéos si nécessaire
})

// Intercepteurs globaux pour la gestion des erreurs
const setupInterceptors = (instance: AxiosInstance) => {
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      // Log l'erreur en développement
      if (import.meta.env.DEV) {
        console.error('API Error:', error.response?.data || error.message)
      }
      return Promise.reject(error)
    }
  )
}

setupInterceptors(defaultApi)
setupInterceptors(videoApi)

export { defaultApi, videoApi } 