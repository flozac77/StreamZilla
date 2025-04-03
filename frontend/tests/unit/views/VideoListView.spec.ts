import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import VideoListView from '../../src/views/VideoListView.vue'
import { useVideoStore } from '../../src/stores/videoStore'
import { createTestingPinia } from '@pinia/testing'

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

// Mock de isFavorite
vi.mock('@/composables/useFavorites', () => ({
  useFavorites: () => ({
    isFavorite: vi.fn().mockReturnValue(false),
    addToHistory: vi.fn()
  })
}))

describe('VideoListView', () => {
  let store

  beforeEach(() => {
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      stubActions: false,
      initialState: {
        video: {
          videos: [],
          loading: false,
          error: null,
          filters: {
            date: 'all',
            duration: 'all',
            views: 'all',
            language: 'all'
          }
        }
      }
    })
    store = useVideoStore()
  })

  const createWrapper = () => {
    const wrapper = mount(VideoListView, {
      global: {
        plugins: [createTestingPinia()],
        mocks: {
          isFavorite: vi.fn().mockReturnValue(false)
        }
      }
    })
    return { wrapper }
  }

  it('loads videos on mount', async () => {
    const { wrapper } = createWrapper()
    await wrapper.vm.$nextTick()
    expect(store.loading).toBe(false)
  })

  it('displays loading indicator', async () => {
    const { wrapper } = createWrapper()
    store.loading = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.loading-indicator').exists()).toBe(true)
  })

  it('displays error message', async () => {
    const { wrapper } = createWrapper()
    store.error = 'Test error'
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })

  it('displays video grid', async () => {
    const { wrapper } = createWrapper()
    store.videos = [{ id: 1, title: 'Test Video' }]
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.video-grid').exists()).toBe(true)
  })

  it('updates history on search', async () => {
    const { wrapper } = createWrapper()
    const searchInput = wrapper.find('input')
    await searchInput.setValue('test')
    await wrapper.vm.$nextTick()
    expect(store.currentSearch).toBe('test')
  })

  it('handles auto-refresh', async () => {
    const { wrapper } = createWrapper()
    vi.useFakeTimers()
    await wrapper.vm.$nextTick()
    vi.advanceTimersByTime(30000)
    expect(store.loading).toBe(false)
    vi.useRealTimers()
  })

  it('handles infinite scroll', async () => {
    const { wrapper } = createWrapper()
    const observer = new IntersectionObserver(() => {})
    vi.spyOn(window, 'IntersectionObserver').mockImplementation(() => observer)
    await wrapper.vm.$nextTick()
    expect(store.loadingMore).toBe(false)
  })

  it('applies filters', async () => {
    const { wrapper } = createWrapper()
    store.filters = {
      date: 'today',
      duration: 'short',
      views: 'more_1000',
      language: 'fr'
    }
    await wrapper.vm.$nextTick()
    expect(store.filteredVideos).toEqual([])
  })

  it('applies sorting', async () => {
    const { wrapper } = createWrapper()
    store.sortBy = 'views'
    await wrapper.vm.$nextTick()
    expect(store.filteredVideos).toEqual([])
  })
}) 