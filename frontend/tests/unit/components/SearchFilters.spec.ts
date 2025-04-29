import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import SearchFilters from '../../../src/components/SearchFilters.vue'
import { useVideoStore } from '../../../src/stores/video'

describe('SearchFilters', () => {
  let store

  beforeEach(() => {
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      stubActions: false,
      initialState: {
        video: {
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
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })
    return { wrapper }
  }

  it('renders all filter sections', () => {
    const { wrapper } = createWrapper()
    expect(wrapper.find('[data-test="date-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="duration-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="views-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="language-filter"]').exists()).toBe(true)
  })

  it('updates store when date filter changes', async () => {
    const { wrapper } = createWrapper()
    const dateSelect = wrapper.find('[data-test="date-filter"]')
    await dateSelect.setValue('today')
    expect(store.filters.date).toBe('today')
  })

  it('updates store when duration filter changes', async () => {
    const { wrapper } = createWrapper()
    const durationSelect = wrapper.find('[data-test="duration-filter"]')
    await durationSelect.setValue('short')
    expect(store.filters.duration).toBe('short')
  })

  it('updates store when views filter changes', async () => {
    const { wrapper } = createWrapper()
    const viewsSelect = wrapper.find('[data-test="views-filter"]')
    await viewsSelect.setValue('more_1000')
    expect(store.filters.views).toBe('more_1000')
  })

  it('updates store when language filter changes', async () => {
    const { wrapper } = createWrapper()
    const languageSelect = wrapper.find('[data-test="language-filter"]')
    await languageSelect.setValue('fr')
    expect(store.filters.language).toBe('fr')
  })

  it('updates sort when clicking sort buttons', async () => {
    const { wrapper } = createWrapper()
    const sortButton = wrapper.find('[data-test="sort-button"]')
    await sortButton.trigger('click')
    expect(store.sortBy).toBe('date')
  })

  it('highlights active sort button', async () => {
    const { wrapper } = createWrapper()
    const sortButton = wrapper.find('[data-test="sort-button"]')
    await sortButton.trigger('click')
    expect(sortButton.classes()).toContain('active')
  })

  it('resets filters when changing game', async () => {
    const { wrapper } = createWrapper()
    
    // Modifier les filtres
    store.$patch({
      filters: {
        date: 'today',
        duration: 'short',
        views: 'more_1000',
        language: 'fr'
      }
    })

    // Émettre l'événement de changement de jeu
    await wrapper.vm.$emit('game-change')

    // Vérifier que les filtres sont réinitialisés
    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
  })
}) 