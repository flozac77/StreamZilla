import { vi } from 'vitest'
import { config } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'

// Configuration globale de Vue Test Utils
config.global.mocks = {
  $t: (key: string) => key,
  $route: {
    params: {},
    query: {},
    path: '/'
  },
  $router: {
    push: vi.fn(),
    replace: vi.fn()
  }
}

// Configuration de Pinia pour les tests
const pinia = createTestingPinia({
  createSpy: vi.fn,
  stubActions: false,
  initialState: {
    video: {
      videos: [],
      allVideos: [],
      visibleVideos: [],
      loading: false,
      loadingMore: false,
      error: null,
      currentSearch: '',
      currentGame: '',
      page: 1,
      hasMore: true,
      filters: {
        date: 'all',
        duration: 'all',
        views: 'all',
        language: 'all'
      },
      sortBy: 'date'
    }
  }
})

config.global.plugins = [pinia]

// Configuration d'Axios Mock Adapter
const mockAxios = new MockAdapter(axios)

// Réinitialisation des mocks après chaque test
afterEach(() => {
  vi.clearAllMocks()
  mockAxios.reset()
})

// Export des utilitaires de test
export { mockAxios } 