import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import SearchFilters from '@/components/SearchFilters.vue'
import { useVideoStore } from '@/stores/videoStore'

describe('SearchFilters.vue', () => {
  it('renders all filter sections', () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    expect(wrapper.find('[data-test="date-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="duration-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="views-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="language-filter"]').exists()).toBe(true)
  })

  it('updates store when date filter changes', async () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const store = useVideoStore()
    await wrapper.find('[data-test="date-today"]').trigger('click')
    
    expect(store.updateFilters).toHaveBeenCalledWith({
      type: 'date',
      value: 'today'
    })
  })

  it('updates store when duration filter changes', async () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const store = useVideoStore()
    await wrapper.find('[data-test="duration-short"]').trigger('click')
    
    expect(store.updateFilters).toHaveBeenCalledWith({
      type: 'duration',
      value: 'short'
    })
  })

  it('updates store when views filter changes', async () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const store = useVideoStore()
    await wrapper.find('[data-test="views-more_1000"]').trigger('click')
    
    expect(store.updateFilters).toHaveBeenCalledWith({
      type: 'views',
      value: 'more_1000'
    })
  })

  it('updates store when language filter changes', async () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const store = useVideoStore()
    await wrapper.find('[data-test="language-fr"]').trigger('click')
    
    expect(store.updateFilters).toHaveBeenCalledWith({
      type: 'language',
      value: 'fr'
    })
  })

  it('updates sort when clicking sort buttons', async () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const store = useVideoStore()
    await wrapper.find('[data-test="sort-date"]').trigger('click')
    
    expect(store.updateSort).toHaveBeenCalledWith('date')
  })

  it('highlights active sort button', async () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia({
          initialState: {
            video: { sortBy: 'date' }
          }
        })]
      }
    })

    expect(wrapper.find('[data-test="sort-date"]').classes()).toContain('active')
  })

  it('resets filters when changing game', async () => {
    const wrapper = mount(SearchFilters, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const store = useVideoStore()
    await wrapper.vm.$emit('game-changed')
    
    expect(store.resetSearch).toHaveBeenCalled()
  })
}) 