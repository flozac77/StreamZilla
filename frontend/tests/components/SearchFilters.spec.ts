import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import SearchFilters from '../../src/components/SearchFilters.vue'
import { useVideoStore } from '../../src/stores/video'

describe('SearchFilters', () => {
  let wrapper
  let store

  beforeEach(() => {
    const pinia = createTestingPinia({
      initialState: {
        video: {
          filters: {
            date: 'all',
            duration: 'all',
            views: 'all',
            language: 'all'
          },
          sortBy: 'date'
        }
      },
      stubActions: false
    })
    
    store = useVideoStore(pinia)
    wrapper = mount(SearchFilters, {
      global: {
        plugins: [pinia]
      }
    })
  })

  it('displays all filter sections', () => {
    expect(wrapper.find('[data-test="date-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="duration-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="views-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="language-filter"]').exists()).toBe(true)
  })

  it('updates date filter', async () => {
    const select = wrapper.find('[data-test="date-filter"]')
    await select.setValue('this_week')
    expect(store.filters.date).toBe('this_week')
  })

  it('updates duration filter', async () => {
    const select = wrapper.find('[data-test="duration-filter"]')
    await select.setValue('short')
    expect(store.filters.duration).toBe('short')
  })

  it('updates views filter', async () => {
    const select = wrapper.find('[data-test="views-filter"]')
    await select.setValue('less_100')
    expect(store.filters.views).toBe('less_100')
  })

  it('updates language filter', async () => {
    const select = wrapper.find('[data-test="language-filter"]')
    await select.setValue('fr')
    expect(store.filters.language).toBe('fr')
  })

  it('updates sorting', async () => {
    const buttons = wrapper.findAll('[data-test="sort-button"]')
    const dateButton = buttons[0]
    const viewsButton = buttons[1]
    const durationButton = buttons[2]

    await viewsButton.trigger('click')
    expect(store.sortBy).toBe('views')
    expect(viewsButton.classes()).toContain('bg-purple-600')
    expect(dateButton.classes()).toContain('bg-gray-700')

    await durationButton.trigger('click')
    expect(store.sortBy).toBe('duration')
    expect(durationButton.classes()).toContain('bg-purple-600')
    expect(viewsButton.classes()).toContain('bg-gray-700')

    await dateButton.trigger('click')
    expect(store.sortBy).toBe('date')
    expect(dateButton.classes()).toContain('bg-purple-600')
    expect(durationButton.classes()).toContain('bg-gray-700')
  })

  it('resets filters on game change', async () => {
    store.updateFilters({
      date: 'this_week',
      duration: 'short',
      views: 'less_100',
      language: 'fr'
    })
    store.updateSort('views')

    await wrapper.vm.$emit('game-change')

    expect(store.filters).toEqual({
      date: 'all',
      duration: 'all',
      views: 'all',
      language: 'all'
    })
    expect(store.sortBy).toBe('date')
  })
}) 