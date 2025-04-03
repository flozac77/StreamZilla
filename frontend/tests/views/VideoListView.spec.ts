import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import VideoListView from '@/views/VideoListView.vue'
import { useVideoStore } from '@/stores/videoStore'
import { useUserPreferencesStore } from '@/stores/userPreferencesStore'
import { mockAxios } from '../setup'

// Mock des composants enfants
vi.mock('@/components/SearchFilters.vue', () => ({
  default: {
    name: 'SearchFilters',
    template: '<div class="mock-search-filters"></div>'
  }
}))

vi.mock('@/components/UserPreferences.vue', () => ({
  default: {
    name: 'UserPreferences',
    template: '<div class="mock-user-preferences"></div>'
  }
}))

vi.mock('@/components/LoadingSpinner.vue', () => ({
  default: {
    name: 'LoadingSpinner',
    template: '<div class="mock-loading-spinner"></div>'
  }
}))

describe('VideoListView', () => {
  const mockVideos = [
    {
      id: '1',
      title: 'Video 1',
      thumbnail_url: 'url1',
      duration: '1h30m',
      view_count: 1000,
      language: 'fr',
      created_at: new Date().toISOString()
    },
    {
      id: '2',
      title: 'Video 2',
      thumbnail_url: 'url2',
      duration: '45m',
      view_count: 500,
      language: 'en',
      created_at: new Date().toISOString()
    }
  ]

  beforeEach(() => {
    // Mock de la réponse API
    mockAxios.onGet('/api/search').reply(200, { videos: mockVideos })
    
    // Reset des timers
    vi.useFakeTimers()
  })

  afterEach(() => {
    mockAxios.reset()
    vi.clearAllMocks()
    vi.useRealTimers()
  })

  it('appelle searchVideosByGame au montage avec le bon paramètre', async () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          stubActions: false
        })]
      },
      props: {
        game: 'Minecraft'
      }
    })

    const store = useVideoStore()
    expect(store.searchVideosByGame).toHaveBeenCalledWith('Minecraft')
  })

  it('affiche le loader pendant le chargement', () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            video: { loading: true }
          }
        })]
      }
    })

    expect(wrapper.find('.mock-loading-spinner').exists()).toBe(true)
  })

  it('affiche un message d\'erreur si une erreur survient', async () => {
    const errorMessage = 'Une erreur est survenue'
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            video: { error: errorMessage }
          }
        })]
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain(errorMessage)
  })

  it('affiche la grille de vidéos quand les données sont chargées', async () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            video: { videos: mockVideos }
          }
        })]
      }
    })

    await wrapper.vm.$nextTick()
    const videoCards = wrapper.findAll('.grid > div')
    expect(videoCards).toHaveLength(mockVideos.length)
  })

  it('met à jour l\'historique quand une recherche est effectuée', async () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })]
      },
      props: {
        game: 'Minecraft'
      }
    })

    const userPreferencesStore = useUserPreferencesStore()
    expect(userPreferencesStore.addToHistory).toHaveBeenCalledWith('Minecraft')
  })

  it('gère correctement le rechargement automatique', async () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })]
      },
      props: {
        game: 'Minecraft'
      }
    })

    const store = useVideoStore()

    // Avance le temps de 2 minutes
    await vi.advanceTimersByTimeAsync(120000)
    expect(store.searchVideosByGame).toHaveBeenCalledTimes(2) // Une fois au montage, une fois après 2 minutes

    vi.useRealTimers()
  })

  it('gère correctement le scroll infini', async () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            video: {
              hasMore: true,
              loading: false,
              loadingMore: false
            }
          }
        })]
      }
    })

    const store = useVideoStore()

    const loadMoreTrigger = wrapper.find('[ref="loadMoreTrigger"]')
    expect(loadMoreTrigger.exists()).toBe(true)

    // Simule le scroll
    await wrapper.vm.onIntersect([{ isIntersecting: true }])
    expect(store.loadMore).toHaveBeenCalled()
  })

  it('applique correctement les filtres', async () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })]
      }
    })

    const store = useVideoStore()
    
    await wrapper.vm.updateFilters({
      type: 'date',
      value: 'today'
    })

    expect(store.updateFilters).toHaveBeenCalled()
  })

  it('applique correctement le tri', async () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn
        })]
      }
    })

    const store = useVideoStore()

    await wrapper.vm.updateSort('views')
    expect(store.updateSort).toHaveBeenCalledWith('views')
  })
}) 