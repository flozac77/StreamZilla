import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import VideoListView from '@/views/VideoListView.vue'
import { useVideoStore } from '@/stores/video'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { useRoute } from 'vue-router'
import { useIntersectionObserver } from '@vueuse/core'

// Mock @vueuse/core
vi.mock('@vueuse/core', () => ({
  useIntersectionObserver: vi.fn((target, callback) => {
    return {
      stop: vi.fn(),
      isSupported: true
    }
  })
}))

// Mock des composants enfants
vi.mock('@/components/SearchFilters.vue', () => ({
  default: {
    name: 'SearchFilters',
    template: '<div class="search-filters"></div>'
  }
}))

vi.mock('@/components/UserPreferences.vue', () => ({
  default: {
    name: 'UserPreferences',
    template: '<div class="user-preferences"></div>'
  }
}))

vi.mock('@/components/LoadingSpinner.vue', () => ({
  default: {
    name: 'LoadingSpinner',
    template: '<div class="loading-spinner"></div>'
  }
}))

// Mock vue-router
vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => ({
    params: { game: 'Minecraft' }
  }))
}))

// Mock vue-toastification
vi.mock('vue-toastification', () => ({
  useToast: vi.fn(() => ({
    success: vi.fn(),
    error: vi.fn()
  }))
}))

describe('VideoListView', () => {
  const mockVideos = [
    {
      id: '1',
      title: 'Video 1',
      created_at: '2024-01-01T10:00:00Z',
      duration: '30m',
      view_count: 500,
      language: 'fr',
      user_name: 'user1',
      url: 'url1',
      thumbnail_url: 'thumb1',
      description: 'desc1',
      streamer_name: 'streamer1',
      game_id: 'game1',
      game_name: 'Game 1'
    },
    {
      id: '2',
      title: 'Video 2',
      created_at: '2023-12-01T10:00:00Z',
      duration: '2h',
      view_count: 1500,
      language: 'en',
      user_name: 'user2',
      url: 'url2',
      thumbnail_url: 'thumb2',
      description: 'desc2',
      streamer_name: 'streamer2',
      game_id: 'game2',
      game_name: 'Game 2'
    }
  ]

  beforeEach(() => {
    setActivePinia(createPinia())
    
    // Mock du store video
    const videoStore = useVideoStore()
    videoStore.searchVideosByGame = vi.fn().mockResolvedValue({
      videos: mockVideos,
      total_count: 2,
      game_name: 'Minecraft',
      game: null,
      last_updated: '2024-01-01T12:00:00Z'
    })
    videoStore.updateFilters = vi.fn()
    videoStore.updateSort = vi.fn()
    videoStore.loadMore = vi.fn()
    
    // Mock du store userPreferences
    const userPreferencesStore = useUserPreferencesStore()
    userPreferencesStore.addToHistory = vi.fn()
  })

  it('appelle searchVideosByGame au montage avec le bon paramètre', async () => {
    const wrapper = mount(VideoListView)
    await wrapper.vm.$nextTick()
    
    const store = useVideoStore()
    expect(store.searchVideosByGame).toHaveBeenCalledWith('Minecraft')
  })

  it('affiche le loader pendant le chargement', () => {
    const store = useVideoStore()
    store.$patch({ loading: true })
    
    const wrapper = mount(VideoListView)
    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
  })

  it('affiche un message d\'erreur si une erreur survient', async () => {
    const store = useVideoStore()
    store.$patch({ error: 'Une erreur est survenue' })
    
    const wrapper = mount(VideoListView)
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Une erreur est survenue')
  })

  it('affiche la grille de vidéos quand les données sont chargées', async () => {
    const store = useVideoStore()
    store.$patch({ 
      allVideos: mockVideos,
      visibleVideos: mockVideos,
      loading: false 
    })
    
    const wrapper = mount(VideoListView)
    await wrapper.vm.$nextTick()
    const videoCards = wrapper.findAll('.video-card')
    expect(videoCards).toHaveLength(mockVideos.length)
  })

  it('met à jour l\'historique quand une recherche est effectuée', async () => {
    const wrapper = mount(VideoListView)
    await wrapper.vm.$nextTick()
    
    const userPreferencesStore = useUserPreferencesStore()
    expect(userPreferencesStore.addToHistory).toHaveBeenCalledWith('Minecraft')
  })

  it('gère correctement le rechargement automatique', async () => {
    vi.useFakeTimers()
    
    const wrapper = mount(VideoListView)
    const store = useVideoStore()
    
    // Avance le temps de 2 minutes
    await vi.advanceTimersByTimeAsync(120000)
    expect(store.searchVideosByGame).toHaveBeenCalledTimes(2) // Une fois au montage, une fois après 2 minutes
    
    vi.useRealTimers()
  })

  it('gère correctement le scroll infini', async () => {
    const store = useVideoStore()
    store.$patch({ 
      hasMore: true,
      loading: false,
      loadingMore: false
    })
    
    const wrapper = mount(VideoListView)
    await wrapper.vm.$nextTick()
    
    // Simule l'intersection observer
    const callback = (useIntersectionObserver as jest.Mock).mock.calls[0][1]
    callback([{ isIntersecting: true }])
    
    expect(store.loadMore).toHaveBeenCalled()
  })

  it('applique correctement les filtres', async () => {
    const wrapper = mount(VideoListView)
    const store = useVideoStore()
    
    await wrapper.vm.fetchVideos()
    await wrapper.vm.updateFilters({
      date: 'today',
      duration: 'short',
      views: 'more_1000',
      language: 'fr'
    })
    
    expect(store.updateFilters).toHaveBeenCalled()
  })

  it('applique correctement le tri', async () => {
    const wrapper = mount(VideoListView)
    const store = useVideoStore()
    
    await wrapper.vm.fetchVideos()
    await wrapper.vm.updateSort('views')
    expect(store.updateSort).toHaveBeenCalledWith('views')
  })
}) 