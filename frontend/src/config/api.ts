import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
})

// Intercepteur pour les requêtes
api.interceptors.request.use(
  (config) => {
    console.debug('🚀 Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Intercepteur pour les réponses
api.interceptors.response.use(
  (response) => {
    console.debug('✅ Response:', response.status, response.data)
    return response
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api 