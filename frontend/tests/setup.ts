import '@testing-library/jest-dom'
import { config } from '@vue/test-utils'
import { vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

// Mock des variables d'environnement
process.env.VITE_API_URL = 'http://localhost:8000'

// Configuration globale de Vue Test Utils
config.global.mocks = {
  $route: {
    params: {},
    query: {}
  },
  $router: {
    push: vi.fn(),
    replace: vi.fn()
  }
}

// Mock d'IntersectionObserver pour les tests
class MockIntersectionObserver {
  observe() {
    return null
  }

  unobserve() {
    return null
  }

  disconnect() {
    return null
  }
}

global.IntersectionObserver = MockIntersectionObserver as any

// Mock de import.meta.env
vi.mock('import.meta.env', () => ({
  VITE_API_URL: 'http://localhost:8000'
}))

// Initialisation de Pinia
const pinia = createPinia()
setActivePinia(pinia)

// Configuration globale de Vue Test Utils avec Pinia
config.global.plugins = [pinia] 