import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import VideoListView from '@/views/VideoListView.vue'
import { useVideoStore } from '@/stores/videoStore'
import { useUserPreferencesStore } from '@/stores/userPreferencesStore'
import { useToast } from 'vue-toastification'

// Mock des composants
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

vi.mock('vue-toastification', () => ({
  useToast: vi.fn(() => ({
    error: vi.fn(),
    success: vi.fn()
  }))
}))

const mockVideos = [
  {
    id: '1',
    title: 'Video 1',
    created_at: new Date().toISOString(),
    duration: '00:05:00',
    view_count: 500,
    language: 'fr',
    user_name: 'user1',
    url: 'url1',
    thumbnail_url: 'thumb1'
  },
  {
    id: '2',
    title: 'Video 2',
    created_at: '2023-01-01T00:00:00Z',
    duration: '02:00:00',
    view_count: 1500,
    language: 'en',
    user_name: 'user2',
    url: 'url2',
    thumbnail_url: 'thumb2'
  }
]

describe('VideoListView', () => {
  let wrapper
  let videoStore
  let userPreferencesStore
  let toast

  beforeEach(() => {
    const pinia = createTestingPinia({
      initialState: {
        video: {
          videos: [],
          visibleVideos: [],
          allVideos: [],
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
        },
        userPreferences: {
          autoReload: false,
          reloadInterval: 60,
          favorites: [],
          history: []
        }
      },
      stubActions: false
    })

    videoStore = useVideoStore(pinia)
    userPreferencesStore = useUserPreferencesStore(pinia)
    toast = useToast()

    wrapper = mount(VideoListView, {
      global: {
        plugins: [pinia],
        mocks: {
          $route: {
            params: {
              game: 'Minecraft'
            }
          },
          $router: {
            push: vi.fn()
          }
        }
      }
    })
  })

  it('charge les vidéos au montage', async () => {
    const searchSpy = vi.spyOn(videoStore, 'searchVideosByGame')
    await wrapper.vm.$nextTick()
    expect(searchSpy).toHaveBeenCalledWith('Minecraft')
  })

  it('affiche un indicateur de chargement', async () => {
    videoStore.loading = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })

  it('affiche un message d\'erreur', async () => {
    videoStore.error = 'Une erreur est survenue'
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.text-red-500').text()).toBe('Une erreur est survenue')
  })

  it('affiche la grille de vidéos', async () => {
    videoStore.visibleVideos = mockVideos
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.grid').exists()).toBe(true)
    expect(wrapper.findAll('.grid > div')).toHaveLength(2)
  })

  it('met à jour l\'historique lors d\'une recherche', async () => {
    const addToHistorySpy = vi.spyOn(userPreferencesStore, 'addToHistory')
    await wrapper.vm.fetchVideos()
    expect(addToHistorySpy).toHaveBeenCalledWith('Minecraft')
  })

  it('gère le rechargement automatique', async () => {
    const fetchSpy = vi.spyOn(wrapper.vm, 'fetchVideos')
    vi.useFakeTimers()
    
    wrapper.vm.startAutoRefresh()
    vi.advanceTimersByTime(120000)
    expect(fetchSpy).toHaveBeenCalledTimes(1)
    
    vi.advanceTimersByTime(120000)
    expect(fetchSpy).toHaveBeenCalledTimes(2)
    
    vi.useRealTimers()
  })

  it('gère le scroll infini', async () => {
    const loadMoreSpy = vi.spyOn(videoStore, 'loadMore')
    const observer = wrapper.vm.setupIntersectionObserver()
    
    // Simuler l'intersection
    observer.value?.([{ isIntersecting: true }])
    
    expect(loadMoreSpy).toHaveBeenCalled()
  })

  it('applique les filtres', async () => {
    videoStore.visibleVideos = mockVideos
    await wrapper.vm.updateFilters({
      date: 'today',
      duration: 'short',
      views: 'less_100'
    })
    expect(videoStore.filters.date).toBe('today')
    expect(videoStore.filters.duration).toBe('short')
    expect(videoStore.filters.views).toBe('less_100')
  })

  it('applique le tri', async () => {
    videoStore.visibleVideos = mockVideos
    await wrapper.vm.updateSort('views')
    expect(videoStore.sortBy).toBe('views')
  })
}) 